<?php
/**
 * WordPress Configuration Template
 *
 * 此文件使用占位符，部署时由 deploy.sh 替换为实际值。
 * 不要直接提交包含真实密码的 wp-config.php 到 Git。
 *
 * @usage ./deploy.sh
 */

// ============================================
// 数据库配置 - 部署时替换
// ============================================
define( 'DB_NAME', '__DB_NAME__' );
define( 'DB_USER', '__DB_USER__' );
define( 'DB_PASSWORD', '__DB_PASSWORD__' );
define( 'DB_HOST', '__DB_HOST__' );
define( 'DB_CHARSET', 'utf8mb4' );
define( 'DB_COLLATE', '' );

// ============================================
// 调试设置
// ============================================
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);

define('WP_ENVIRONMENT_TYPE', 'production');
define('DISABLE_WP_CRON', true);

@ini_set('log_errors','1');
@ini_set('display_errors','0');
error_reporting(E_ALL ^ E_NOTICE ^ E_DEPRECATED);

// ============================================
// WordPress URL 配置 - 部署时替换
// ============================================
define('WP_HOME', '__WP_HOME__' );
define('WP_SITEURL', '__WP_SITEURL__' );

$table_prefix = 'wp_';

// ============================================
// 内容目录配置 - 部署时替换
// ============================================
define( 'WP_CONTENT_DIR', __DIR__ . '/wp-content' );
define( 'WP_CONTENT_URL', '__WP_CONTENT_URL__' );

// ============================================
// 高级缓存（如果有）
// ============================================
// define( 'WP_CACHE', true );

// ============================================
// 密钥（建议在服务器上手动设置）
// ============================================
define('AUTH_KEY',         'put your unique phrase here');
define('SECURE_AUTH_KEY',  'put your unique phrase here');
define('LOGGED_IN_KEY',    'put your unique phrase here');
define('NONCE_KEY',        'put your unique phrase here');
define('AUTH_SALT',        'put your unique phrase here');
define('SECURE_AUTH_SALT', 'put your unique phrase here');
define('LOGGED_IN_SALT',   'put your unique phrase here');
define('NONCE_SALT',       'put your unique phrase here');

// ============================================
// 自动加载和启动
// ============================================
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

require_once ABSPATH . 'wp-settings.php';
