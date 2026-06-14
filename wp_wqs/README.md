# wp_wqs

Local migration workspace for Wang Qingsong's website. The repository keeps the old Joomla export, WordPress migration scripts, database dumps, and a local WordPress code snapshot. The live local site is currently served by ServBay from `/Applications/ServBay/www/wqs_2026`.

## Current Local Site

- Primary URL: `http://wp_wqs.local/`
- Also works: `http://localhost/` and `http://127.0.0.1/`, both redirect to `http://wp_wqs.local/`
- WordPress root used by ServBay: `/Applications/ServBay/www/wqs_2026`
- Database: `wqs_wordpress`
- MySQL host: `127.0.0.1:3307`
- Web server: ServBay Nginx
- PHP: ServBay PHP-FPM

Do not use `https://wp_wqs.local/` unless an SSL vhost is added. The current local binding is HTTP.

## OrbStack / PHP 8081 Development Site

The migrated development copy under `local-dev/wordpress` is exposed at:

```text
http://localhost:8081/wp_wqs/
```

It is served by PHP's built-in server through a user LaunchAgent:

```text
local-dev/com.wp-wqs.php8081.plist
```

Start or restart it with:

```bash
./local-dev/start-wp8081.sh
```

Runtime files:

- Web root for the PHP server: `local-dev`
- URL entry symlink: `local-dev/wp_wqs -> wordpress`
- Router for WordPress permalinks: `local-dev/router.php`
- Log file: `local-dev/php8081.log`
- PID file may be created by older manual starts: `local-dev/php8081.pid`

The development copy uses `local-dev/wordpress/wp-config.php` with:

```php
define('WP_HOME', 'http://localhost:8081/wp_wqs');
define('WP_SITEURL', 'http://localhost:8081/wp_wqs');
define('WP_CONTENT_URL', 'http://localhost:8081/wp_wqs/wp-content');
```

Useful checks:

```bash
lsof -nP -iTCP:8081 -sTCP:LISTEN
curl -I http://localhost:8081/wp_wqs/
tail -f local-dev/php8081.log
```

As of 2026-06-13, the homepage and WordPress REST/AJAX endpoints return successfully. The archive page may show `0 项结果` because the database currently has no published posts with the custom post types `artwork`, `exhibition`, or `shooting`; existing content is mostly stored as ordinary `post` records.

## Repository Map

- `database-export/` - SQL exports of the legacy database.
- `old-site/` - old Joomla site files and database export.
- `local-dev/wordpress/` - downloaded WordPress code snapshot used during migration work.
- `migration-scripts/` - one-off PHP scripts for Joomla to WordPress migration, media import, Polylang linking, navigation fixes, and verification checks.
- `media-backup/` - placeholder for backed-up media assets.

## Runtime Notes

The repository is not the active document root. ServBay serves this site from:

```text
/Applications/ServBay/www/wqs_2026
```

The active WordPress config is:

```text
/Applications/ServBay/www/wqs_2026/wp-config.php
```

The active Nginx vhost is:

```text
/Applications/ServBay/etc/nginx/vhosts/wp_wqs.localhost.conf
```

The vhost should include:

```nginx
listen 80;
listen [::]:80;
server_name localhost wp_wqs.local 127.0.0.1;
```

## Useful Checks

```bash
curl -I http://wp_wqs.local/
curl -I http://localhost/
curl -I http://127.0.0.1/
lsof -nP -iTCP:80 -sTCP:LISTEN
lsof -nP -iTCP:3307 -sTCP:LISTEN
```

WordPress URL options should be:

```sql
SELECT option_name, option_value
FROM wp_options
WHERE option_name IN ('home', 'siteurl');
```

Expected values:

```text
home    http://wp_wqs.local
siteurl http://wp_wqs.local
```

## Debug Log

On 2026-06-04, the local homepage issue was traced to multiple entry points resolving to different Nginx vhosts:

- `http://wp_wqs.local/` returned the WordPress homepage.
- `http://localhost/` used IPv6 `::1` and hit another vhost, returning 403.
- `http://127.0.0.1/` hit the ServBay default page.
- `http://2026.wangqingsong.com/` redirected to an old `localhost:8081` value through stale Polylang cache.

Fixes applied:

- WordPress `home` and `siteurl` are set to `http://wp_wqs.local`.
- Deleted stale `_transient_pll_languages_list` cache containing `localhost:8081`.
- Updated the Nginx vhost to listen on IPv6 and include `127.0.0.1`.
- Reloaded the running Nginx master process.

After the fix:

- `http://wp_wqs.local/` returns `200 OK`.
- `http://localhost/` redirects to `http://wp_wqs.local/`.
- `http://127.0.0.1/` redirects to `http://wp_wqs.local/`.
