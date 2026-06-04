#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/sentiment-web-product}"
APP_PORT="${APP_PORT:-8501}"

echo "Tencent Cloud Docker deploy helper"
echo "Target app dir: ${APP_DIR}"
echo
echo "Run these commands on the Tencent Cloud server:"
echo
cat <<EOF
sudo mkdir -p ${APP_DIR}
sudo chown -R \$USER:\$USER ${APP_DIR}

# Upload this project folder to ${APP_DIR}, then:
cd ${APP_DIR}
docker compose up -d --build

# Verify:
docker compose ps
curl -I http://127.0.0.1:${APP_PORT}/
EOF
echo
echo "Nginx can reverse proxy to http://127.0.0.1:${APP_PORT}/ after the container is healthy."
