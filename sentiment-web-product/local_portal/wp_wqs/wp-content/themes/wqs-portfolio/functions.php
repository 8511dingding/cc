<?php
/**
 * WQS Portfolio functions and definitions
 *
 * @link https://developer.wordpress.org/themes/basics/theme-functions/
 *
 * @package WQS_Portfolio
 * @since 1.0.0
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Sets up theme defaults and registers support for various WordPress features.
 */
function wqs_portfolio_setup()
{
    /*
     * Make theme available for translation.
     * Translations can be filed in the /languages/ directory.
     */
    load_theme_textdomain('wqs-portfolio', get_template_directory() . '/languages');

    // Add default posts and comments RSS feed links to head.
    add_theme_support('automatic-feed-links');

    /*
     * Let WordPress manage the document title.
     * By adding theme support, we declare that this theme does not use a
     * hard-coded <title> tag in the document head, and expect WordPress to
     * provide it for us.
     */
    add_theme_support('title-tag');

    /*
     * Enable support for Post Thumbnails on posts and pages.
     *
     * @link https://developer.wordpress.org/themes/functionality/post-thumbnails/
     */
    add_theme_support('post-thumbnails');

    // Register navigation menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'wqs-portfolio'),
        'footer' => __('Footer Menu', 'wqs-portfolio'),
    ));

    /*
     * Switch default core markup for search form, comment form, and comments
     * to output valid HTML5 markup.
     */
    add_theme_support('html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ));

    // Add theme support for selective refresh for widgets.
    add_theme_support('customize-selective-refresh-widgets');

    // Custom image sizes for works
    add_image_size('works-thumb', 600, 450, true);
    add_image_size('works-full', 1200, 900, false);
}
add_action('after_setup_theme', 'wqs_portfolio_setup');

/**
 * Register widget areas.
 *
 * @link https://developer.wordpress.org/themes/functionality/sidebars/#registering-a-sidebar
 */
function wqs_portfolio_widgets_init()
{
    register_sidebar(array(
        'name'          => __('Sidebar', 'wqs-portfolio'),
        'id'            => 'sidebar-1',
        'description'   => __('Add widgets here to appear in your sidebar.', 'wqs-portfolio'),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h2 class="widget-title">',
        'after_title'   => '</h2>',
    ));
}
add_action('widgets_init', 'wqs_portfolio_widgets_init');

/**
 * Enqueue scripts and styles.
 */
function wqs_portfolio_scripts()
{
    // Main stylesheet
    wp_enqueue_style('wqs-portfolio-style', get_stylesheet_uri(), array(), '1.0.0');

    // Google Fonts
    wp_enqueue_style('wqs-fonts', 'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&display=swap', array(), null);

    // PhotoSwipe CSS
    wp_enqueue_style('photoswipe', 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe.min.css', array(), '5.4.4');

    // Main JavaScript
    wp_enqueue_script('wqs-portfolio-scripts', get_template_directory_uri() . '/assets/js/main.js', array('jquery'), '1.0.0', true);

    // PhotoSwipe JS
    wp_enqueue_script('photoswipe', 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/umd/photoswipe.min.js', array(), '5.4.4', true);
    wp_enqueue_script('photoswipe-ui', 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/umd/photoswipe-lightbox.min.js', array('photoswipe'), '5.4.4', true);

    // Pass AJAX URL to JS
    wp_localize_script('wqs-portfolio-scripts', 'wqs_ajax', array(
        'ajax_url' => admin_url('admin-ajax.php'),
    ));
}
add_action('wp_enqueue_scripts', 'wqs_portfolio_scripts');

/**
 * Register Custom Post Types.
 */
function wqs_register_post_types()
{
    // Works Post Type
    register_post_type('works', array(
        'labels' => array(
            'name'                  => __('作品', 'wqs-portfolio'),
            'singular_name'         => __('作品', 'wqs-portfolio'),
            'menu_name'             => __('作品', 'wqs-portfolio'),
            'name_admin_bar'        => __('作品', 'wqs-portfolio'),
            'add_new'               => __('添加新作品', 'wqs-portfolio'),
            'add_new_item'          => __('添加新作品', 'wqs-portfolio'),
            'edit_item'             => __('编辑作品', 'wqs-portfolio'),
            'new_item'              => __('新作品', 'wqs-portfolio'),
            'view_item'             => __('查看作品', 'wqs-portfolio'),
            'view_items'            => __('查看作品', 'wqs-portfolio'),
            'search_items'          => __('搜索作品', 'wqs-portfolio'),
            'not_found'             => __('未找到作品', 'wqs-portfolio'),
            'not_found_in_trash'    => __('回收站中未找到作品', 'wqs-portfolio'),
            'all_items'             => __('所有作品', 'wqs-portfolio'),
        ),
        'label'                 => __('作品', 'wqs-portfolio'),
        'description'           => __('王庆松的摄影作品', 'wqs-portfolio'),
        'labels'                => array(
            'name'              => __('作品', 'wqs-portfolio'),
            'singular_name'     => __('作品', 'wqs-portfolio'),
        ),
        'public' => true,
        'show_ui'              => true,
        'show_in_menu'         => true,
        'show_in_nav_menus'    => true,
        'show_in_rest'         => true,
        'delete_with_user'     => false,
        'exclude_from_search'  => false,
        'has_archive' => true,
        'hierarchical'         => false,
        'map_meta_cap'         => true,
        'supports' => array(
            'title',
            'editor',
            'thumbnail',
            'excerpt',
            'trackbacks',
            'custom-fields',
            'comments',
            'revisions',
            'author',
            'page-attributes',
            'post-formats',
        ),
        'rewrite' => array(
            'slug'       => 'works',
            'with_front' => false,
            'feeds'      => true,
            'pages'      => true,
        ),
        'menu_position' => 5,
    ));

    // Exhibition Post Type
    register_post_type('exhibition', array(
        'labels' => array(
            'name'                  => __('Exhibitions', 'wqs-portfolio'),
            'singular_name'         => __('Exhibition', 'wqs-portfolio'),
            'menu_name'             => __('Exhibitions', 'wqs-portfolio'),
            'add_new'               => __('Add New', 'wqs-portfolio'),
            'add_new_item'          => __('Add Exhibition', 'wqs-portfolio'),
            'edit_item'             => __('Edit Exhibition', 'wqs-portfolio'),
            'new_item'              => __('New Exhibition', 'wqs-portfolio'),
            'view_item' => __('View Exhibition', 'wqs-portfolio'),
            'search_items'          => __('Search Exhibitions', 'wqs-portfolio'),
            'not_found'             => __('No exhibitions found', 'wqs-portfolio'),
        ),
        'public' => true,
        'show_ui'              => true,
        'show_in_nav_menus'    => true,
        'show_in_rest'         => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'rewrite' => array('slug' => 'exhibitions'),
        'menu_position' => 6,
    ));

    // Review Post Type
    register_post_type('review', array(
        'labels' => array(
            'name'                  => __('Reviews', 'wqs-portfolio'),
            'singular_name'         => __('Review', 'wqs-portfolio'),
            'menu_name'             => __('Reviews', 'wqs-portfolio'),
            'add_new'               => __('Add New', 'wqs-portfolio'),
            'add_new_item'          => __('Add Review', 'wqs-portfolio'),
            'edit_item'             => __('Edit Review', 'wqs-portfolio'),
            'new_item'              => __('New Review', 'wqs-portfolio'),
            'view_item'             => __('View Review', 'wqs-portfolio'),
            'search_items'          => __('Search Reviews', 'wqs-portfolio'),
            'not_found'             => __('No reviews found', 'wqs-portfolio'),
        ),
        'public' => true,
        'show_ui'              => true,
        'show_in_nav_menus'    => true,
        'show_in_rest'         => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'rewrite' => array('slug' => 'reviews'),
        'menu_position' => 7,
    ));

    // Behind the Scenes Post Type
    register_post_type('behind_the_scenes', array(
        'labels' => array(
            'name'                  => __('Behind the Scenes', 'wqs-portfolio'),
            'singular_name'         => __('Behind the Scenes', 'wqs-portfolio'),
            'menu_name'             => __('Behind the Scenes', 'wqs-portfolio'),
            'add_new'               => __('Add New', 'wqs-portfolio'),
            'add_new_item'          => __('Add BTS', 'wqs-portfolio'),
            'edit_item'             => __('Edit BTS', 'wqs-portfolio'),
            'new_item'              => __('New BTS', 'wqs-portfolio'),
            'view_item'             => __('View BTS', 'wqs-portfolio'),
            'search_items'          => __('Search BTS', 'wqs-portfolio'),
            'not_found'             => __('No BTS found', 'wqs-portfolio'),
        ),
        'public' => true,
        'show_ui'              => true,
        'show_in_nav_menus'    => true,
        'show_in_rest'         => true,
        'has_archive' => true,
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
        'rewrite' => array('slug' => 'behind-the-scenes'),
        'menu_position' => 8,
    ));

    // Flush rewrite rules after CPT registration
    flush_rewrite_rules();
}
add_action('init', 'wqs_register_post_types');

/**
 * Register Custom Taxonomies for Works.
 */
function wqs_register_taxonomies()
{
    // Year taxonomy for works
    register_taxonomy('works_year', 'works', array(
        'labels' => array(
            'name'              => __('年份', 'wqs-portfolio'),
            'singular_name'     => __('年份', 'wqs-portfolio'),
            'search_items'      => __('搜索年份', 'wqs-portfolio'),
            'all_items'         => __('所有年份', 'wqs-portfolio'),
            'edit_item'         => __('编辑年份', 'wqs-portfolio'),
            'update_item'       => __('更新年份', 'wqs-portfolio'),
            'add_new_item'      => __('添加新年份', 'wqs-portfolio'),
            'new_item_name'     => __('新年份名称', 'wqs-portfolio'),
            'not_found'         => __('未找到年份', 'wqs-portfolio'),
        ),
        'hierarchical'      => true,
        'show_ui'           => true,
        'show_admin_column' => true,
        'query_var'         => true,
        'show_in_rest'      => true,
        'rewrite'           => array('slug' => 'works-year'),
    ));

    // Category taxonomy for works
    register_taxonomy('works_category', 'works', array(
        'labels' => array(
            'name'              => __('作品分类', 'wqs-portfolio'),
            'singular_name'     => __('作品分类', 'wqs-portfolio'),
            'search_items'      => __('搜索分类', 'wqs-portfolio'),
            'all_items'         => __('所有分类', 'wqs-portfolio'),
            'edit_item'         => __('编辑分类', 'wqs-portfolio'),
            'update_item'       => __('更新分类', 'wqs-portfolio'),
            'add_new_item'      => __('添加新分类', 'wqs-portfolio'),
            'new_item_name'     => __('新分类名称', 'wqs-portfolio'),
            'not_found'         => __('未找到分类', 'wqs-portfolio'),
        ),
        'hierarchical'      => true,
        'show_ui'           => true,
        'show_admin_column' => true,
        'query_var'         => true,
        'show_in_rest'      => true,
        'rewrite'           => array('slug' => 'works-category'),
    ));
}
add_action('init', 'wqs_register_taxonomies');

/**
 * Polylang Integration - Register strings for translation.
 */
function wqs_pll_register_strings()
{
    if (function_exists('pll_register_string')) {
        pll_register_string('site-title', 'Wang Qingsong');
        pll_register_string('works-title', 'Works');
        pll_register_string('works-description', 'Photography works from 1997 to present');
        pll_register_string('menu-works', '作品');
        pll_register_string('menu-exhibition', '展览');
        pll_register_string('menu-review', '评论');
        pll_register_string('menu-bts', '工作照');
        pll_register_string('menu-resume', 'Resume');
        pll_register_string('menu-contact', 'Contact');
    }
}
add_action('pll_init', 'wqs_pll_register_strings');

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
 * Get translated post ID (Polylang helper).
 */
function wqs_get_translated_post($post_id, $lang = null)
{
    if (!function_exists('pll_get_post')) {
        return $post_id;
    }
    if ($lang === null) {
        $lang = pll_current_language('slug');
    }
    return pll_get_post($post_id, $lang);
}

/**
 * Get language switcher HTML.
 */
function wqs_get_language_switcher()
{
    if (!function_exists('pll_the_languages')) {
        return '';
    }

    $output = '<div class="language-switcher">';

    $languages = pll_the_languages(array(
        'dropdown' => 0,
        'show_flags' => 1,
        'show_names' => 1,
        'hide_if_no_translation' => 0,
        'hide_if_default' => 0,
        'echo' => 0,
    ));

    if ($languages) {
        $output .= $languages;
    }

    $output .= '</div>';

    return $output;
}