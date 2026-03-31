from __future__ import annotations

from typing import Any, Dict, List

from github_sheet_tool_lib.core import load_sheet_rows


class GoogleSheetService:
    def load_rows(self, sheet_url: str) -> List[Dict[str, Any]]:
        return load_sheet_rows(sheet_url)
