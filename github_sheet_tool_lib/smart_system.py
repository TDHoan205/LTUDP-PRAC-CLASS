from __future__ import annotations

import csv
import json
import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from github_sheet_tool_lib.core import (
    GithubClient,
    MAX_WORKERS,
    RequirementSpec,
    build_report,
    parse_required_files,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso_or_none(value: str) -> Optional[datetime]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


@dataclass
class ScanConfig:
    section: str
    bai_range: str = "1-5"
    assignment: str = "kiem tra bai tap theo de bai"
    similarity_threshold: float = 0.9
    deadline_iso: str = ""
    token: Optional[str] = None


class SmartStorage:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mssv TEXT,
                    full_name TEXT,
                    github_url TEXT,
                    class_name TEXT,
                    group_name TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT,
                    source_ref TEXT,
                    section TEXT,
                    bai_range TEXT,
                    assignment TEXT,
                    deadline_iso TEXT,
                    created_at TEXT,
                    report_json_path TEXT,
                    report_csv_path TEXT,
                    meta_json TEXT
                );

                CREATE TABLE IF NOT EXISTS scan_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    row_number INTEGER,
                    mssv TEXT,
                    full_name TEXT,
                    class_name TEXT,
                    group_name TEXT,
                    repo_url TEXT,
                    repo_full_name TEXT,
                    submitted_status TEXT,
                    deadline_status TEXT,
                    last_commit_at TEXT,
                    score_10 REAL,
                    repo_status TEXT,
                    plagiarism_high_risk INTEGER,
                    comments TEXT,
                    details_json TEXT,
                    FOREIGN KEY(scan_id) REFERENCES scans(id)
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

    # CRUD students
    def create_student(self, payload: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            ts = now_iso()
            cur = conn.execute(
                """
                INSERT INTO students (mssv, full_name, github_url, class_name, group_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.get("mssv", ""),
                    payload.get("full_name", ""),
                    payload.get("github_url", ""),
                    payload.get("class_name", ""),
                    payload.get("group_name", ""),
                    ts,
                    ts,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def list_students(self) -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_student(self, student_id: int, payload: Dict[str, Any]) -> bool:
        conn = self._connect()
        try:
            ts = now_iso()
            cur = conn.execute(
                """
                UPDATE students
                SET mssv=?, full_name=?, github_url=?, class_name=?, group_name=?, updated_at=?
                WHERE id=?
                """,
                (
                    payload.get("mssv", ""),
                    payload.get("full_name", ""),
                    payload.get("github_url", ""),
                    payload.get("class_name", ""),
                    payload.get("group_name", ""),
                    ts,
                    student_id,
                ),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def delete_student(self, student_id: int) -> bool:
        conn = self._connect()
        try:
            cur = conn.execute("DELETE FROM students WHERE id=?", (student_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def import_students_from_csv(self, csv_path: str) -> int:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(csv_path)

        count = 0
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                payload = {
                    "mssv": row.get("MSSV", row.get("mssv", "")).strip(),
                    "full_name": row.get("Họ tên", row.get("Ho ten", row.get("full_name", ""))).strip(),
                    "github_url": row.get("Link GitHub", row.get("github_url", "")).strip(),
                    "class_name": row.get("Lớp", row.get("class_name", "")).strip(),
                    "group_name": row.get("Nhóm", row.get("group_name", "")).strip(),
                }
                if payload["mssv"] or payload["full_name"] or payload["github_url"]:
                    self.create_student(payload)
                    count += 1
        return count

    # scan persistence
    def create_scan(self, payload: Dict[str, Any]) -> int:
        conn = self._connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO scans (source_type, source_ref, section, bai_range, assignment, deadline_iso, created_at, report_json_path, report_csv_path, meta_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.get("source_type", ""),
                    payload.get("source_ref", ""),
                    payload.get("section", ""),
                    payload.get("bai_range", ""),
                    payload.get("assignment", ""),
                    payload.get("deadline_iso", ""),
                    payload.get("created_at", now_iso()),
                    payload.get("report_json_path", ""),
                    payload.get("report_csv_path", ""),
                    json.dumps(payload.get("meta", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def save_scan_entries(self, scan_id: int, entries: List[Dict[str, Any]]) -> None:
        conn = self._connect()
        try:
            for e in entries:
                conn.execute(
                    """
                    INSERT INTO scan_entries (
                        scan_id, row_number, mssv, full_name, class_name, group_name,
                        repo_url, repo_full_name, submitted_status, deadline_status,
                        last_commit_at, score_10, repo_status, plagiarism_high_risk,
                        comments, details_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        scan_id,
                        int(e.get("row_number", 0)),
                        e.get("student_id", ""),
                        e.get("student_name", ""),
                        e.get("class_name", ""),
                        e.get("group", ""),
                        e.get("repo_url", ""),
                        e.get("repo_full_name", ""),
                        e.get("submitted_status", ""),
                        e.get("deadline_status", ""),
                        e.get("last_commit_at", ""),
                        float(e.get("score_10", 0.0)),
                        e.get("repo_status", ""),
                        1 if e.get("plagiarism_high_risk", False) else 0,
                        e.get("comments", ""),
                        json.dumps(e, ensure_ascii=False),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def list_scans(self) -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute("SELECT * FROM scans ORDER BY id DESC").fetchall()
            out: List[Dict[str, Any]] = []
            for r in rows:
                d = dict(r)
                try:
                    d["meta"] = json.loads(d.get("meta_json") or "{}")
                except Exception:
                    d["meta"] = {}
                out.append(d)
            return out
        finally:
            conn.close()

    def get_scan_entries(self, scan_id: int) -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM scan_entries WHERE scan_id=? ORDER BY score_10 DESC, id ASC",
                (scan_id,),
            ).fetchall()
            out: List[Dict[str, Any]] = []
            for r in rows:
                d = dict(r)
                try:
                    details = json.loads(d.get("details_json") or "{}")
                except Exception:
                    details = {}
                d["details"] = details
                out.append(d)
            return out
        finally:
            conn.close()


class SmartGitHubAssignmentChecker:
    def __init__(self, base_dir: str, db_name: str = "smart_checker.db") -> None:
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "smart_checker_data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.storage = SmartStorage(os.path.join(self.data_dir, db_name))
        self._scan_thread: Optional[threading.Thread] = None
        self._scan_stop = threading.Event()

    # ---------- Core scan ----------
    def _fetch_last_commit(self, client: GithubClient, repo_full_name: str) -> str:
        data, status, _ = client._request_json(f"/repos/{repo_full_name}/commits?per_page=1")  # pylint: disable=protected-access
        if status >= 400 or not isinstance(data, list) or not data:
            return ""
        first = data[0]
        commit_obj = first.get("commit", {}) if isinstance(first, dict) else {}
        author_obj = commit_obj.get("author", {}) if isinstance(commit_obj, dict) else {}
        date_str = author_obj.get("date", "") if isinstance(author_obj, dict) else ""
        return str(date_str or "")

    def _deadline_status(self, last_commit_at: str, deadline_iso: str) -> str:
        deadline = parse_iso_or_none(deadline_iso)
        if deadline is None:
            return "N/A"
        last_dt = parse_iso_or_none(last_commit_at)
        if last_dt is None:
            return "CHUA_NOP"
        if last_dt <= deadline:
            return "DUNG_HAN"
        return "TRE_HAN"

    def run_scan_from_sheet(self, sheet_url: str, cfg: ScanConfig) -> Dict[str, Any]:
        required_files = parse_required_files("", cfg.bai_range)
        spec = RequirementSpec(
            section=cfg.section,
            required_files=required_files,
            assignment_text=cfg.assignment,
            enabled=True,
        )

        report = build_report(
            sheet_url=sheet_url,
            token=cfg.token,
            spec=spec,
            max_workers=MAX_WORKERS,
            similarity_threshold=cfg.similarity_threshold,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_json_path = os.path.join(self.data_dir, f"report_{timestamp}.json")
        report_csv_path = os.path.join(self.data_dir, f"report_{timestamp}.csv")

        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        from github_sheet_tool_lib.core import write_exercise_summary_csv

        write_exercise_summary_csv(report, report_csv_path)

        # Build detailed entries with deadline and quick AI comment.
        repo_result_map: Dict[str, Dict[str, Any]] = {}
        exercise = report.get("exercise_check", {})
        for r in exercise.get("repo_results", []):
            repo_result_map[str(r.get("repo", ""))] = r

        client = GithubClient(cfg.token)
        entries: List[Dict[str, Any]] = []
        for s in report.get("submitter_overview", []):
            repo_full = str(s.get("repo_full_name", ""))
            repo_result = repo_result_map.get(repo_full, {})
            last_commit_at = self._fetch_last_commit(client, repo_full) if s.get("accessible", False) else ""
            deadline_state = self._deadline_status(last_commit_at, cfg.deadline_iso)

            files = repo_result.get("files", [])
            first_notes = []
            if files and isinstance(files, list):
                for fobj in files[:2]:
                    notes = fobj.get("notes", [])
                    if isinstance(notes, list):
                        first_notes.extend(notes[:2])
            comments = " | ".join(first_notes[:4])

            entry = {
                "row_number": s.get("row_number", 0),
                "student_id": s.get("student_id", ""),
                "student_name": s.get("student_name", ""),
                "class_name": s.get("class_name", ""),
                "group": s.get("group", ""),
                "repo_url": s.get("repo_url", ""),
                "repo_full_name": repo_full,
                "submitted_status": "DA_NOP" if s.get("accessible", False) else "CHUA_NOP",
                "deadline_status": deadline_state,
                "last_commit_at": last_commit_at,
                "score_10": float(repo_result.get("score_10", 0.0)),
                "repo_status": repo_result.get("repo_status", "N/A"),
                "plagiarism_high_risk": bool(repo_result.get("plagiarism_high_risk", False)),
                "comments": comments,
                "repo_contents": s.get("repo_contents", {}),
                "files": repo_result.get("files", []),
            }
            entries.append(entry)

        scan_id = self.storage.create_scan(
            {
                "source_type": "google_sheet",
                "source_ref": sheet_url,
                "section": cfg.section,
                "bai_range": cfg.bai_range,
                "assignment": cfg.assignment,
                "deadline_iso": cfg.deadline_iso,
                "created_at": now_iso(),
                "report_json_path": report_json_path,
                "report_csv_path": report_csv_path,
                "meta": {
                    "submitted_links": report.get("submitted_links", 0),
                    "accessible_links": report.get("accessible_links", 0),
                    "warnings": len(report.get("warnings", [])),
                },
            }
        )

        self.storage.save_scan_entries(scan_id, entries)

        return {
            "scan_id": scan_id,
            "report_json_path": report_json_path,
            "report_csv_path": report_csv_path,
            "summary": {
                "submitted_links": report.get("submitted_links", 0),
                "accessible_links": report.get("accessible_links", 0),
                "pass_count": exercise.get("pass_count", 0),
                "warn_count": exercise.get("warn_count", 0),
                "fail_count": exercise.get("fail_count", 0),
            },
            "report": report,
        }

    # ---------- Analytics ----------
    def get_dashboard(self, scan_id: int) -> Dict[str, Any]:
        entries = self.storage.get_scan_entries(scan_id)
        total = len(entries)
        if total == 0:
            return {
                "total": 0,
                "submitted_percent": 0.0,
                "late_percent": 0.0,
                "missing_percent": 0.0,
                "by_group": [],
            }

        submitted = sum(1 for e in entries if e.get("submitted_status") == "DA_NOP")
        late = sum(1 for e in entries if e.get("deadline_status") == "TRE_HAN")
        missing = sum(1 for e in entries if e.get("submitted_status") != "DA_NOP")

        by_group_map: Dict[str, Dict[str, Any]] = {}
        for e in entries:
            g = (e.get("group_name") or e.get("group") or "NO_GROUP").strip() or "NO_GROUP"
            if g not in by_group_map:
                by_group_map[g] = {"group": g, "total": 0, "submitted": 0, "avg_score_10": 0.0, "scores": []}
            by_group_map[g]["total"] += 1
            if e.get("submitted_status") == "DA_NOP":
                by_group_map[g]["submitted"] += 1
            by_group_map[g]["scores"].append(float(e.get("score_10", 0.0)))

        by_group = []
        for g, obj in by_group_map.items():
            scores = obj.pop("scores", [])
            obj["avg_score_10"] = round(sum(scores) / max(1, len(scores)), 2)
            by_group.append(obj)

        by_group.sort(key=lambda x: x["group"])

        return {
            "total": total,
            "submitted_percent": round(submitted * 100.0 / total, 2),
            "late_percent": round(late * 100.0 / total, 2),
            "missing_percent": round(missing * 100.0 / total, 2),
            "by_group": by_group,
        }

    def ask_chatbot(self, scan_id: int, question: str) -> str:
        q = (question or "").lower().strip()
        entries = self.storage.get_scan_entries(scan_id)
        if not entries:
            return "Chua co du lieu scan de tra loi."

        if "chua nop" in q or "ai chua" in q:
            rows = [e for e in entries if e.get("submitted_status") != "DA_NOP"]
            if not rows:
                return "Tat ca sinh vien da nop."
            lines = [f"- {e.get('full_name') or e.get('student_name')} ({e.get('mssv') or e.get('student_id')})" for e in rows[:20]]
            return "Sinh vien chua nop:\n" + "\n".join(lines)

        if "tre" in q or "trễ" in q:
            rows = [e for e in entries if e.get("deadline_status") == "TRE_HAN"]
            if not rows:
                return "Khong co sinh vien nop tre han."
            lines = [f"- {e.get('full_name') or e.get('student_name')} ({e.get('mssv') or e.get('student_id')})" for e in rows[:20]]
            return "Sinh vien nop tre:\n" + "\n".join(lines)

        if (
            "yeu" in q
            or "yếu" in q
            or "thap" in q
            or "thấp" in q
            or "can cai thien" in q
            or "bottom" in q
        ):
            ranked: List[Dict[str, Any]] = []
            for e in entries:
                submitted = e.get("submitted_status") == "DA_NOP"
                late = e.get("deadline_status") == "TRE_HAN"
                risk = bool(e.get("plagiarism_high_risk"))
                score = float(e.get("score_10", 0.0))

                penalty = 0
                reasons: List[str] = []
                if not submitted:
                    penalty += 5
                    reasons.append("chua nop")
                if late:
                    penalty += 2
                    reasons.append("tre han")
                if risk:
                    penalty += 3
                    reasons.append("nghi dao code")
                if score < 5:
                    penalty += 3
                    reasons.append("diem < 5")
                elif score < 7:
                    penalty += 2
                    reasons.append("diem < 7")
                elif score < 8:
                    penalty += 1

                if penalty > 0:
                    ranked.append(
                        {
                            "name": e.get("full_name") or e.get("student_name") or "N/A",
                            "mssv": e.get("mssv") or e.get("student_id") or "N/A",
                            "score": score,
                            "penalty": penalty,
                            "reasons": reasons,
                        }
                    )

            if not ranked:
                return "Khong tim thay nhom sinh vien yeu can uu tien."

            ranked.sort(key=lambda x: (-int(x["penalty"]), float(x["score"]), str(x["name"])))
            top = ranked[:10]
            lines = [
                f"- {r['name']} ({r['mssv']}): {float(r['score']):.2f}/10 | Uu tien {int(r['penalty'])} | {', '.join(r['reasons']) or 'can theo doi'}"
                for r in top
            ]
            return (
                "Top sinh vien yeu can xu ly som:\n"
                + "\n".join(lines)
                + "\n\nGoi y: uu tien lien he nhom 'chua nop' va 'nghi dao code' truoc."
            )

        if "top" in q or "tot nhat" in q or "tốt nhất" in q:
            rows = sorted(entries, key=lambda x: float(x.get("score_10", 0.0)), reverse=True)[:10]
            lines = [f"- {e.get('full_name') or e.get('student_name')}: {float(e.get('score_10', 0.0)):.2f}/10" for e in rows]
            return "Top sinh vien theo diem:\n" + "\n".join(lines)

        return "Ban co the hoi: 'Ai chua nop?', 'Ai nop tre?', 'Top sinh vien tot nhat?', 'Top sinh vien yeu?'"

    # ---------- Auto scan ----------
    def start_auto_scan(
        self,
        sheet_url: str,
        cfg: ScanConfig,
        interval_minutes: int = 10,
    ) -> str:
        if self._scan_thread and self._scan_thread.is_alive():
            return "Auto scan dang chay."

        self._scan_stop.clear()

        def _loop() -> None:
            while not self._scan_stop.is_set():
                try:
                    self.run_scan_from_sheet(sheet_url, cfg)
                except Exception:
                    pass
                # sleep in chunks so stop is responsive
                for _ in range(max(1, interval_minutes * 6)):
                    if self._scan_stop.is_set():
                        break
                    time.sleep(10)

        self._scan_thread = threading.Thread(target=_loop, daemon=True)
        self._scan_thread.start()
        return "Da bat auto scan."

    def stop_auto_scan(self) -> str:
        self._scan_stop.set()
        return "Da dung auto scan."

    # ---------- Export ----------
    def export_scan_csv(self, scan_id: int, out_path: str) -> str:
        entries = self.storage.get_scan_entries(scan_id)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        headers = [
            "mssv",
            "full_name",
            "group_name",
            "repo_full_name",
            "submitted_status",
            "deadline_status",
            "last_commit_at",
            "score_10",
            "repo_status",
            "plagiarism_high_risk",
            "comments",
        ]
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for e in entries:
                writer.writerow({k: e.get(k, "") for k in headers})
        return out_path

    def export_scan_pdf_like(self, scan_id: int, out_path: str) -> str:
        # Simple HTML report (print-to-PDF from browser). This keeps dependencies zero.
        entries = self.storage.get_scan_entries(scan_id)
        dashboard = self.get_dashboard(scan_id)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

        rows_html = "".join(
            f"<tr><td>{e.get('mssv','')}</td><td>{e.get('full_name','')}</td><td>{e.get('repo_full_name','')}</td>"
            f"<td>{e.get('submitted_status','')}</td><td>{e.get('deadline_status','')}</td><td>{float(e.get('score_10',0.0)):.2f}</td></tr>"
            for e in entries
        )

        html = f"""
        <html><head><meta charset='utf-8'><title>Smart Checker Report</title></head>
        <body style='font-family:Segoe UI,Arial,sans-serif'>
          <h2>Smart GitHub Assignment Checker with AI</h2>
          <p>Submitted: {dashboard.get('submitted_percent',0)}% | Late: {dashboard.get('late_percent',0)}% | Missing: {dashboard.get('missing_percent',0)}%</p>
          <table border='1' cellpadding='6' cellspacing='0'>
            <tr><th>MSSV</th><th>Ho ten</th><th>Repo</th><th>Nop</th><th>Deadline</th><th>Diem/10</th></tr>
            {rows_html}
          </table>
        </body></html>
        """
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        return out_path
