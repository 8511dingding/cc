<?php
/**
 * Rewrite maintenance.
 *
 * Site content is stored as standard posts with categories and Polylang
 * translations. Legacy custom post types were removed from this theme.
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

function wqs_rewrite_flush()
{
    flush_rewrite_rules();
}
add_action('after_switch_theme', 'wqs_rewrite_flush');
