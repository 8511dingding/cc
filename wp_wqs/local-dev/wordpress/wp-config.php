<?php
/**
 * WordPress Configuration
 * Local development setup
 */

define( 'DB_NAME', 'wqs_wordpress' );
define( 'DB_USER', 'root' );
define( 'DB_PASSWORD', 'GM3750-jm' );
define( 'DB_HOST', '127.0.0.1:3306' );
define( 'DB_CHARSET', 'utf8mb4' );
define( 'DB_COLLATE', '' );

define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);

@ini_set('log_errors','1');
@ini_set('display_errors','0');
error_reporting(E_ALL ^ E_NOTICE ^ E_DEPRECATED);

define('WP_HOME', 'http://localhost:8081/wp_wqs');
define('WP_SITEURL', 'http://localhost:8081/wp_wqs');

$table_prefix = 'wp_';

define( 'WP_CONTENT_DIR', __DIR__ . '/wp-content' );
define( 'WP_CONTENT_URL', 'http://localhost:8081/wp_wqs/wp-content' );

if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

require_once ABSPATH . 'wp-settings.php';
