#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"

echo "Starting OrbStack..."
if command -v orb >/dev/null 2>&1; then
  orb start >/dev/null 2>&1 || true
fi

echo "Waiting for Docker..."
for i in {1..60}; do
  if docker info >/dev/null 2>&1; then
    break
  fi
  sleep 2
  if [[ "$i" == "60" ]]; then
    echo "Docker is still unavailable. Please open OrbStack and allow any permission prompts, then run this file again."
    exit 1
  fi
done

MODE="${1:-prod}"
if [[ "$MODE" != "prod" && "$MODE" != "dev" ]]; then
  echo "Unknown mode: $MODE"
  echo "Use: ./start-platform-orbstack.command [prod|dev]"
  exit 1
fi

echo "Starting dynamic sentiment platform (${MODE})..."
if [[ "$MODE" == "dev" ]]; then
  docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build --force-recreate sentiment-platform-api sentiment-platform-web local-portal
else
  docker compose up -d --build --force-recreate sentiment-platform-api sentiment-platform-web local-portal
fi

echo
echo "Done."
echo "Local portal: http://localhost:8080/"
echo "Dynamic platform: http://localhost:8080/platform/"
echo "Platform API: http://localhost:8080/api/platform/dashboard"
if [[ "$MODE" == "dev" ]]; then
  echo "Frontend dev server: http://localhost:5173/platform/"
fi
echo
read -r "REPLY?Press Enter to close..."
