"""Launcher cho github_sheet_tool_lib."""

from pathlib import Path
import sys


# Allow running this file directly: python baitapclass/github_sheet_tool_lib/github_sheet_tool.py
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from github_sheet_tool_lib.core import main


if __name__ == "__main__":
    raise SystemExit(main())
