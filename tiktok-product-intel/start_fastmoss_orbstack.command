#!/bin/zsh
set -e

cd "/Users/jianing/Ning's Git/tiktok-product-intel"

PORT=8090
URL="http://localhost:${PORT}/FastMOSS-Report/"

echo "Starting FastMOSS report with OrbStack Docker..."
echo "URL: ${URL}"
echo

if command -v orb >/dev/null 2>&1; then
  orb start --all || true
fi

docker rm -f fastmoss-report >/dev/null 2>&1 || true
docker compose -f docker-compose.fastmoss.yml up -d --force-recreate

echo
docker ps -a --filter name=fastmoss-report
echo

python3 - <<'PY'
import time
import urllib.request
import webbrowser

url = "http://localhost:8090/FastMOSS-Report/"
for _ in range(20):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            print("Status:", response.status)
            webbrowser.open(url)
            break
    except Exception as exc:
        last = exc
        time.sleep(1)
else:
    print("Could not open report:", last)
    print("Container logs:")
PY

docker logs fastmoss-report 2>/dev/null || true

echo
read -k 1 "?Press any key to close..."
