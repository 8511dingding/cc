<?php
/**
 * Plugin Name: 王庆松艺术档案库
 * Plugin URI: https://example.com/wang-qingsong-archive
 * Description: 当代艺术家王庆松作品、展览、工作照档案库，复刻 MoMA Collection 风格。短代码 [wq_archive] 可嵌入任意页面。
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
 */
function wq_archive_register_post_types() {

    $artwork_labels = array(
        'name'                  => '作品',
        'singular_name'         => '作品',
        'menu_name'             => '作品',
        'add_new'               => '添加作品',
        'add_new_item'          => '添加新作品',
        'edit_item'             => '编辑作品',
        'new_item'              => '新作品',
        'view_item'             => '查看作品',
        'search_items'          => '搜索作品',
        'not_found'             => '未找到作品',
        'featured_image'        => '作品图片',
        'set_featured_image'    => '设置作品图片',
    );

    $artwork_args = array(
        'label'               => '作品',
        'labels'              => $artwork_labels,
        'public'              => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'supports'            => array('title', 'editor', 'thumbnail', 'excerpt'),
        'has_archive'         => true,
        'rewrite'             => array('slug' => 'artwork', 'with_front' => false),
    );
    register_post_type('artwork', $artwork_args);

    $exhibition_labels = array(
        'name'                  => '展览',
        'singular_name'         => '展览',
        'menu_name'             => '展览',
        'add_new'               => '添加展览',
        'add_new_item'          => '添加新展览',
        'edit_item'             => '编辑展览',
        'new_item'              => '新展览',
        'view_item'             => '查看展览',
        'search_items'          => '搜索展览',
        'not_found'             => '未找到展览',
        'featured_image'        => '展览图片',
        'set_featured_image'    => '设置展览图片',
    );

    $exhibition_args = array(
        'label'               => '展览',
        'labels'              => $exhibition_labels,
        'public'              => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'supports'            => array('title', 'editor', 'thumbnail', 'excerpt'),
        'has_archive'         => true,
        'rewrite'             => array('slug' => 'exhibition', 'with_front' => false),
    );
    register_post_type('exhibition', $exhibition_args);

    $shooting_labels = array(
        'name'                  => '工作照',
        'singular_name'         => '工作照',
        'menu_name'             => '工作照',
        'add_new'               => '添加工作照',
        'add_new_item'          => '添加新工作照',
        'edit_item'             => '编辑工作照',
        'new_item'              => '新工作照',
        'view_item'             => '查看工作照',
        'search_items'          => '搜索工作照',
        'not_found'             => '未找到工作照',
        'featured_image'        => '工作照图片',
        'set_featured_image'    => '设置工作照图片',
    );

    $shooting_args = array(
        'label'               => '工作照',
        'labels'              => $shooting_labels,
        'public'              => true,
        'publicly_queryable'  => true,
        'show_ui'             => true,
        'show_in_menu'        => true,
        'supports'            => array('title', 'editor', 'thumbnail', 'excerpt'),
        'has_archive'         => true,
        'rewrite'             => array('slug' => 'shooting', 'with_front' => false),
    );
    register_post_type('shooting', $shooting_args);
}
add_action('init', 'wq_archive_register_post_types', 10);

/**
 * ================================================
 * 注册自定义分类法 (Custom Taxonomies)
 * ================================================
 */
function wq_archive_register_taxonomies() {

    $year_labels = array(
        'name'              => '年份',
        'singular_name'     => '年份',
        'menu_name'         => '年份',
        'all_items'         => '所有年份',
        'edit_item'         => '编辑年份',
        'add_new_item'      => '添加新年份',
        'search_items'      => '搜索年份',
    );

    register_taxonomy('creation_year', array('artwork', 'exhibition', 'shooting'), array(
        'labels'            => $year_labels,
        'hierarchical'      => true,
        'show_ui'          => true,
        'show_admin_column' => true,
        'rewrite'          => array('slug' => 'creation-year'),
        'show_in_rest'     => true,
    ));

    $type_labels = array(
        'name'              => '媒介类型',
        'singular_name'     => '媒介类型',
        'menu_name'         => '媒介类型',
        'all_items'         => '所有类型',
        'edit_item'         => '编辑类型',
        'add_new_item'      => '添加新类型',
        'search_items'      => '搜索类型',
    );

    register_taxonomy('item_type', array('artwork', 'exhibition', 'shooting'), array(
        'labels'            => $type_labels,
        'hierarchical'      => false,
        'show_ui'          => true,
        'show_admin_column' => true,
        'rewrite'          => array('slug' => 'item-type'),
        'show_in_rest'     => true,
    ));
}
add_action('init', 'wq_archive_register_taxonomies', 10);

/**
 * ================================================
 * 激活/停用
 * ================================================
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
 * 资源加载（仅在短代码出现时加载）
 * ================================================
 */
function wq_archive_enqueue_assets() {
    global $post;
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'wq_archive')) {
        wp_enqueue_style('wq-archive-styles', WQ_ARCHIVE_PLUGIN_URL . 'assets/css/archive.css', array(), WQ_ARCHIVE_VERSION);
        wp_enqueue_script('wq-archive-scripts', WQ_ARCHIVE_PLUGIN_URL . 'assets/js/archive.js', array('jquery'), WQ_ARCHIVE_VERSION, true);
        wp_localize_script('wq-archive-scripts', 'wqArchive', array(
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce'   => wp_create_nonce('wq_archive_nonce'),
        ));
    }
}
add_action('wp_enqueue_scripts', 'wq_archive_enqueue_assets');

/**
 * ================================================
 * 短代码 [wq_archive]
 * 完全独立，嵌入任意页面/帖子/小工具
 * ================================================
 */
function wq_archive_shortcode($atts) {
    $atts = shortcode_atts(array(
        'post_type' => 'artwork',
        'limit'     => 12,
    ), $atts, 'wq_archive');

    ob_start();

    // 获取筛选选项
    $item_types = get_terms(array('taxonomy' => 'item_type', 'hide_empty' => true, 'orderby' => 'name'));
    $creation_years = get_terms(array('taxonomy' => 'creation_year', 'hide_empty' => true, 'orderby' => 'name', 'order' => 'DESC'));
    ?>
    <div class="wq-archive" id="wq-archive-top">

        <header class="wq-archive__header">
            <div class="wq-archive__header-inner">
                <h1 class="wq-archive__site-title">王庆松</h1>
                <p class="wq-archive__site-subtitle">Wang Qingsong — Archive</p>
            </div>
            <hr class="wq-archive__rule wq-archive__rule--heavy">
        </header>

        <section class="wq-archive__filter-bar">

            <div class="wq-archive__search-wrap">
                <label for="wq-archive-search" class="wq-archive__filter-label">搜索</label>
                <input type="search" id="wq-archive-search" class="wq-archive__search-input" placeholder="关键词...">
            </div>

            <hr class="wq-archive__rule wq-archive__rule--medium">

            <div class="wq-archive__type-tabs">
                <span class="wq-archive__filter-label">类型</span>
                <div class="wq-archive__tabs-list">
                    <button class="wq-archive__tab wq-archive__tab--active" data-post-type="artwork" type="button">作品</button>
                    <button class="wq-archive__tab" data-post-type="exhibition" type="button">展览</button>
                    <button class="wq-archive__tab" data-post-type="shooting" type="button">工作照</button>
                </div>
            </div>

            <hr class="wq-archive__rule wq-archive__rule--medium">

            <div class="wq-archive__dropdowns">
                <div class="wq-archive__dropdown-wrap">
                    <label for="wq-archive-type-filter" class="wq-archive__filter-label">媒介</label>
                    <select id="wq-archive-type-filter" class="wq-archive__select">
                        <option value="">全部媒介</option>
                        <?php if (!is_wp_error($item_types)): foreach ($item_types as $type): ?>
                            <option value="<?php echo esc_attr($type->slug); ?>"><?php echo esc_html($type->name); ?></option>
                        <?php endforeach; endif; ?>
                    </select>
                </div>

                <div class="wq-archive__dropdown-wrap">
                    <label for="wq-archive-year-filter" class="wq-archive__filter-label">年份</label>
                    <select id="wq-archive-year-filter" class="wq-archive__select">
                        <option value="">全部年份</option>
                        <?php if (!is_wp_error($creation_years)): foreach ($creation_years as $year): ?>
                            <option value="<?php echo esc_attr($year->slug); ?>"><?php echo esc_html($year->name); ?></option>
                        <?php endforeach; endif; ?>
                    </select>
                </div>
            </div>

            <hr class="wq-archive__rule wq-archive__rule--medium">

        </section>

        <div class="wq-archive__results-meta">
            <span class="wq-archive__results-count" id="wq-archive-results-count">加载中...</span>
        </div>

        <main class="wq-archive__grid-container">
            <div class="wq-archive__grid" id="wq-archive-grid">
                <div class="wq-archive__loading" aria-busy="true">
                    <span class="wq-archive__loading-text">加载中...</span>
                </div>
            </div>
            <div class="wq-archive__no-results" id="wq-archive-no-results" hidden>
                <p>未找到匹配的内容，请尝试其他筛选条件。</p>
            </div>
        </main>

        <div class="wq-archive__pagination" id="wq-archive-pagination" hidden>
            <button class="wq-archive__load-more" id="wq-archive-load-more" type="button">加载更多</button>
        </div>

    </div>

    <script>
    window.wqArchive = {
        ajaxUrl: '<?php echo esc_url(admin_url('admin-ajax.php')); ?>',
        nonce: '<?php echo esc_attr(wp_create_nonce('wq_archive_nonce')); ?>',
        currentPostType: '<?php echo esc_attr($atts['post_type']); ?>',
        postsPerPage: <?php echo intval($atts['limit']); ?>
    };
    </script>
    <?php

    return ob_get_clean();
}
add_shortcode('wq_archive', 'wq_archive_shortcode');

/**
 * ================================================
 * AJAX 处理器
 * ================================================
 */
function wq_archive_fetch_results() {
    check_ajax_referer('wq_archive_nonce', 'nonce');

    $post_type = isset($_POST['post_type']) ? sanitize_text_field($_POST['post_type']) : 'artwork';
    $item_type = isset($_POST['item_type']) ? sanitize_text_field($_POST['item_type']) : '';
    $creation_year = isset($_POST['creation_year']) ? sanitize_text_field($_POST['creation_year']) : '';
    $search = isset($_POST['s']) ? sanitize_text_field($_POST['s']) : '';
    $page = isset($_POST['page']) ? intval($_POST['page']) : 1;
    $posts_per_page = isset($_POST['posts_per_page']) ? intval($_POST['posts_per_page']) : 12;

    $args = array(
        'post_type'      => $post_type,
        'posts_per_page' => $posts_per_page,
        'paged'          => $page,
        'post_status'    => 'publish',
    );

    if (!empty($search)) {
        $args['s'] = $search;
    }

    $tax_query = array();

    if (!empty($item_type)) {
        $tax_query[] = array('taxonomy' => 'item_type', 'field' => 'slug', 'terms' => $item_type);
    }

    if (!empty($creation_year)) {
        $tax_query[] = array('taxonomy' => 'creation_year', 'field' => 'slug', 'terms' => $creation_year);
    }

    if (!empty($tax_query)) {
        if (count($tax_query) > 1) {
            $tax_query['relation'] = 'AND';
        }
        $args['tax_query'] = $tax_query;
    }

    $query = new WP_Query($args);
    $total = $query->found_posts;
    $has_more = ($page * $posts_per_page) < $total;

    $items = array();
    if ($query->have_posts()) {
        while ($query->have_posts()) {
            $query->the_post();
            $post_id = get_the_ID();
            $thumbnail = has_post_thumbnail($post_id) ? get_the_post_thumbnail_url($post_id, 'medium') : null;

            $type_terms = get_the_terms($post_id, 'item_type');
            $year_terms = get_the_terms($post_id, 'creation_year');
            $meta_parts = array();
            if ($type_terms && !is_wp_error($type_terms)) { $meta_parts[] = $type_terms[0]->name; }
            if ($year_terms && !is_wp_error($year_terms)) { $meta_parts[] = $year_terms[0]->name; }

            $items[] = array(
                'title'     => get_the_title(),
                'thumbnail' => $thumbnail,
                'url'       => get_permalink(),
                'meta'      => implode(' / ', $meta_parts),
            );
        }
        wp_reset_postdata();
    }

    wp_send_json_success(array('items' => $items, 'total' => $total, 'has_more' => $has_more));
}
add_action('wp_ajax_wq_archive_fetch_results', 'wq_archive_fetch_results');
add_action('wp_ajax_nopriv_wq_archive_fetch_results', 'wq_archive_fetch_results');
