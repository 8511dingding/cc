#!/bin/zsh
set -e

cd "/Users/jianing/Ning's Git/tiktok-product-intel"

echo "Starting FastMOSS report from local project folder..."
echo

PORT=8090
ROOT="orbstack-www/ning_mac"
URL="http://localhost:${PORT}/FastMOSS-Report/"

if [ ! -f "${ROOT}/FastMOSS-Report/index.html" ]; then
  echo "Report files were not found:"
  echo "$(pwd)/${ROOT}/FastMOSS-Report/index.html"
  read -k 1 "?Press any key to close..."
  exit 1
fi

if lsof -nP -iTCP:${PORT} -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port ${PORT} is already in use. Existing listener:"
  lsof -nP -iTCP:${PORT} -sTCP:LISTEN
  echo
  echo "Please stop the existing process or use start_fastmoss_local.command."
  read -k 1 "?Press any key to close..."
  exit 1
fi

echo
echo "FastMOSS report is starting:"
echo "${URL}"
echo

python3 -m http.server "${PORT}" --bind 127.0.0.1 --directory "${ROOT}" &
SERVER_PID=$!

cleanup() {
  kill "${SERVER_PID}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

python3 - <<'PY'
import time
import urllib.request
import webbrowser

url = "http://localhost:8090/FastMOSS-Report/"
for _ in range(20):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status < 500:
                webbrowser.open(url)
                print("Opened report in browser.")
                break
    except Exception:
        time.sleep(1)
else:
    print("The report did not respond yet. Keep this window open and try the URL above again.")
PY

echo
echo "Keep this window open while viewing the report."
echo "Press Ctrl+C to stop."
wait "${SERVER_PID}"
