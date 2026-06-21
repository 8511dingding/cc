# Project Instructions

## Project Shape

This is the active local WordPress workspace for Wang Qingsong's website. The
running site uses the WordPress files in this repository; it is no longer
served by ServBay.

## Current Local Runtime

- Site URL: `http://localhost:8081/wp_wqs/`
- Active WordPress root: `local-dev/wordpress/`
- URL entry symlink: `local-dev/wp_wqs -> wordpress`
- PHP router: `local-dev/router.php`
- Start script: `local-dev/start-wp8081.sh`
- PHP server workers: `4`
- Database: `wqs_wordpress`
- MySQL host: `127.0.0.1:3306`
- MySQL provider: OrbStack
- Active theme: `local-dev/wordpress/wp-content/themes/wqs-portfolio/`

ServBay, `/Applications/ServBay/www/wqs_2026`, `wp_wqs.local`, port 80, and
MySQL port 3307 are retired historical configurations. Do not inspect, modify,
deploy to, or verify against them unless the user explicitly asks about old
environment history.

Start or restart the current site with:

```bash
./local-dev/start-wp8081.sh
```

This starts PHP's built-in server on `localhost:8081` and serves
`local-dev/wp_wqs` through `local-dev/router.php`. The local configuration
disables request-triggered WP-Cron because loopback cron calls can deadlock a
PHP development server. Run `wp-cron.php` manually only when a scheduled local
task is explicitly needed.

## Code Style

- Migration scripts are plain PHP with direct PDO/MySQL access.
- Keep scripts narrow and task-specific; most files in `migration-scripts/`
  are one-off repair or verification scripts.
- Avoid broad string replacement in serialized WordPress options. Prefer
  targeted SQL updates, WordPress-aware tools, or deleting safe transient
  caches.
- Site-specific editor behavior should live in the theme or an MU plugin, not
  in third-party plugin core files.

## Verification

Use the current HTTP endpoint first:

```bash
curl -I http://localhost:8081/wp_wqs/
lsof -nP -iTCP:8081 -sTCP:LISTEN
lsof -nP -iTCP:3306 -sTCP:LISTEN
```

Expected:

- `http://localhost:8081/wp_wqs/` returns `200 OK`.
- PHP listens on port `8081`.
- OrbStack MySQL is reachable on `127.0.0.1:3306`.

## WordPress URL Rules

The constants in `local-dev/wordpress/wp-config.php` are authoritative:

```php
define('WP_HOME', 'http://localhost:8081/wp_wqs');
define('WP_SITEURL', 'http://localhost:8081/wp_wqs');
define('WP_CONTENT_URL', 'http://localhost:8081/wp_wqs/wp-content');
```

If language links contain another host or port, inspect Polylang transients and
serialized options carefully. Do not replace serialized option data by hand.
