from __future__ import annotations

import os
import socket
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))


def main() -> int:
    try:
        import uvicorn
    except Exception as e:
        print("Chua co uvicorn. Cai bang: pip install uvicorn fastapi")
        print(f"Chi tiet: {e}")
        return 1

    host = os.getenv("SMART_CHECKER_HOST", "127.0.0.1")
    port = int(os.getenv("SMART_CHECKER_PORT", "8088"))

    # If the default port is already bound, treat it as an already-running server.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        if sock.connect_ex((host, port)) == 0:
            print(f"Server da dang chay tai http://{host}:{port}")
            return 0

    uvicorn.run("github_sheet_tool_lib.web.app:app", host=host, port=port, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
