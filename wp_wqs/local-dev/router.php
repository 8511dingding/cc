<?php
/**
 * Router for PHP's built-in server.
 *
 * The local WordPress site is exposed as /wp_wqs while the real files live in
 * local-dev/wordpress. Existing static files are served by the built-in server;
 * all WordPress routes fall back to /wp_wqs/index.php.
 */

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?: '/';

if ($path === '/wp_wqs') {
    header('Location: /wp_wqs/');
    return true;
}

if (strpos($path, '/wp_wqs/') !== 0) {
    return false;
}

$file = __DIR__ . $path;

if (is_file($file)) {
    return false;
}

$_SERVER['SCRIPT_NAME'] = '/wp_wqs/index.php';
$_SERVER['PHP_SELF'] = '/wp_wqs/index.php';
$_SERVER['SCRIPT_FILENAME'] = __DIR__ . '/wp_wqs/index.php';

require __DIR__ . '/wp_wqs/index.php';
return true;
