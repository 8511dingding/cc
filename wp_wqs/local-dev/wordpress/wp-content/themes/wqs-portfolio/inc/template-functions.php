<?php
/**
 * Template Functions
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Adds custom classes to the array of body classes.
 */
function wqs_body_classes($classes)
{
    if (is_singular('works')) {
        $classes[] = 'single-works';
    }

    if (is_post_type_archive('works')) {
        $classes[] = 'archive-works';
    }

    // Adds a class of hfeed to non-singular pages.
    if (!is_singular()) {
        $classes[] = 'hfeed';
    }

    // Adds a class of no-sidebar when there is no sidebar present.
    if (!is_active_sidebar('sidebar-1')) {
        $classes[] = 'no-sidebar';
    }

    return $classes;
}
add_filter('body_class', 'wqs_body_classes');

/**
 * Add a pingback url auto-discovery header for single posts.
 */
function wqs_pingback_header()
{
    if (is_singular()) {
        echo '<link rel="pingback" href="' . esc_url(get_bloginfo('pingback_url')) . '">';
    }
}
add_action('wp_head', 'wqs_pingback_header');

/**
 * Get current language slug.
 */
function wqs_get_current_language()
{
    if (function_exists('pll_current_language')) {
        return pll_current_language('slug');
    }
    return 'en';
}

/**
 * Get translated post ID.
 */
function wqs_get_translated_post($post_id, $lang = null)
{
    if (!function_exists('pll_get_post')) {
        return $post_id;
    }
    if ($lang === null) {
        $lang = wqs_get_current_language();
    }
    return pll_get_post($post_id, $lang);
}

/**
 * Modify main query for works archive.
 */
function wqs_modify_main_query($query)
{
    if (!is_admin() && $query->is_main_query()) {
        if (is_post_type_archive('works')) {
            $query->set('posts_per_page', 12);
            $query->set('orderby', 'date');
            $query->set('order', 'DESC');
        }
    }
}
add_action('pre_get_posts', 'wqs_modify_main_query');

/**
 * Add custom image sizes to Media Library.
 */
function wqs_custom_image_sizes($sizes)
{
    $custom_sizes = array(
        'works-thumb' => __('作品缩略图', 'wqs-portfolio'),
        'works-full' => __('作品完整图', 'wqs-portfolio'),
    );
    return array_merge($sizes, $custom_sizes);
}
add_filter('image_size_names_choose', 'wqs_custom_image_sizes');