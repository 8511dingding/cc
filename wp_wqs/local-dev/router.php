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

// 去掉 /wp_wqs 前缀，获取 WordPress 内部路径
$remainingPath = substr($path, strlen('/wp_wqs'));
if ($remainingPath === '' || $remainingPath === false) {
    $remainingPath = '/';
}

$file = __DIR__ . $remainingPath;

if (is_file($file)) {
    return false;
}

if (is_dir($file) && is_file(rtrim($file, '/') . '/index.php')) {
    $index_path = rtrim($remainingPath, '/') . '/index.php';
    $_SERVER['SCRIPT_NAME'] = '/wp_wqs' . $index_path;
    $_SERVER['PHP_SELF'] = '/wp_wqs' . $index_path;
    $_SERVER['SCRIPT_FILENAME'] = rtrim($file, '/') . '/index.php';

    require $_SERVER['SCRIPT_FILENAME'];
    return true;
}

// 清除 PATH_INFO，避免干扰 WordPress 的 URL 解析
unset($_SERVER['PATH_INFO']);

// WordPress 需要看到相对路径作为 REQUEST_URI
$_SERVER['SCRIPT_NAME'] = '/wp_wqs/index.php';
$_SERVER['PHP_SELF'] = '/wp_wqs/index.php';
$_SERVER['SCRIPT_FILENAME'] = __DIR__ . '/wp_wqs/index.php';
$_SERVER['REQUEST_URI'] = $remainingPath;

require __DIR__ . '/wp_wqs/index.php';
return true;
