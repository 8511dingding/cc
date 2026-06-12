<?php
/**
 * Plugin Name: 王庆松艺术档案库
 * Plugin URI: https://example.com/wang-qingsong-archive
 * Description: 当代艺术家王庆松作品、展览、工作照档案库，复刻 MoMA Collection 风格
 * Version: 1.0.0
 * Author: Developer
 * Text Domain: wq-archive
 * Domain Path: /languages
 */

// ==================== 安全措施 ====================
if (!defined('ABSPATH')) {
    exit;
}

// ==================== 常量定义 ====================
define('WQ_ARCHIVE_VERSION', '1.0.0');
define('WQ_ARCHIVE_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('WQ_ARCHIVE_PLUGIN_URL', plugin_dir_url(__FILE__));

/**
 * ================================================
 * 注册自定义文章类型 (Custom Post Types)
 * ================================================
 * 三种 CPT 覆盖艺术家档案的三大核心内容：
 * - artwork: 作品（摄影、装置等）
 * - exhibition: 展览记录
 * - shooting: 工作照/幕后花絮
 */
function wq_archive_register_post_types() {

    // --- 作品 (Artwork) ---
    $artwork_labels = array(
        'name'                  => '作品',
        'singular_name'         => '作品',
        'menu_name'             => '作品',
        'name_admin_bar'        => '作品',
        'add_new'               => '添加作品',
        'add_new_item'          => '添加新作品',
        'edit_item'             => '编辑作品',
        'new_item'              => '新作品',
        'view_item'             => '查看作品',
        'search_items'          => '搜索作品',
        'not_found'             => '未找到作品',
        'not_found_in_trash'    => '回收站中未找到作品',
        'featured_image'        => '作品图片',
        'set_featured_image'    => '设置作品图片',
        'remove_featured_image' => '移除作品图片',
    );

    $artwork_args = array(
        'label'               => '作品',
        'labels'              => $artwork_labels,
        'description'         => '王庆松老师的艺术作品集',
        'public'              => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'show_in_nav_menus'   => true,
        'show_in_admin_bar'   => true,
        'menu_position'       => 5,
        'menu_icon'           => 'dashicons-art',
        'capability_type'     => 'post',
        'hierarchical'        => false,
        'exclude_from_search' => false,
        'supports'            => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'has_archive'         => true,
        'rewrite'             => array('slug' => 'artwork', 'with_front' => false),
        'query_var'           => true,
        'can_export'          => true,
    );
    register_post_type('artwork', $artwork_args);

    // --- 展览 (Exhibition) ---
    $exhibition_labels = array(
        'name'                  => '展览',
        'singular_name'         => '展览',
        'menu_name'             => '展览',
        'name_admin_bar'        => '展览',
        'add_new'               => '添加展览',
        'add_new_item'          => '添加新展览',
        'edit_item'             => '编辑展览',
        'new_item'              => '新展览',
        'view_item'             => '查看展览',
        'search_items'          => '搜索展览',
        'not_found'             => '未找到展览',
        'not_found_in_trash'    => '回收站中未找到展览',
        'featured_image'        => '展览图片',
        'set_featured_image'    => '设置展览图片',
        'remove_featured_image' => '移除展览图片',
    );

    $exhibition_args = array(
        'label'               => '展览',
        'labels'              => $exhibition_labels,
        'description'         => '王庆松老师的展览记录',
        'public'              => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'show_in_nav_menus'   => true,
        'show_in_admin_bar'   => true,
        'menu_position'       => 5,
        'menu_icon'           => 'dashicons-calendar-alt',
        'capability_type'     => 'post',
        'hierarchical'        => false,
        'exclude_from_search' => false,
        'supports'            => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'has_archive'         => true,
        'rewrite'             => array('slug' => 'exhibition', 'with_front' => false),
        'query_var'           => true,
        'can_export'          => true,
    );
    register_post_type('exhibition', $exhibition_args);

    // --- 工作照 (Shooting) ---
    $shooting_labels = array(
        'name'                  => '工作照',
        'singular_name'         => '工作照',
        'menu_name'             => '工作照',
        'name_admin_bar'        => '工作照',
        'add_new'               => '添加工作照',
        'add_new_item'          => '添加新工作照',
        'edit_item'             => '编辑工作照',
        'new_item'              => '新工作照',
        'view_item'             => '查看工作照',
        'search_items'          => '搜索工作照',
        'not_found'             => '未找到工作照',
        'not_found_in_trash'    => '回收站中未找到工作照',
        'featured_image'        => '工作照图片',
        'set_featured_image'    => '设置工作照图片',
        'remove_featured_image' => '移除工作照图片',
    );

    $shooting_args = array(
        'label'               => '工作照',
        'labels'              => $shooting_labels,
        'description'         => '王庆松老师的工作照、创作过程记录',
        'public'              => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'show_in_nav_menus'   => true,
        'show_in_admin_bar'   => true,
        'menu_position'       => 5,
        'menu_icon'           => 'dashicons-camera-alt',
        'capability_type'     => 'post',
        'hierarchical'        => false,
        'exclude_from_search' => false,
        'supports'            => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'has_archive'         => true,
        'rewrite'             => array('slug' => 'shooting', 'with_front' => false),
        'query_var'           => true,
        'can_export'          => true,
    );
    register_post_type('shooting', $shooting_args);
}
add_action('init', 'wq_archive_register_post_types', 10);

/**
 * ================================================
 * 注册自定义分类法 (Custom Taxonomies)
 * ================================================
 * - creation_year: 年份（层级化，用于时间跨度筛选，对应 MoMA 的 Date 筛选）
 * - item_type: 媒介/类型（摄影、装置、手稿等）
 */
function wq_archive_register_taxonomies() {

    // --- 年份分类 (Creation Year) - 层级化 ---
    $year_labels = array(
        'name'              => '年份',
        'singular_name'     => '年份',
        'menu_name'         => '年份',
        'all_items'         => '所有年份',
        'edit_item'         => '编辑年份',
        'view_item'         => '查看年份',
        'update_item'       => '更新年份',
        'add_new_item'      => '添加新年份',
        'new_item_name'     => '新年份名称',
        'search_items'      => '搜索年份',
        'popular_items'     => '常用年份',
        'separate_items_with_commas' => '多个年份用逗号分隔',
        'add_or_remove_items' => '添加或删除年份',
        'choose_from_most_used' => '选择最常用的年份',
    );

    $year_args = array(
        'labels'            => $year_labels,
        'hierarchical'      => true,  // true = 层级化 (如 Categories)
        'show_ui'          => true,
        'show_admin_column' => true,
        'query_var'        => true,
        'rewrite'          => array('slug' => 'creation-year'),
        'show_in_rest'     => true,  // Gutenberg 支持
        'capabilities'     => array(
            'manage_terms' => 'edit_posts',
            'edit_terms'   => 'edit_posts',
            'delete_terms' => 'edit_posts',
            'assign_terms' => 'edit_posts',
        ),
    );
    register_taxonomy('creation_year', array('artwork', 'exhibition', 'shooting'), $year_args);

    // --- 媒介类型分类 (Item Type) - 非层级化 ---
    $type_labels = array(
        'name'              => '媒介类型',
        'singular_name'     => '媒介类型',
        'menu_name'         => '媒介类型',
        'all_items'         => '所有类型',
        'edit_item'         => '编辑类型',
        'view_item'         => '查看类型',
        'update_item'       => '更新类型',
        'add_new_item'      => '添加新类型',
        'new_item_name'     => '新类型名称',
        'search_items'      => '搜索类型',
        'popular_items'     => '常用类型',
        'separate_items_with_commas' => '多个类型用逗号分隔',
        'add_or_remove_items' => '添加或删除类型',
        'choose_from_most_used' => '选择最常用的类型',
    );

    $type_args = array(
        'labels'            => $type_labels,
        'hierarchical'      => false, // 非层级化 (如 Tags)
        'show_ui'          => true,
        'show_admin_column' => true,
        'query_var'        => true,
        'rewrite'          => array('slug' => 'item-type'),
        'show_in_rest'     => true,  // Gutenberg 支持
        'capabilities'     => array(
            'manage_terms' => 'edit_posts',
            'edit_terms'   => 'edit_posts',
            'delete_terms' => 'edit_posts',
            'assign_terms' => 'edit_posts',
        ),
    );
    register_taxonomy('item_type', array('artwork', 'exhibition', 'shooting'), $type_args);
}
add_action('init', 'wq_archive_register_taxonomies', 10);

/**
 * ================================================
 * 激活/停用时的刷新重写规则
 * ================================================
 * 确保 CPT 和 Taxonomy 的 slug 能正常工作
 */
function wq_archive_activate() {
    wq_archive_register_post_types();
    wq_archive_register_taxonomies();
    flush_rewrite_rules();
}
register_activation_hook(__FILE__, 'wq_archive_activate');

function wq_archive_deactivate() {
    flush_rewrite_rules();
}
register_deactivation_hook(__FILE__, 'wq_archive_deactivate');

/**
 * ================================================
 * 插件加载时执行（确保在 init 时已注册）
 * ================================================
 */
function wq_archive_loaded() {
    // CPT 和 Taxonomy 在 init 钩子中注册
    // 此处可添加其他初始化逻辑
}
add_action('plugins_loaded', 'wq_archive_loaded');

/**
 * ================================================
 * 引入前端资源（CSS/JS）和模板文件
 * ================================================
 */
function wq_archive_enqueue_assets() {
    // 仅在归档页面或指定模板加载样式
    if (is_post_type_archive(array('artwork', 'exhibition', 'shooting')) ||
        is_tax(array('creation_year', 'item_type'))) {
        wp_enqueue_style(
            'wq-archive-styles',
            WQ_ARCHIVE_PLUGIN_URL . 'assets/css/archive.css',
            array(),
            WQ_ARCHIVE_VERSION
        );
        wp_enqueue_script(
            'wq-archive-scripts',
            WQ_ARCHIVE_PLUGIN_URL . 'assets/js/archive.js',
            array('jquery'),
            WQ_ARCHIVE_VERSION,
            true
        );
        // 传递 AJAX URL 到 JS
        wp_localize_script('wq-archive-scripts', 'wqArchive', array(
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce'   => wp_create_nonce('wq_archive_nonce'),
        ));
    }
}
add_action('wp_enqueue_scripts', 'wq_archive_enqueue_assets');

/**
 * ================================================
 * AJAX 处理器 — 筛选结果查询
 * ================================================
 */
function wq_archive_fetch_results() {
    check_ajax_referer('wq_archive_nonce', 'nonce');

    $post_type = isset($_POST['post_type']) ? sanitize_text_field($_POST['post_type']) : 'artwork';
    $item_type = isset($_POST['item_type']) ? sanitize_text_field($_POST['item_type']) : '';
    $creation_year = isset($_POST['creation_year']) ? sanitize_text_field($_POST['creation_year']) : '';
    $search = isset($_POST['s']) ? sanitize_text_field($_POST['s']) : '';
    $page = isset($_POST['page']) ? intval($_POST['page']) : 1;
    $posts_per_page = 12;

    $args = array(
        'post_type'      => $post_type,
        'posts_per_page' => $posts_per_page,
        'paged'          => $page,
        'post_status'    => 'publish',
    );

    if (!empty($search)) {
        $args['s'] = $search;
    }

    if (!empty($item_type)) {
        $args['tax_query'][] = array(
            'taxonomy' => 'item_type',
            'field'    => 'slug',
            'terms'    => $item_type,
        );
    }

    if (!empty($creation_year)) {
        $args['tax_query'][] = array(
            'taxonomy' => 'creation_year',
            'field'    => 'slug',
            'terms'    => $creation_year,
        );
    }

    if (count($args['tax_query']) > 1) {
        $args['tax_query']['relation'] = 'AND';
    }

    $query = new WP_Query($args);
    $total = $query->found_posts;
    $has_more = ($page * $posts_per_page) < $total;

    $items = array();
    if ($query->have_posts()) {
        while ($query->have_posts()) {
            $query->the_post();
            $post_id = get_the_ID();

            if (has_post_thumbnail($post_id)) {
                $thumbnail = get_the_post_thumbnail_url($post_id, 'medium');
            } else {
                $thumbnail = null;
            }

            $type_terms = get_the_terms($post_id, 'item_type');
            $year_terms = get_the_terms($post_id, 'creation_year');
            $meta_parts = array();
            if ($type_terms && !is_wp_error($type_terms)) {
                $meta_parts[] = $type_terms[0]->name;
            }
            if ($year_terms && !is_wp_error($year_terms)) {
                $meta_parts[] = $year_terms[0]->name;
            }

            $items[] = array(
                'title'     => get_the_title(),
                'thumbnail' => $thumbnail,
                'url'       => get_permalink(),
                'meta'      => implode(' / ', $meta_parts),
            );
        }
        wp_reset_postdata();
    }

    wp_send_json_success(array(
        'items'    => $items,
        'total'    => $total,
        'has_more' => $has_more,
    ));
}
add_action('wp_ajax_wq_archive_fetch_results', 'wq_archive_fetch_results');
add_action('wp_ajax_nopriv_wq_archive_fetch_results', 'wq_archive_fetch_results');