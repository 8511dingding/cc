<?php
/**
 * Front page template dispatcher.
 *
 * @package WQS_Portfolio
 */

get_header();

$template = wqs_get_homepage_template();
$template_file = get_template_directory() . '/template-parts/home/home-' . $template . '.php';

if (!is_file($template_file)) {
    $template_file = get_template_directory() . '/template-parts/home/home-museum-ribbon.php';
}

include $template_file;

get_footer();
