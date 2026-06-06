#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

ok() {
  printf "[OK] %s\n" "$1"
}

warn() {
  printf "[WARN] %s\n" "$1"
}

fail() {
  printf "[FAIL] %s\n" "$1"
}

echo "Sentiment platform environment doctor"
echo

if command -v orb >/dev/null 2>&1; then
  ORB_STATUS="$(orb status 2>/dev/null || true)"
  if [[ "$ORB_STATUS" == "Running" ]]; then
    ok "OrbStack is running"
  else
    warn "OrbStack status is '${ORB_STATUS:-unknown}'. Open OrbStack or run: orb start"
  fi
else
  warn "orb command not found. Install OrbStack or make sure /usr/local/bin is in PATH."
fi

if docker info >/dev/null 2>&1; then
  ok "Docker API is reachable"
else
  fail "Docker API is not reachable. Start OrbStack first."
fi

if docker compose config >/dev/null 2>&1; then
  ok "docker-compose.yml is valid"
else
  fail "docker-compose.yml is not valid"
fi

if curl -fsS --max-time 5 http://localhost:8080/platform/ >/dev/null 2>&1; then
  ok "Frontend responds at http://localhost:8080/platform/"
else
  warn "Frontend is not responding at http://localhost:8080/platform/"
fi

if curl -fsS --max-time 5 http://localhost:8080/api/platform/dashboard >/dev/null 2>&1; then
  ok "API responds at http://localhost:8080/api/platform/dashboard"
else
  warn "API is not responding at http://localhost:8080/api/platform/dashboard"
fi

echo
echo "Recommended start command:"
echo "  make platform-up"
