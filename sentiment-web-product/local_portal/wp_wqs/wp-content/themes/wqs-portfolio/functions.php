<?php
/**
 * Theme functions and definitions
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

// Theme version
if (!defined('_S_VERSION')) {
    define('_S_VERSION', '1.0.0');
}

// Required files
require get_template_directory() . '/inc/post-types.php';
require get_template_directory() . '/inc/template-tags.php';
require get_template_directory() . '/inc/template-functions.php';
require get_template_directory() . '/inc/customizer.php';

/**
 * Sets up theme defaults and registers support for various WordPress features.
 */
function wqs_setup()
{
    load_theme_textdomain('wqs-portfolio', get_template_directory() . '/languages');

    add_theme_support('automatic-feed-links');
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');

    register_nav_menus(array(
        'primary' => __('Primary Menu', 'wqs-portfolio'),
        'footer' => __('Footer Menu', 'wqs-portfolio'),
    ));

    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ));

    add_theme_support('customize-selective-refresh-widgets');

    // Custom image sizes
    add_image_size('works-thumb', 600, 450, true);
    add_image_size('works-full', 1200, 900, false);
}
add_action('after_setup_theme', 'wqs_setup');

/**
 * Register widget areas.
 */
function wqs_widgets_init()
{
    register_sidebar(array(
        'name' => __('Sidebar', 'wqs-portfolio'),
        'id' => 'sidebar-1',
        'description' => __('Add widgets here.', 'wqs-portfolio'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget' => '</section>',
        'before_title' => '<h2 class="widget-title">',
        'after_title' => '</h2>',
    ));
}
add_action('widgets_init', 'wqs_widgets_init');

/**
 * Enqueue scripts and styles.
 */
function wqs_scripts()
{
    // Main stylesheet
    wp_enqueue_style('wqs-portfolio-style', get_stylesheet_uri(), array(), _S_VERSION);

    // Google Fonts - Playfair Display + Inter
    wp_enqueue_style('wqs-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&family=Playfair+Display:wght@400;500;600&display=swap', array(), null);

    // AOS (Animate On Scroll) CSS
    wp_enqueue_style('aos-css', 'https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.min.css', array(), '2.3.4');

    // PhotoSwipe CSS
    wp_enqueue_style('photoswipe', 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe.min.css', array(), '5.4.4');

    // Navigation script
    wp_enqueue_script('wqs-navigation', get_template_directory_uri() . '/js/navigation.js', array(), _S_VERSION, true);

    // PhotoSwipe JS
    wp_enqueue_script('photoswipe', 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/umd/photoswipe.min.js', array(), '5.4.4', true);
    wp_enqueue_script('photoswipe-ui', 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/umd/photoswipe-lightbox.min.js', array('photoswipe'), '5.4.4', true);

    // AOS JS
    wp_enqueue_script('aos-js', 'https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.min.js', array(), '2.3.4', true);

    // Main scripts
    wp_enqueue_script('wqs-portfolio-scripts', get_template_directory_uri() . '/js/main.js', array('jquery'), _S_VERSION, true);

    // Pass AJAX URL to JS
    wp_localize_script('wqs-portfolio-scripts', 'wqsData', array(
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'currentLang' => wqs_get_current_language(),
    ));

    if (is_singular() && comments_open() && get_option('thread_comments')) {
        wp_enqueue_script('comment-reply');
    }
}
add_action('wp_enqueue_scripts', 'wqs_scripts');

/**
 * Polylang Integration - Register strings for translation.
 */
function wqs_pll_register_strings()
{
    if (function_exists('pll_register_string')) {
        pll_register_string('site-title', 'Wang Qingsong');
        pll_register_string('works-title', 'Works');
        pll_register_string('menu-works', '作品');
        pll_register_string('menu-exhibition', '展览');
        pll_register_string('menu-review', '评论');
        pll_register_string('menu-bts', '工作照');
    }
}
add_action('pll_init', 'wqs_pll_register_strings');