#!/usr/bin/env python3
"""
Serve the deployed FastMOSS report from the project-owned OrbStack host folder.

After starting this script, open:
http://localhost:8080/FastMOSS-Report/
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os


HOST = "127.0.0.1"
PORT = 8080
ROOT = Path(__file__).resolve().parents[1] / "orbstack-www" / "ning_mac"


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Report root does not exist: {ROOT}")

    os.chdir(ROOT)
    server = ThreadingHTTPServer((HOST, PORT), SimpleHTTPRequestHandler)
    print(f"Serving {ROOT}")
    print(f"Open http://localhost:{PORT}/FastMOSS-Report/")
    server.serve_forever()


if __name__ == "__main__":
    main()
