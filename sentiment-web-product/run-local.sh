#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

DOCKER_BIN="${DOCKER_BIN:-}"
if [[ -z "$DOCKER_BIN" ]]; then
  if command -v docker >/dev/null 2>&1; then
    DOCKER_BIN="docker"
  elif [[ -x "$HOME/.orbstack/bin/docker" ]]; then
    DOCKER_BIN="$HOME/.orbstack/bin/docker"
  fi
fi

if [[ -z "$DOCKER_BIN" ]]; then
  echo "docker command not found."
  echo "Install OrbStack first: https://orbstack.dev/"
  echo "After OrbStack is running, re-run: ./run-local.sh"
  exit 1
fi

mkdir -p web_system/exports web_system/uploads

MODE="${1:-prod}"
if [[ "$MODE" != "prod" && "$MODE" != "dev" ]]; then
  echo "Unknown mode: $MODE"
  echo "Use: ./run-local.sh [prod|dev]"
  exit 1
fi

if [[ "$MODE" == "dev" ]]; then
  "$DOCKER_BIN" compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build --force-recreate sentiment-platform-api sentiment-platform-web local-portal
else
  "$DOCKER_BIN" compose up -d --build --force-recreate sentiment-platform-api sentiment-platform-web local-portal
fi

echo
echo "Local portal: http://localhost:8080/"
echo "Dynamic platform: http://localhost:8080/platform/"
echo "Platform API: http://localhost:8080/api/platform/dashboard"
if [[ "$MODE" == "dev" ]]; then
  echo "Frontend dev server: http://localhost:5173/platform/"
fi
