from __future__ import annotations

import json
import os
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import tkinter as tk
from tkinter import END, DISABLED, NORMAL, StringVar, Tk, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from github_sheet_tool_lib.core import (  # noqa: E402
    MAX_WORKERS,
    GithubClient,
    RequirementSpec,
    build_report,
    parse_required_files,
    write_exercise_summary_csv,
)


class GithubDashboardUI:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Smart GitHub Assignment Checker with AI")
        self.root.geometry("1360x860")
        self.root.minsize(1200, 760)

        self.mode = StringVar(value="light")
        self.sheet_url = StringVar(value="")
        self.section = StringVar(value="2.3")
        self.search_text = StringVar(value="")
        self.deadline_iso = StringVar(value="")
        self.refresh_min = StringVar(value="10")
        self.filter_mode = StringVar(value="all")
        self.notify_text = StringVar(value="Thông báo: Chưa có dữ liệu")

        self.stat_total = StringVar(value="0")
        self.stat_submitted = StringVar(value="0")
        self.stat_missing = StringVar(value="0")
        self.stat_late = StringVar(value="0")

        self.status_text = StringVar(value="Trạng thái: Sẵn sàng")
        self.last_json_path = StringVar(value="")
        self.last_csv_path = StringVar(value="")

        self.palette: Dict[str, str] = {}
        self.students: List[Dict[str, Any]] = []
        self.repo_result_map: Dict[str, Dict[str, Any]] = {}
        self.current_report: Dict[str, Any] = {}
        self.current_similarity: Dict[str, Any] = {}
        self.selected_student: Dict[str, Any] | None = None

        self.student_tree: ttk.Treeview
        self.rank_tree: ttk.Treeview
        self.log_text: ScrolledText
        self.detail_text: ScrolledText
        self.commit_canvas: tk.Canvas
        self.pie_canvas: tk.Canvas
        self.bar_canvas: tk.Canvas
        self.progress: ttk.Progressbar
        self.run_btn: ttk.Button

        self._setup_style("light")
        self._build_ui()
        self._apply_theme("light")

    # ---------- theme ----------
    def _palette(self, mode: str) -> Dict[str, str]:
        if mode == "dark":
            return {
                "bg": "#071B2E",
                "card": "#102A43",
                "text": "#E7F2FF",
                "sub": "#9AC0E6",
                "accent": "#2F86D6",
                "soft": "#163854",
                "logbg": "#0C2238",
                "logfg": "#DAECFF",
            }
        return {
            "bg": "#EAF3FF",
            "card": "#FFFFFF",
            "text": "#12324D",
            "sub": "#1F6FB8",
            "accent": "#2F86D6",
            "soft": "#D8EBFF",
            "logbg": "#F5FAFF",
            "logfg": "#133A5E",
        }

    def _setup_style(self, mode: str) -> None:
        self.palette = self._palette(mode)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Page.TFrame", background=self.palette["bg"])
        style.configure("Card.TFrame", background=self.palette["card"])
        style.configure("TopTitle.TLabel", background=self.palette["bg"], foreground=self.palette["text"], font=("Segoe UI", 19, "bold"))
        style.configure("TopSub.TLabel", background=self.palette["bg"], foreground=self.palette["sub"], font=("Segoe UI", 10))
        style.configure("Field.TLabel", background=self.palette["bg"], foreground=self.palette["text"], font=("Segoe UI", 10, "bold"))
        style.configure("CardTitle.TLabel", background=self.palette["card"], foreground=self.palette["text"], font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", background=self.palette["bg"], foreground=self.palette["sub"], font=("Segoe UI", 9, "italic"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7))
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(10, 6))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _apply_theme(self, mode: str) -> None:
        self._setup_style(mode)
        self.root.configure(bg=self.palette["bg"])
        self.log_text.configure(bg=self.palette["logbg"], fg=self.palette["logfg"], insertbackground=self.palette["logfg"])
        self.detail_text.configure(bg=self.palette["logbg"], fg=self.palette["logfg"], insertbackground=self.palette["logfg"])
        self._draw_charts()

    def _toggle_theme(self) -> None:
        m = "dark" if self.mode.get() == "light" else "light"
        self.mode.set(m)
        self._apply_theme(m)

    # ---------- layout ----------
    def _build_ui(self) -> None:
        page = ttk.Frame(self.root, style="Page.TFrame", padding=12)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(3, weight=1)

        self._build_topbar(page)
        self._build_cards(page)
        self._build_main(page)

        self.progress = ttk.Progressbar(page, mode="indeterminate")
        self.progress.grid(row=4, column=0, sticky="ew", pady=(8, 2))
        ttk.Label(page, textvariable=self.status_text, style="Status.TLabel").grid(row=5, column=0, sticky="w")

    def _build_topbar(self, parent: ttk.Frame) -> None:
        top = ttk.Frame(parent, style="Page.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top.columnconfigure(1, weight=1)

        title = ttk.Frame(top, style="Page.TFrame")
        title.grid(row=0, column=0, sticky="w")
        ttk.Label(title, text="Smart GitHub Assignment Checker with AI", style="TopTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(title, text="Một màn hình: tìm kiếm - thống kê - bảng SV - panel chi tiết", style="TopSub.TLabel").grid(row=1, column=0, sticky="w")

        controls = ttk.Frame(top, style="Page.TFrame")
        controls.grid(row=0, column=1, sticky="e")

        ttk.Label(controls, text="Tìm kiếm", style="Field.TLabel").grid(row=0, column=0, padx=(0, 6))
        ttk.Entry(controls, textvariable=self.search_text, width=24).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(controls, text="Lọc", style="Secondary.TButton", command=self._refresh_student_table).grid(row=0, column=2, padx=(0, 8))

        ttk.Label(controls, text="Deadline ISO", style="Field.TLabel").grid(row=0, column=3, padx=(0, 6))
        ttk.Entry(controls, textvariable=self.deadline_iso, width=20).grid(row=0, column=4, padx=(0, 8))

        ttk.Label(controls, text="Refresh (phút)", style="Field.TLabel").grid(row=0, column=5, padx=(0, 6))
        ttk.Entry(controls, textvariable=self.refresh_min, width=6).grid(row=0, column=6, padx=(0, 8))

        ttk.Button(controls, text="🌙 Light/Dark", style="Secondary.TButton", command=self._toggle_theme).grid(row=0, column=7, padx=(0, 8))
        ttk.Button(controls, text="🔔 Thông báo", style="Secondary.TButton", command=self._show_notifications).grid(row=0, column=8)

        line2 = ttk.Frame(parent, style="Page.TFrame")
        line2.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        line2.columnconfigure(1, weight=1)
        line2.columnconfigure(3, weight=1)

        ttk.Label(line2, text="Google Sheet URL", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Entry(line2, textvariable=self.sheet_url).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Label(line2, text="Folder cần kiểm tra", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 6))
        ttk.Entry(line2, textvariable=self.section, width=22).grid(row=0, column=3, sticky="ew", padx=(0, 10))
        self.run_btn = ttk.Button(line2, text="🔄 Scan GitHub", style="Primary.TButton", command=self.on_scan)
        self.run_btn.grid(row=0, column=4, padx=(0, 8))

    def _build_cards(self, parent: ttk.Frame) -> None:
        cards = ttk.Frame(parent, style="Page.TFrame")
        cards.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        for i in range(4):
            cards.columnconfigure(i, weight=1)

        self._card(cards, 0, "👨‍🎓 Tổng SV", self.stat_total)
        self._card(cards, 1, "✅ Đã nộp", self.stat_submitted)
        self._card(cards, 2, "❌ Chưa nộp", self.stat_missing)
        self._card(cards, 3, "⚠️ Trễ", self.stat_late)

    def _card(self, parent: ttk.Frame, col: int, title: str, value_var: StringVar) -> None:
        f = tk.Frame(parent, bg=self.palette["soft"], padx=12, pady=10)
        f.grid(row=0, column=col, sticky="ew", padx=6)
        ttk.Label(f, text=title, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(f, textvariable=value_var, style="TopTitle.TLabel").grid(row=1, column=0, sticky="w")

    def _build_main(self, parent: ttk.Frame) -> None:
        main = ttk.Panedwindow(parent, orient="horizontal")
        main.grid(row=3, column=0, sticky="nsew")

        left = ttk.Frame(main, style="Card.TFrame", padding=10)
        right = ttk.Frame(main, style="Card.TFrame", padding=10)
        main.add(left, weight=3)
        main.add(right, weight=2)

        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Charts
        chart_wrap = ttk.Frame(left, style="Card.TFrame")
        chart_wrap.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        chart_wrap.columnconfigure(0, weight=1)
        chart_wrap.columnconfigure(1, weight=1)

        pie_box = ttk.Frame(chart_wrap, style="Card.TFrame")
        bar_box = ttk.Frame(chart_wrap, style="Card.TFrame")
        pie_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        bar_box.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        ttk.Label(pie_box, text="Biểu đồ tròn: Nộp/Chưa nộp", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.pie_canvas = tk.Canvas(pie_box, height=180, bg=self.palette["card"], highlightthickness=0)
        self.pie_canvas.grid(row=1, column=0, sticky="ew")

        ttk.Label(bar_box, text="Biểu đồ cột: Theo nhóm", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.bar_canvas = tk.Canvas(bar_box, height=180, bg=self.palette["card"], highlightthickness=0)
        self.bar_canvas.grid(row=1, column=0, sticky="ew")

        # Student table
        table_panel = ttk.Frame(left, style="Card.TFrame")
        table_panel.grid(row=1, column=0, sticky="nsew")
        table_panel.rowconfigure(2, weight=1)
        table_panel.columnconfigure(0, weight=1)

        ttk.Label(table_panel, text="Bảng sinh viên", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        filter_row = ttk.Frame(table_panel, style="Card.TFrame")
        filter_row.grid(row=1, column=0, sticky="ew", pady=(4, 6))
        ttk.Button(filter_row, text="Tất cả", style="Secondary.TButton", command=lambda: self._set_filter("all")).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(filter_row, text="Chưa nộp", style="Secondary.TButton", command=lambda: self._set_filter("missing")).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(filter_row, text="Trễ", style="Secondary.TButton", command=lambda: self._set_filter("late")).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(filter_row, text="Điểm thấp", style="Secondary.TButton", command=lambda: self._set_filter("low")).grid(row=0, column=3)

        cols = ("mssv", "name", "repo", "status", "score", "action")
        self.student_tree = ttk.Treeview(table_panel, columns=cols, show="headings", height=16)
        self.student_tree.heading("mssv", text="MSSV")
        self.student_tree.heading("name", text="Tên")
        self.student_tree.heading("repo", text="GitHub")
        self.student_tree.heading("status", text="Trạng thái")
        self.student_tree.heading("score", text="Điểm")
        self.student_tree.heading("action", text="Action")

        self.student_tree.column("mssv", width=90, anchor="center")
        self.student_tree.column("name", width=160, anchor="w")
        self.student_tree.column("repo", width=240, anchor="w")
        self.student_tree.column("status", width=110, anchor="center")
        self.student_tree.column("score", width=70, anchor="center")
        self.student_tree.column("action", width=180, anchor="center")

        self.student_tree.tag_configure("submitted", foreground="#1A7F37")
        self.student_tree.tag_configure("missing", foreground="#B42318")
        self.student_tree.tag_configure("late", foreground="#B26A00")

        self.student_tree.grid(row=2, column=0, sticky="nsew")
        self.student_tree.bind("<<TreeviewSelect>>", self._on_select_student)
        self.student_tree.bind("<Double-1>", self._on_student_double_click)

        # Right detail panel
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Panel chi tiết sinh viên", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.detail_text = ScrolledText(right, height=11, bg=self.palette["logbg"], fg=self.palette["logfg"], insertbackground=self.palette["logfg"], relief="flat", font=("Consolas", 10))
        self.detail_text.grid(row=1, column=0, sticky="ew", pady=(6, 8))

        ttk.Label(right, text="Timeline commit", style="CardTitle.TLabel").grid(row=2, column=0, sticky="w")
        self.commit_canvas = tk.Canvas(right, height=160, bg=self.palette["card"], highlightthickness=0)
        self.commit_canvas.grid(row=3, column=0, sticky="ew", pady=(4, 8))

        action_right = ttk.Frame(right, style="Card.TFrame")
        action_right.grid(row=4, column=0, sticky="ew")
        ttk.Button(action_right, text="👁️ View", style="Secondary.TButton", command=self._action_view).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(action_right, text="🤖 AI", style="Secondary.TButton", command=self._action_ai).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(action_right, text="🔍 Check đạo code", style="Secondary.TButton", command=self._open_plagiarism_popup).grid(row=0, column=2)

        ttk.Label(right, text="Nhật ký nhanh", style="CardTitle.TLabel").grid(row=5, column=0, sticky="w", pady=(8, 0))
        self.log_text = ScrolledText(right, height=8, bg=self.palette["logbg"], fg=self.palette["logfg"], insertbackground=self.palette["logfg"], relief="flat", font=("Consolas", 9))
        self.log_text.grid(row=6, column=0, sticky="ew")

    # ---------- actions ----------
    def _set_filter(self, mode: str) -> None:
        self.filter_mode.set(mode)
        self._refresh_student_table()

    def _show_notifications(self) -> None:
        messagebox.showinfo("Thông báo", self.notify_text.get())

    def _open_file(self, path: str) -> None:
        if not path or not os.path.exists(path):
            messagebox.showwarning("Không tìm thấy", "Chưa có file để mở")
            return
        try:
            os.startfile(path)  # type: ignore[attr-defined]
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _open_last_json(self) -> None:
        self._open_file(self.last_json_path.get())

    def _open_last_csv(self) -> None:
        self._open_file(self.last_csv_path.get())

    def _set_status(self, text: str) -> None:
        self.status_text.set(f"Trạng thái: {text}")

    def _log(self, msg: str) -> None:
        def _append() -> None:
            self.log_text.insert(END, msg + "\n")
            self.log_text.see(END)

        self.root.after(0, _append)

    def _parse_deadline(self) -> datetime | None:
        raw = self.deadline_iso.get().strip()
        if not raw:
            return None
        try:
            if raw.endswith("Z"):
                raw = raw[:-1] + "+00:00"
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    def _fetch_runtime_meta(self, repos: List[str], token: str | None) -> Dict[str, Dict[str, Any]]:
        client = GithubClient(token)
        result: Dict[str, Dict[str, Any]] = {}
        for repo in repos:
            meta = {
                "branch": "",
                "last_commit": "",
                "timeline": [],
                "commit_count": 0,
                "contributors": 0,
            }
            repo_info, status, _ = client._request_json(f"/repos/{repo}")  # pylint: disable=protected-access
            if status < 400 and isinstance(repo_info, dict):
                meta["branch"] = str(repo_info.get("default_branch", ""))

            commits, cstatus, _ = client._request_json(f"/repos/{repo}/commits?per_page=20")  # pylint: disable=protected-access
            if cstatus < 400 and isinstance(commits, list):
                dates: List[str] = []
                for c in commits:
                    cobj = c.get("commit", {}) if isinstance(c, dict) else {}
                    aobj = cobj.get("author", {}) if isinstance(cobj, dict) else {}
                    d = str(aobj.get("date", "")) if isinstance(aobj, dict) else ""
                    if d:
                        dates.append(d)
                if dates:
                    meta["last_commit"] = dates[0]
                    meta["timeline"] = dates
                meta["commit_count"] = len(dates)

            contributors, tstatus, _ = client._request_json(f"/repos/{repo}/contributors?per_page=100&page=1")  # pylint: disable=protected-access
            if tstatus < 400 and isinstance(contributors, list):
                meta["contributors"] = len(contributors)

            result[repo] = meta
        return result

    def on_scan(self) -> None:
        if not self.sheet_url.get().strip():
            messagebox.showerror("Thiếu dữ liệu", "Bạn phải nhập Google Sheet URL")
            return
        if not self.section.get().strip():
            messagebox.showerror("Thiếu dữ liệu", "Bạn phải nhập folder cần kiểm tra")
            return

        self.run_btn.configure(state=DISABLED)
        self.progress.start(10)
        self._set_status("Đang quét GitHub...")
        self._log("Bắt đầu scan...")
        threading.Thread(target=self._run_scan_worker, daemon=True).start()

    def _run_scan_worker(self) -> None:
        try:
            section = self.section.get().strip()
            sheet_url = self.sheet_url.get().strip()
            token = os.getenv("GITHUB_TOKEN", "").strip() or None

            required_files = parse_required_files("", "1-5")
            spec = RequirementSpec(
                section=section,
                required_files=required_files,
                assignment_text=f"kiem tra bai trong folder {section}",
                enabled=True,
            )

            report = build_report(
                sheet_url=sheet_url,
                token=token,
                spec=spec,
                max_workers=MAX_WORKERS,
                similarity_threshold=0.9,
            )

            safe = section.replace("/", "_").replace("\\", "_").replace(" ", "_")
            out_json = f"baitapclass/github_sheet_report_{safe}.json"
            out_csv = f"baitapclass/github_sheet_report_{safe}_summary.csv"

            os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            write_exercise_summary_csv(report, out_csv)

            self.current_report = report
            self.current_similarity = report.get("similarity_check", {})

            # enrich per-student with repo runtime info
            submitters = report.get("submitter_overview", [])
            repos = sorted({str(s.get("repo_full_name", "")) for s in submitters if s.get("accessible", False)})
            runtime_map = self._fetch_runtime_meta(repos, token)

            repo_results = {str(r.get("repo", "")): r for r in report.get("exercise_check", {}).get("repo_results", [])}
            deadline = self._parse_deadline()

            rows: List[Dict[str, Any]] = []
            late = 0
            missing = 0
            submitted = 0
            for s in submitters:
                repo = str(s.get("repo_full_name", ""))
                rmeta = runtime_map.get(repo, {})
                rres = repo_results.get(repo, {})
                score10 = float(rres.get("score_10", 0.0))
                status = "Đã nộp" if s.get("accessible", False) else "Chưa nộp"
                last_commit = str(rmeta.get("last_commit", ""))
                if s.get("accessible", False):
                    submitted += 1
                    if deadline and last_commit:
                        try:
                            d = last_commit.replace("Z", "+00:00")
                            ldt = datetime.fromisoformat(d)
                            if ldt.tzinfo is None:
                                ldt = ldt.replace(tzinfo=timezone.utc)
                            if ldt > deadline:
                                status = "Trễ"
                                late += 1
                        except Exception:
                            pass
                else:
                    missing += 1

                row = {
                    "mssv": s.get("student_id", ""),
                    "name": s.get("student_name", ""),
                    "group": s.get("group", ""),
                    "repo": repo,
                    "repo_url": s.get("repo_url", ""),
                    "status": status,
                    "score": score10,
                    "contents": s.get("repo_contents", {}),
                    "repo_result": rres,
                    "runtime": rmeta,
                }
                rows.append(row)

            self.students = rows
            self.repo_result_map = repo_results

            total = len(rows)
            self.root.after(0, lambda: self.stat_total.set(str(total)))
            self.root.after(0, lambda: self.stat_submitted.set(str(submitted)))
            self.root.after(0, lambda: self.stat_missing.set(str(missing)))
            self.root.after(0, lambda: self.stat_late.set(str(late)))

            # notifications
            high_risk = sum(1 for v in report.get("plagiarism_flags", {}).values() if v.get("high_risk"))
            note = f"{missing} sinh viên chưa nộp | {high_risk} trường hợp nghi đạo code"
            self.root.after(0, lambda: self.notify_text.set(f"Thông báo: {note}"))

            self.root.after(0, self._refresh_student_table)
            self.root.after(0, self._draw_charts)
            self.root.after(0, lambda: self.last_json_path.set(out_json))
            self.root.after(0, lambda: self.last_csv_path.set(out_csv))
            self._log(f"Hoàn tất. JSON: {out_json}")
            self._log(f"CSV: {out_csv}")
            self.root.after(0, lambda: self._set_status("Hoàn tất"))
        except Exception as e:
            self._log(f"Lỗi: {e}\n{traceback.format_exc()}")
            self.root.after(0, lambda: messagebox.showerror("Có lỗi", str(e)))
            self.root.after(0, lambda: self._set_status("Lỗi"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.run_btn.configure(state=NORMAL))

    # ---------- charts ----------
    def _draw_charts(self) -> None:
        self._draw_pie()
        self._draw_bar()

    def _draw_pie(self) -> None:
        c = self.pie_canvas
        c.delete("all")
        total = max(1, int(self.stat_total.get() or "0"))
        submitted = int(self.stat_submitted.get() or "0")
        missing = max(0, total - submitted)
        p_sub = submitted / total
        angle = int(360 * p_sub)

        w = int(c.winfo_width() or 320)
        h = int(c.winfo_height() or 180)
        x0, y0, x1, y1 = 20, 10, min(w - 20, 170), min(h - 10, 160)
        c.create_arc(x0, y0, x1, y1, start=0, extent=angle, fill="#1A7F37", outline="")
        c.create_arc(x0, y0, x1, y1, start=angle, extent=360 - angle, fill="#B42318", outline="")
        c.create_text(200, 55, text=f"Đã nộp: {submitted}", anchor="w", fill=self.palette["text"], font=("Segoe UI", 10, "bold"))
        c.create_text(200, 85, text=f"Chưa nộp: {missing}", anchor="w", fill=self.palette["text"], font=("Segoe UI", 10, "bold"))

    def _draw_bar(self) -> None:
        c = self.bar_canvas
        c.delete("all")
        groups: Dict[str, int] = {}
        for s in self.students:
            g = str(s.get("group", "") or "NA")
            groups[g] = groups.get(g, 0) + 1
        if not groups:
            c.create_text(20, 20, text="Chưa có dữ liệu nhóm", anchor="w", fill=self.palette["sub"], font=("Segoe UI", 10))
            return

        items = sorted(groups.items(), key=lambda x: x[1], reverse=True)[:8]
        max_v = max(v for _, v in items)
        x = 20
        for g, v in items:
            bar_h = int((v / max_v) * 110)
            c.create_rectangle(x, 140 - bar_h, x + 28, 140, fill="#2F86D6", outline="")
            c.create_text(x + 14, 148, text=g, anchor="n", fill=self.palette["text"], font=("Segoe UI", 8))
            c.create_text(x + 14, 140 - bar_h - 6, text=str(v), anchor="s", fill=self.palette["text"], font=("Segoe UI", 8, "bold"))
            x += 42

    # ---------- table / detail ----------
    def _refresh_student_table(self) -> None:
        kw = self.search_text.get().strip().lower()
        mode = self.filter_mode.get()

        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        rows = self.students
        if kw:
            rows = [
                r for r in rows
                if kw in str(r.get("name", "")).lower()
                or kw in str(r.get("mssv", "")).lower()
                or kw in str(r.get("repo", "")).lower()
            ]

        if mode == "missing":
            rows = [r for r in rows if r.get("status") == "Chưa nộp"]
        elif mode == "late":
            rows = [r for r in rows if r.get("status") == "Trễ"]
        elif mode == "low":
            rows = [r for r in rows if float(r.get("score", 0.0)) < 5.0]

        for i, r in enumerate(rows):
            tag = "submitted"
            if r.get("status") == "Chưa nộp":
                tag = "missing"
            elif r.get("status") == "Trễ":
                tag = "late"
            self.student_tree.insert(
                "",
                END,
                iid=f"row_{i}",
                values=(
                    r.get("mssv", ""),
                    r.get("name", ""),
                    r.get("repo", ""),
                    r.get("status", ""),
                    f"{float(r.get('score', 0.0)):.1f}",
                    "View | AI | Check đạo",
                ),
                tags=(tag,),
            )

    def _get_selected_row(self) -> Dict[str, Any] | None:
        selected = self.student_tree.selection()
        if not selected:
            return None
        idx_str = selected[0].split("_")[-1]
        try:
            idx = int(idx_str)
        except Exception:
            return None

        # Rebuild filtered rows to map index correctly.
        kw = self.search_text.get().strip().lower()
        mode = self.filter_mode.get()
        rows = self.students
        if kw:
            rows = [r for r in rows if kw in str(r.get("name", "")).lower() or kw in str(r.get("mssv", "")).lower() or kw in str(r.get("repo", "")).lower()]
        if mode == "missing":
            rows = [r for r in rows if r.get("status") == "Chưa nộp"]
        elif mode == "late":
            rows = [r for r in rows if r.get("status") == "Trễ"]
        elif mode == "low":
            rows = [r for r in rows if float(r.get("score", 0.0)) < 5.0]
        if idx < 0 or idx >= len(rows):
            return None
        return rows[idx]

    def _on_select_student(self, _event: Any) -> None:
        row = self._get_selected_row()
        self.selected_student = row
        self._render_detail_panel(row)

    def _on_student_double_click(self, event: Any) -> None:
        item = self.student_tree.identify_row(event.y)
        col = self.student_tree.identify_column(event.x)
        if not item:
            return
        self.student_tree.selection_set(item)
        self._on_select_student(event)
        if col == "#6":
            self._action_view()

    def _render_detail_panel(self, row: Dict[str, Any] | None) -> None:
        self.detail_text.delete("1.0", END)
        self.commit_canvas.delete("all")
        if not row:
            self.detail_text.insert(END, "Chọn 1 sinh viên để xem chi tiết.\n")
            return

        runtime = row.get("runtime", {})
        contents = row.get("contents", {})
        repo_result = row.get("repo_result", {})

        lines = [
            f"MSSV: {row.get('mssv', '')}",
            f"Tên: {row.get('name', '')}",
            f"Nhóm: {row.get('group', '')}",
            f"Repo: {row.get('repo', '')}",
            f"Trạng thái: {row.get('status', '')}",
            f"Branch: {runtime.get('branch', '')}",
            f"Commit gần nhất: {runtime.get('last_commit', '')}",
            f"Số commit (20 gần nhất): {runtime.get('commit_count', 0)}",
            f"Contributors: {runtime.get('contributors', 0)}",
            f"Điểm AI: {float(row.get('score',0.0)):.2f}/10",
            f"Repo có folder cần kiểm tra: {'Có' if contents.get('section_found', False) else 'Không'}",
            f"Tổng file .py: {contents.get('python_files_total', 0)}",
            "",
            "Nhận xét AI:",
        ]
        files = repo_result.get("files", [])
        if isinstance(files, list) and files:
            for f in files[:3]:
                notes = f.get("notes", [])
                if isinstance(notes, list):
                    for n in notes[:2]:
                        lines.append(f"- {f.get('required_name','')}: {n}")
        else:
            lines.append("- Chưa có dữ liệu chấm file.")

        self.detail_text.insert(END, "\n".join(lines))
        self._draw_commit_timeline(runtime.get("timeline", []))

    def _draw_commit_timeline(self, timeline: List[str]) -> None:
        c = self.commit_canvas
        c.delete("all")
        if not timeline:
            c.create_text(20, 20, text="Không có dữ liệu commit timeline", anchor="w", fill=self.palette["sub"], font=("Segoe UI", 10))
            return
        x = 20
        y = 90
        step = max(18, int((c.winfo_width() or 520) / max(6, len(timeline))))
        for i, dt in enumerate(timeline[:20]):
            c.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#2F86D6", outline="")
            if i > 0:
                c.create_line(x - step + 4, y, x - 4, y, fill="#6EA9E1", width=2)
            if i % 3 == 0:
                c.create_text(x, y + 16, text=dt[:10], angle=45, anchor="w", fill=self.palette["text"], font=("Segoe UI", 7))
            x += step

    # ---------- row actions ----------
    def _action_view(self) -> None:
        row = self._get_selected_row()
        if not row:
            messagebox.showinfo("Thông tin", "Hãy chọn sinh viên trước")
            return
        self._render_detail_panel(row)

    def _action_ai(self) -> None:
        row = self._get_selected_row()
        if not row:
            messagebox.showinfo("Thông tin", "Hãy chọn sinh viên trước")
            return
        repo_result = row.get("repo_result", {})
        files = repo_result.get("files", [])
        msg = [f"Sinh viên: {row.get('name','')}", f"Điểm: {float(row.get('score',0.0)):.2f}/10", ""]
        if isinstance(files, list) and files:
            for f in files[:5]:
                msg.append(f"{f.get('required_name','')}: {f.get('verdict','')} - {f.get('score',0)}")
        messagebox.showinfo("AI chấm điểm", "\n".join(msg))

    def _open_plagiarism_popup(self) -> None:
        sim = self.current_similarity or {}
        pairs = sim.get("near_duplicate_pairs", []) if isinstance(sim, dict) else []
        if not pairs:
            messagebox.showinfo("Check đạo code", "Chưa có dữ liệu cặp giống nhau.")
            return

        top = tk.Toplevel(self.root)
        top.title("Phát hiện đạo code")
        top.geometry("900x420")

        cols = ("a", "b", "pct", "file")
        tree = ttk.Treeview(top, columns=cols, show="headings", height=14)
        tree.heading("a", text="SV A (repo)")
        tree.heading("b", text="SV B (repo)")
        tree.heading("pct", text="% giống")
        tree.heading("file", text="Bài")
        tree.column("a", width=280)
        tree.column("b", width=280)
        tree.column("pct", width=90, anchor="center")
        tree.column("file", width=120, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        for i, p in enumerate(pairs[:300]):
            tree.insert(
                "",
                END,
                iid=f"p_{i}",
                values=(
                    p.get("repo_a", ""),
                    p.get("repo_b", ""),
                    f"{float(p.get('similarity',0.0))*100:.1f}%",
                    p.get("required_name", ""),
                ),
            )

        def on_open_compare(_event: Any) -> None:
            sel = tree.selection()
            if not sel:
                return
            idx = int(sel[0].split("_")[-1])
            pair = pairs[idx]
            self._open_compare_popup(pair)

        tree.bind("<Double-1>", on_open_compare)

    def _open_compare_popup(self, pair: Dict[str, Any]) -> None:
        repo_a = str(pair.get("repo_a", ""))
        repo_b = str(pair.get("repo_b", ""))
        path_a = str(pair.get("path_a", ""))
        path_b = str(pair.get("path_b", ""))

        token = os.getenv("GITHUB_TOKEN", "").strip() or None
        client = GithubClient(token)

        paths_a, branch_a, err_a = client.fetch_repo_tree(repo_a)
        paths_b, branch_b, err_b = client.fetch_repo_tree(repo_b)
        if err_a or err_b:
            messagebox.showwarning("Lỗi tải code", f"Không tải được cây repo:\n{err_a}\n{err_b}")
            return

        content_a, e1 = client.fetch_file_content(repo_a, path_a, branch_a)
        content_b, e2 = client.fetch_file_content(repo_b, path_b, branch_b)
        if e1 or e2 or content_a is None or content_b is None:
            messagebox.showwarning("Lỗi tải file", f"{e1}\n{e2}")
            return

        win = tk.Toplevel(self.root)
        win.title("So sánh code nghi trùng")
        win.geometry("1200x700")
        win.columnconfigure(0, weight=1)
        win.columnconfigure(1, weight=1)
        win.rowconfigure(0, weight=1)

        left = ScrolledText(win, font=("Consolas", 10))
        right = ScrolledText(win, font=("Consolas", 10))
        left.grid(row=0, column=0, sticky="nsew")
        right.grid(row=0, column=1, sticky="nsew")
        left.insert(END, content_a)
        right.insert(END, content_b)

        # Simple highlight by exact trimmed line overlap.
        set_b = {ln.strip() for ln in content_b.splitlines() if ln.strip()}
        for i, ln in enumerate(content_a.splitlines(), start=1):
            if ln.strip() and ln.strip() in set_b:
                left.tag_add("same", f"{i}.0", f"{i}.end")

        set_a = {ln.strip() for ln in content_a.splitlines() if ln.strip()}
        for i, ln in enumerate(content_b.splitlines(), start=1):
            if ln.strip() and ln.strip() in set_a:
                right.tag_add("same", f"{i}.0", f"{i}.end")

        left.tag_configure("same", background="#FFF2A8")
        right.tag_configure("same", background="#FFF2A8")

    # ---------- run ----------
    def _schedule_autorefresh(self) -> None:
        try:
            m = int(self.refresh_min.get().strip() or "0")
        except Exception:
            m = 0
        if m <= 0:
            return

        def _tick() -> None:
            if self.sheet_url.get().strip():
                self.on_scan()
            self.root.after(max(1, m) * 60 * 1000, _tick)

        self.root.after(max(1, m) * 60 * 1000, _tick)


def main() -> int:
    root = Tk()
    app = GithubDashboardUI(root)
    app._log("UI sẵn sàng. Nhập URL + folder rồi bấm Scan GitHub.")
    app._schedule_autorefresh()
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
