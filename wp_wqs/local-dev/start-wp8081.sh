#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -e wp_wqs ]; then
  ln -s wordpress wp_wqs
fi

label="com.wp-wqs.php8081"
domain="gui/$(id -u)"
plist="$PWD/$label.plist"

if launchctl print "$domain/$label" >/dev/null 2>&1; then
  launchctl bootout "$domain/$label" >/dev/null 2>&1 || true
fi

launchctl bootstrap "$domain" "$plist"
launchctl kickstart -k "$domain/$label"
launchctl print "$domain/$label" | sed -n '1,20p'
