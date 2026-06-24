<?php
/**
 * Front-end performance guards for the local WQS site.
 *
 * @package WQS_Portfolio
 */

defined('ABSPATH') || exit;

/**
 * Keep admin-only plugins out of normal front-end requests.
 *
 * The plugins remain enabled in wp-admin, AJAX, REST, and cron contexts.
 *
 * @param array $plugins Active plugin basenames.
 * @return array
 */
function wqs_performance_filter_frontend_plugins($plugins)
{
    if (
        is_admin() ||
        wp_doing_ajax() ||
        wp_doing_cron() ||
        (defined('REST_REQUEST') && REST_REQUEST) ||
        (defined('WP_CLI') && WP_CLI)
    ) {
        return $plugins;
    }

    $frontend_skips = array(
        'term-management-tools/term-management-tools.php',
        'updraftplus/updraftplus.php',
        'wpvivid-backuprestore/wpvivid-backuprestore.php',
    );

    return array_values(array_diff($plugins, $frontend_skips));
}
add_filter('option_active_plugins', 'wqs_performance_filter_frontend_plugins');
