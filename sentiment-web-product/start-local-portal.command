#!/bin/zsh
cd "$(dirname "$0")"
export PORT="${PORT:-8090}"
export HOST="${HOST:-127.0.0.1}"
node tools/local-portal-server.mjs
