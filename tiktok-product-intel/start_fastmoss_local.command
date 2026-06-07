#!/bin/zsh
set -e

cd "/Users/jianing/Ning's Git/tiktok-product-intel"

PORT=8091
ROOT="orbstack-www/ning_mac"
URL="http://localhost:${PORT}/FastMOSS-Report/"

echo "Starting FastMOSS report without Docker..."
echo "Root: $(pwd)/${ROOT}"
echo "URL:  ${URL}"
echo

if [ ! -f "${ROOT}/FastMOSS-Report/index.html" ]; then
  echo "Report files were not found:"
  echo "$(pwd)/${ROOT}/FastMOSS-Report/index.html"
  read -k 1 "?Press any key to close..."
  exit 1
fi

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

url = "http://localhost:8091/FastMOSS-Report/"
for _ in range(20):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            print("Status:", response.status)
            webbrowser.open(url)
            break
    except Exception as exc:
        last = exc
        time.sleep(0.5)
else:
    print("Could not open report:", last)
PY

echo
echo "Keep this window open while viewing the report."
echo "Press Ctrl+C to stop."
wait "${SERVER_PID}"
