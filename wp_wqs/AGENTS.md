# Project Instructions

## Project Shape

This is a WordPress migration workspace, not a typical application repo with a package manager build. The active local site is served by ServBay from `/Applications/ServBay/www/wqs_2026`; the repository contains migration assets, old-site data, scripts, and a WordPress snapshot.

## Local Runtime

- Local URL: `http://wp_wqs.local/`
- Migrated dev URL: `http://localhost:8081/wp_wqs/`
- Database: MySQL on `127.0.0.1:3307`
- Active WordPress root: `/Applications/ServBay/www/wqs_2026`
- Active Nginx vhost: `/Applications/ServBay/etc/nginx/vhosts/wp_wqs.localhost.conf`
- Repository WordPress snapshot: `local-dev/wordpress/`

When debugging the running site, inspect the ServBay paths above first. Changes made only under `local-dev/wordpress/` will not affect the currently served site unless manually synced.

For the migrated development copy, inspect `local-dev/wordpress/` and run:

```bash
./local-dev/start-wp8081.sh
```

This loads `local-dev/com.wp-wqs.php8081.plist`, starts PHP's built-in server on `localhost:8081`, and serves `local-dev/wp_wqs` through `local-dev/router.php`.

## Code Style

- Migration scripts are plain PHP with direct PDO/MySQL access.
- Keep scripts narrow and task-specific; most files in `migration-scripts/` are one-off repair or verification scripts.
- Avoid broad string replacement in serialized WordPress options. Prefer targeted SQL updates, WordPress-aware tools, or deleting safe transient caches.

## Verification

Use HTTP checks first:

```bash
curl -I http://wp_wqs.local/
curl -I http://localhost/
curl -I http://127.0.0.1/
```

Expected:

- `wp_wqs.local` returns `200 OK`.
- `localhost` redirects to `wp_wqs.local`.
- `127.0.0.1` redirects to `wp_wqs.local`.

Check services:

```bash
lsof -nP -iTCP:80 -sTCP:LISTEN
lsof -nP -iTCP:3307 -sTCP:LISTEN
```

## WordPress URL Rules

Keep these options aligned:

```sql
SELECT option_name, option_value
FROM wp_options
WHERE option_name IN ('home', 'siteurl');
```

Both should be `http://wp_wqs.local`.

If old `localhost:8081` links reappear in language links, check Polylang transients first:

```sql
SELECT option_name
FROM wp_options
WHERE option_value LIKE '%localhost:8081%';
```

Deleting stale `_transient_*` rows is safer than replacing serialized option data by hand.
