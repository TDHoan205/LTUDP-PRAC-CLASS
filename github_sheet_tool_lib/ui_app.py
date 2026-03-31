from __future__ import annotations

# Legacy compatibility wrapper. Desktop Tk UI was moved to web/legacy/ui_app.py.
from github_sheet_tool_lib.web.legacy.ui_app import main


if __name__ == "__main__":
    raise SystemExit(main())
