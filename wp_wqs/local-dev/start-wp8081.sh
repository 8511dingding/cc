#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -e wp_wqs ]; then
  ln -s wordpress wp_wqs
fi

label="com.wp-wqs.php8081"
domain="gui/$(id -u)"
plist="$PWD/$label.plist"
pidfile="$PWD/$label.pid"
php_bin="/opt/homebrew/bin/php"

start_fallback_server() {
  if [ -f "$pidfile" ]; then
    old_pid="$(cat "$pidfile" 2>/dev/null || true)"
    if [ -n "${old_pid:-}" ] && kill -0 "$old_pid" >/dev/null 2>&1; then
      kill "$old_pid" >/dev/null 2>&1 || true
    fi
    rm -f "$pidfile"
  fi

  PHP_CLI_SERVER_WORKERS=4 "$php_bin" -S localhost:8081 -t "$PWD" "$PWD/router.php" >> "$PWD/php8081.log" 2>&1 &
  echo "$!" > "$pidfile"
  sleep 1

  if kill -0 "$(cat "$pidfile")" >/dev/null 2>&1; then
    echo "Started fallback PHP server on http://localhost:8081/wp_wqs/ (pid $(cat "$pidfile"))"
    exit 0
  fi

  echo "Fallback PHP server failed to start. See $PWD/php8081.log" >&2
  exit 1
}

if launchctl print "$domain/$label" >/dev/null 2>&1; then
  launchctl bootout "$domain/$label" >/dev/null 2>&1 || true
fi

if launchctl bootstrap "$domain" "$plist"; then
  launchctl kickstart -k "$domain/$label"
  launchctl print "$domain/$label" | sed -n '1,20p'
else
  echo "launchctl bootstrap failed; starting fallback PHP server." >&2
  start_fallback_server
fi
