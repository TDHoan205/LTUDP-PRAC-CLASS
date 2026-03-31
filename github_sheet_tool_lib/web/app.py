from __future__ import annotations

import os
from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from github_sheet_tool_lib.smart_api import app


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

if not any(getattr(route, "path", "") == "/static" for route in app.routes):
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request) -> HTMLResponse:
    data = {
        "total": 0,
        "submitted": 0,
        "late": 0,
        "missing": 0,
        "default_section": "2.3",
        "default_refresh": int(os.getenv("SMART_DASHBOARD_REFRESH_MIN", "10")),
    }
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"data": data},
    )
