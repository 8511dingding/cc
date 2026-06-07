#!/bin/zsh
set -e

cd "/Users/jianing/Ning's Git/tiktok-product-intel"

echo "Starting FastMOSS report with OrbStack..."
echo

if command -v orb >/dev/null 2>&1; then
  echo "Checking OrbStack..."
  orb start --all || true
  echo
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker command was not found. Please start or reinstall OrbStack first."
  read -k 1 "?Press any key to close..."
  exit 1
fi

docker compose -f docker-compose.fastmoss.yml down
docker compose -f docker-compose.fastmoss.yml up -d

echo
echo "FastMOSS report is starting:"
echo "http://localhost:8080/FastMOSS-Report/"
echo

python3 - <<'PY'
import time
import urllib.request
import webbrowser

url = "http://localhost:8080/FastMOSS-Report/"
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
read -k 1 "?Press any key to close..."
