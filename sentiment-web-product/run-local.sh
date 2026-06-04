#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker command not found."
  echo "Install OrbStack first: https://orbstack.dev/"
  echo "After OrbStack is running, re-run: ./run-local.sh"
  exit 1
fi

mkdir -p web_system/exports web_system/uploads

docker compose up --build
