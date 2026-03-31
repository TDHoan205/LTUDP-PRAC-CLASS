from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from github_sheet_tool_lib.core import GithubClient
from github_sheet_tool_lib.smart_system import ScanConfig, SmartGitHubAssignmentChecker


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SYSTEM = SmartGitHubAssignmentChecker(base_dir=BASE_DIR)

app = FastAPI(title="Smart GitHub Assignment Checker with AI", version="1.0.0")


# ---------- Security (simple role header) ----------
def require_role(required: str, role: str | None) -> None:
    role = (role or "lecturer").lower()
    if required == "admin" and role != "admin":
        raise HTTPException(status_code=403, detail="Chi admin moi duoc phep")


# ---------- DTOs ----------
class StudentPayload(BaseModel):
    mssv: str = ""
    full_name: str = ""
    github_url: str = ""
    class_name: str = ""
    group_name: str = ""


class ScanSheetPayload(BaseModel):
    sheet_url: str
    section: str = "2.3"
    bai_range: str = "1-5"
    assignment: str = "kiem tra bai tap"
    similarity_threshold: float = 0.9
    deadline_iso: str = ""
    token: str = ""


class ChatPayload(BaseModel):
    question: str


# ---------- Student CRUD ----------
@app.get("/api/students")
def list_students() -> Dict[str, Any]:
    return {"items": SYSTEM.storage.list_students()}


@app.post("/api/students")
def create_student(payload: StudentPayload, x_role: str | None = Header(default="lecturer")) -> Dict[str, Any]:
    require_role("lecturer", x_role)
    student_id = SYSTEM.storage.create_student(payload.model_dump())
    return {"id": student_id}


@app.put("/api/students/{student_id}")
def update_student(student_id: int, payload: StudentPayload, x_role: str | None = Header(default="lecturer")) -> Dict[str, Any]:
    require_role("lecturer", x_role)
    ok = SYSTEM.storage.update_student(student_id, payload.model_dump())
    if not ok:
        raise HTTPException(status_code=404, detail="Khong tim thay sinh vien")
    return {"ok": True}


@app.delete("/api/students/{student_id}")
def delete_student(student_id: int, x_role: str | None = Header(default="admin")) -> Dict[str, Any]:
    require_role("admin", x_role)
    ok = SYSTEM.storage.delete_student(student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Khong tim thay sinh vien")
    return {"ok": True}


@app.post("/api/students/import-csv")
def import_students_csv(csv_path: str = Query(..., description="Duong dan file CSV"), x_role: str | None = Header(default="admin")) -> Dict[str, Any]:
    require_role("admin", x_role)
    count = SYSTEM.storage.import_students_from_csv(csv_path)
    return {"imported": count}


# ---------- Scan ----------
@app.post("/api/scans/from-sheet")
def run_scan_from_sheet(payload: ScanSheetPayload, x_role: str | None = Header(default="lecturer")) -> Dict[str, Any]:
    require_role("lecturer", x_role)
    cfg = ScanConfig(
        section=payload.section,
        bai_range=payload.bai_range,
        assignment=payload.assignment,
        similarity_threshold=max(0.5, min(1.0, payload.similarity_threshold)),
        deadline_iso=payload.deadline_iso,
        token=payload.token.strip() or None,
    )
    return SYSTEM.run_scan_from_sheet(payload.sheet_url, cfg)


@app.get("/api/scans")
def list_scans() -> Dict[str, List[Dict[str, Any]]]:
    return {"items": SYSTEM.storage.list_scans()}


@app.get("/api/scans/latest")
def get_latest_scan() -> Dict[str, Any]:
    scans = SYSTEM.storage.list_scans()
    if not scans:
        return {"scan_id": None}
    top = scans[0]
    return {
        "scan_id": top.get("id"),
        "created_at": top.get("created_at", ""),
        "section": top.get("section", ""),
        "report_json_path": top.get("report_json_path", ""),
    }


@app.get("/api/scans/{scan_id}/entries")
def get_scan_entries(scan_id: int) -> Dict[str, Any]:
    return {"items": SYSTEM.storage.get_scan_entries(scan_id)}


@app.get("/api/scans/{scan_id}/plagiarism")
def get_scan_plagiarism(scan_id: int) -> Dict[str, Any]:
    scans = SYSTEM.storage.list_scans()
    scan = next((s for s in scans if int(s.get("id", 0)) == scan_id), None)
    if not scan:
        raise HTTPException(status_code=404, detail="Khong tim thay scan")

    report_json_path = str(scan.get("report_json_path", "") or "")
    if not report_json_path or not os.path.exists(report_json_path):
        return {"items": []}

    try:
        import json

        with open(report_json_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        sim = report.get("similarity_check", {})
        pairs = sim.get("near_duplicate_pairs", []) if isinstance(sim, dict) else []
        return {"items": pairs}
    except Exception:
        return {"items": []}


@app.get("/api/code-compare")
def compare_code(
    repo_a: str = Query(...),
    path_a: str = Query(...),
    repo_b: str = Query(...),
    path_b: str = Query(...),
    token: str = Query(default=""),
) -> Dict[str, Any]:
    github = GithubClient(token.strip() or None)

    _, branch_a, err_a = github.fetch_repo_tree(repo_a)
    _, branch_b, err_b = github.fetch_repo_tree(repo_b)
    if err_a or err_b:
        raise HTTPException(status_code=400, detail=f"Khong tai duoc repo tree: {err_a or ''} {err_b or ''}")

    code_a, ferr_a = github.fetch_file_content(repo_a, path_a, branch_a)
    code_b, ferr_b = github.fetch_file_content(repo_b, path_b, branch_b)
    if ferr_a or ferr_b:
        raise HTTPException(status_code=400, detail=f"Khong tai duoc file code: {ferr_a or ''} {ferr_b or ''}")

    return {
        "repo_a": repo_a,
        "path_a": path_a,
        "repo_b": repo_b,
        "path_b": path_b,
        "code_a": code_a or "",
        "code_b": code_b or "",
    }


@app.get("/api/scans/{scan_id}/dashboard")
def get_dashboard(scan_id: int) -> Dict[str, Any]:
    return SYSTEM.get_dashboard(scan_id)


@app.post("/api/scans/{scan_id}/chat")
def ask_chatbot(scan_id: int, payload: ChatPayload) -> Dict[str, str]:
    answer = SYSTEM.ask_chatbot(scan_id, payload.question)
    return {"answer": answer}


@app.post("/api/scans/{scan_id}/export-csv")
def export_scan_csv(scan_id: int, out_path: str) -> Dict[str, Any]:
    path = SYSTEM.export_scan_csv(scan_id, out_path)
    return {"path": path}


@app.post("/api/scans/{scan_id}/export-report")
def export_scan_report(scan_id: int, out_path: str) -> Dict[str, Any]:
    path = SYSTEM.export_scan_pdf_like(scan_id, out_path)
    return {"path": path}


# ---------- Automation ----------
@app.post("/api/auto-scan/start")
def start_auto_scan(payload: ScanSheetPayload, interval_minutes: int = 10, x_role: str | None = Header(default="admin")) -> Dict[str, Any]:
    require_role("admin", x_role)
    cfg = ScanConfig(
        section=payload.section,
        bai_range=payload.bai_range,
        assignment=payload.assignment,
        similarity_threshold=max(0.5, min(1.0, payload.similarity_threshold)),
        deadline_iso=payload.deadline_iso,
        token=payload.token.strip() or None,
    )
    msg = SYSTEM.start_auto_scan(payload.sheet_url, cfg, interval_minutes=interval_minutes)
    return {"message": msg}


@app.post("/api/auto-scan/stop")
def stop_auto_scan(x_role: str | None = Header(default="admin")) -> Dict[str, Any]:
    require_role("admin", x_role)
    msg = SYSTEM.stop_auto_scan()
    return {"message": msg}


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
