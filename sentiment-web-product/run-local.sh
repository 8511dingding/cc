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

"$DOCKER_BIN" compose up --build
