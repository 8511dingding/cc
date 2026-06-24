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
require get_template_directory() . '/inc/admin/archive-settings.php';
require get_template_directory() . '/inc/homepage.php';
require get_template_directory() . '/inc/social-sharing.php';
require get_template_directory() . '/inc/footer-settings.php';

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
 * Remove WordPress emoji assets from the front end.
 */
function wqs_disable_emoji_assets()
{
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('wp_print_styles', 'print_emoji_styles');
    remove_action('admin_print_scripts', 'print_emoji_detection_script');
    remove_action('admin_print_styles', 'print_emoji_styles');
    remove_filter('the_content_feed', 'wp_staticize_emoji');
    remove_filter('comment_text_rss', 'wp_staticize_emoji');
    remove_filter('wp_mail', 'wp_staticize_emoji_for_email');
}
add_action('init', 'wqs_disable_emoji_assets');

/**
 * Enqueue scripts and styles.
 */
function wqs_scripts()
{
    // Main stylesheet
    $stylesheet_path = get_stylesheet_directory() . '/style.css';
    $stylesheet_version = is_file($stylesheet_path) ? (string) filemtime($stylesheet_path) : _S_VERSION;
    wp_enqueue_style('wqs-portfolio-style', get_stylesheet_uri(), array(), $stylesheet_version);

    // Google Fonts - Playfair Display + Inter
    wp_enqueue_style('wqs-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&family=Playfair+Display:wght@400;500;600&display=swap', array(), null);

    $uses_aos = !is_front_page();

    if ($uses_aos) {
        wp_enqueue_style('aos-css', 'https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.min.css', array(), '2.3.4');
    }

    // Navigation script
    $navigation_path = get_template_directory() . '/js/navigation.js';
    wp_enqueue_script(
        'wqs-navigation',
        get_template_directory_uri() . '/js/navigation.js',
        array(),
        is_file($navigation_path) ? (string) filemtime($navigation_path) : _S_VERSION,
        true
    );
    wp_script_add_data('wqs-navigation', 'strategy', 'defer');

    if ($uses_aos) {
        wp_enqueue_script('aos-js', 'https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.min.js', array(), '2.3.4', true);
        wp_script_add_data('aos-js', 'strategy', 'defer');
    }

    // Main scripts
    $main_script_path = get_template_directory() . '/js/main.js';
    wp_enqueue_script(
        'wqs-portfolio-scripts',
        get_template_directory_uri() . '/js/main.js',
        array(),
        is_file($main_script_path) ? (string) filemtime($main_script_path) : _S_VERSION,
        true
    );
    wp_script_add_data('wqs-portfolio-scripts', 'strategy', 'defer');

    if (function_exists('wqs_should_load_social_assets') && wqs_should_load_social_assets()) {
        $social_css = get_template_directory() . '/assets/css/social-sharing.css';
        $social_js = get_template_directory() . '/assets/js/social-sharing.js';

        wp_enqueue_style(
            'font-awesome-core',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/fontawesome.min.css',
            array(),
            '6.7.2'
        );
        wp_enqueue_style(
            'font-awesome-brands',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/brands.min.css',
            array('font-awesome-core'),
            '6.7.2'
        );
        wp_enqueue_style(
            'wqs-social-sharing',
            get_template_directory_uri() . '/assets/css/social-sharing.css',
            array('wqs-portfolio-style', 'font-awesome-brands'),
            is_file($social_css) ? (string) filemtime($social_css) : _S_VERSION
        );

        if (is_singular()) {
            wp_enqueue_script(
                'wqs-qrcode',
                'https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js',
                array(),
                '1.0.0',
                true
            );
            wp_script_add_data('wqs-qrcode', 'strategy', 'defer');
            wp_enqueue_script(
                'wqs-social-sharing',
                get_template_directory_uri() . '/assets/js/social-sharing.js',
                array('wqs-qrcode'),
                is_file($social_js) ? (string) filemtime($social_js) : _S_VERSION,
                true
            );
            wp_script_add_data('wqs-social-sharing', 'strategy', 'defer');
        }
    }

    $site_template = function_exists('wqs_get_homepage_template') ? wqs_get_homepage_template() : 'museum-ribbon';
    $template_css = get_template_directory() . '/assets/css/templates/' . $site_template . '.css';

    if (is_file($template_css)) {
        wp_enqueue_style(
            'wqs-site-template',
            get_template_directory_uri() . '/assets/css/templates/' . $site_template . '.css',
            array('wqs-portfolio-style'),
            (string) filemtime($template_css)
        );

        if (function_exists('wqs_get_site_template_custom_css')) {
            wp_add_inline_style('wqs-site-template', wqs_get_site_template_custom_css($site_template));
        }
    }

    if (is_front_page()) {
        $homepage_css = get_template_directory() . '/assets/css/homepage.css';
        $homepage_js = get_template_directory() . '/assets/js/homepage.js';

        wp_enqueue_style(
            'wqs-homepage',
            get_template_directory_uri() . '/assets/css/homepage.css',
            array('wqs-site-template'),
            is_file($homepage_css) ? (string) filemtime($homepage_css) : _S_VERSION
        );
        wp_enqueue_script(
            'wqs-homepage',
            get_template_directory_uri() . '/assets/js/homepage.js',
            array(),
            is_file($homepage_js) ? (string) filemtime($homepage_js) : _S_VERSION,
            true
        );
        wp_script_add_data('wqs-homepage', 'strategy', 'defer');
    } else {
        $site_template_js = get_template_directory() . '/assets/js/site-template.js';
        wp_enqueue_script(
            'wqs-site-template',
            get_template_directory_uri() . '/assets/js/site-template.js',
            array(),
            is_file($site_template_js) ? (string) filemtime($site_template_js) : _S_VERSION,
            true
        );
        wp_script_add_data('wqs-site-template', 'strategy', 'defer');
    }

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
 * Get the first image from post content as fallback for missing featured image.
 *
 * @param int $post_id Post ID.
 * @return array|null Image data (url, width, height) or null if not found.
 */
function wqs_get_first_content_image($post_id)
{
    $post = get_post($post_id);
    if (!$post) {
        return null;
    }

    $content = $post->post_content;
    if (empty($content)) {
        return null;
    }

    // Match image tags in content and return the first locally available image.
    preg_match_all('/<img[^>]+src=["\']([^"\']+)["\'][^>]*>/i', $content, $matches);
    if (empty($matches[1])) {
        return null;
    }

    foreach ($matches[1] as $raw_image_url) {
        $image_url = wqs_resolve_local_content_image_url($raw_image_url);
        if (!$image_url) {
            continue;
        }

        $attachment_id = attachment_url_to_postid($image_url);
        if ($attachment_id && wqs_attachment_file_exists($attachment_id)) {
            $image_data = wp_get_attachment_image_src($attachment_id, 'large');
            if ($image_data) {
                return array(
                    'url' => $image_data[0],
                    'width' => $image_data[1],
                    'height' => $image_data[2],
                );
            }
        }

        $dimensions = wqs_get_local_image_dimensions($image_url);
        return array(
            'url' => $image_url,
            'width' => $dimensions[0],
            'height' => $dimensions[1],
        );
    }

    return null;
}

/**
 * Return the shared local placeholder used by every post list.
 */
function wqs_get_placeholder_image_url()
{
    return get_template_directory_uri() . '/assets/images/review-placeholder.png';
}

/**
 * Check that an attachment still has a readable file on disk.
 */
function wqs_attachment_file_exists($attachment_id)
{
    $file = get_attached_file($attachment_id);
    return $file && is_file($file);
}

/**
 * Resolve migrated image paths and reject missing local files.
 */
function wqs_resolve_local_content_image_url($raw_url)
{
    $raw_url = html_entity_decode(trim((string) $raw_url));
    if ($raw_url === '') {
        return '';
    }

    $parsed_path = wp_parse_url($raw_url, PHP_URL_PATH);
    $relative_path = '';

    if (preg_match('#(?:^|/)(images/stories/.+)$#i', (string) $parsed_path, $matches)) {
        $relative_path = $matches[1];
    } elseif (!wp_http_validate_url($raw_url)) {
        $relative_path = ltrim(strtok($raw_url, '?#'), '/');
    }

    if ($relative_path !== '') {
        $local_file = ABSPATH . $relative_path;
        return is_file($local_file) ? home_url('/' . $relative_path) : '';
    }

    $uploads = wp_upload_dir();
    if (strpos($raw_url, $uploads['baseurl']) === 0) {
        $local_file = $uploads['basedir'] . substr($raw_url, strlen($uploads['baseurl']));
        return is_file($local_file) ? $raw_url : '';
    }

    $home_path = wp_parse_url(home_url('/'), PHP_URL_PATH);
    if ($parsed_path && $home_path && strpos($parsed_path, $home_path) === 0) {
        $local_file = ABSPATH . ltrim(substr($parsed_path, strlen($home_path)), '/');
        return is_file($local_file) ? $raw_url : '';
    }

    return wp_http_validate_url($raw_url) ? $raw_url : '';
}

/**
 * Read dimensions for an image stored inside the local WordPress tree.
 */
function wqs_get_local_image_dimensions($image_url)
{
    $path = wp_parse_url($image_url, PHP_URL_PATH);
    $home_path = wp_parse_url(home_url('/'), PHP_URL_PATH);
    if (!$path || !$home_path || strpos($path, $home_path) !== 0) {
        return array(0, 0);
    }

    $file = ABSPATH . ltrim(substr($path, strlen($home_path)), '/');
    if (!is_file($file)) {
        return array(0, 0);
    }

    $size = wp_getimagesize($file);
    return $size ? array((int) $size[0], (int) $size[1]) : array(0, 0);
}

/**
 * Check if image has extreme aspect ratio (5x or more difference).
 *
 * @param int $width Image width.
 * @param int $height Image height.
 * @return bool True if extreme aspect ratio.
 */
function wqs_is_extreme_aspect_ratio($width, $height)
{
    if ($width <= 0 || $height <= 0) {
        return false;
    }
    $ratio = max($width / $height, $height / $width);
    return $ratio >= 5;
}

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

/**
 * Keep language URLs clean by redirecting legacy ?lang=xx links to Polylang URLs.
 */
function wqs_redirect_legacy_lang_query()
{
    if (is_admin() || empty($_GET['lang']) || !function_exists('pll_the_languages')) {
        return;
    }

    $target_lang = sanitize_key(wp_unslash($_GET['lang']));
    if (!in_array($target_lang, array('en', 'zh'), true)) {
        return;
    }

    if (function_exists('wqs_get_clean_language_url')) {
        $target_url = wqs_get_clean_language_url($target_lang);
    } elseif (function_exists('pll_home_url')) {
        $target_url = pll_home_url($target_lang);
    } else {
        $target_url = home_url('/');
    }

    $target_url = remove_query_arg('lang', $target_url);

    if (!empty($target_url)) {
        wp_safe_redirect($target_url, 301);
        exit;
    }
}
add_action('template_redirect', 'wqs_redirect_legacy_lang_query', 1);
