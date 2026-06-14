<?php
/**
 * Template Name: 王庆松艺术档案库 (MoMA Style)
 * Template Description: 复刻 MoMA Collection 风格的艺术家档案库检索与展示页面
 *
 * @package WQS_Archive
 */

wp_enqueue_style(
    'wqs-archive-plugin-styles',
    plugins_url('wq-archive/assets/css/archive.css'),
    array(),
    '1.0.0'
);

wp_enqueue_script(
    'wqs-archive-plugin-scripts',
    plugins_url('wq-archive/assets/js/archive.js'),
    array('jquery'),
    '1.0.0',
    true
);

wp_localize_script(
    'wqs-archive-plugin-scripts',
    'wqArchive',
    array(
        'ajaxUrl'         => admin_url('admin-ajax.php'),
        'nonce'           => wp_create_nonce('wq_archive_nonce'),
        'currentPostType' => 'artwork',
        'currentType'     => '',
        'currentYear'     => '',
        'searchQuery'     => '',
        'postsPerPage'    => 12,
    )
);

get_header();
?>

<!-- ================================================
     主容器：MoMA 风格极简艺术馆布局
     ================================================ -->
<div class="wq-archive" id="wq-archive-top">

    <!-- ================================================
         顶部标题区
         ================================================ -->
    <header class="wq-archive__header">
        <div class="wq-archive__header-inner">
            <h1 class="wq-archive__site-title">王庆松</h1>
            <p class="wq-archive__site-subtitle">Wang Qingsong — Archive</p>
        </div>
        <hr class="wq-archive__rule wq-archive__rule--heavy">
    </header>

    <!-- ================================================
         检索栏 (Search & Filter Bar)
         MoMA 风格：扁平化表单控件，无圆角阴影
         ================================================ -->
    <section class="wq-archive__filter-bar" aria-label="<?php esc_attr_e('筛选与搜索', 'wqs-archive'); ?>">

        <!-- 搜索框 -->
        <div class="wq-archive__search-wrap">
            <label for="wq-archive-search" class="wq-archive__filter-label">
                <?php esc_html_e('搜索', 'wqs-archive'); ?>
            </label>
            <input
                type="search"
                id="wq-archive-search"
                class="wq-archive__search-input"
                placeholder="<?php esc_attr_e('关键词...', 'wqs-archive'); ?>"
                value=""
            >
        </div>

        <hr class="wq-archive__rule wq-archive__rule--medium">

        <!-- 内容类型切换 (Tabs) -->
        <div class="wq-archive__type-tabs" role="tablist" aria-label="<?php esc_attr_e('内容类型', 'wqs-archive'); ?>">
            <span class="wq-archive__filter-label"><?php esc_html_e('类型', 'wqs-archive'); ?></span>
            <div class="wq-archive__tabs-list">
                <button
                    class="wq-archive__tab wq-archive__tab--active"
                    role="tab"
                    data-post-type="artwork"
                    aria-selected="true"
                    type="button"
                ><?php esc_html_e('作品', 'wqs-archive'); ?></button>
                <button
                    class="wq-archive__tab"
                    role="tab"
                    data-post-type="exhibition"
                    aria-selected="false"
                    type="button"
                ><?php esc_html_e('展览', 'wqs-archive'); ?></button>
                <button
                    class="wq-archive__tab"
                    role="tab"
                    data-post-type="shooting"
                    aria-selected="false"
                    type="button"
                ><?php esc_html_e('工作照', 'wqs-archive'); ?></button>
            </div>
        </div>

        <hr class="wq-archive__rule wq-archive__rule--medium">

        <!-- 下拉筛选 -->
        <div class="wq-archive__dropdowns">
            <div class="wq-archive__dropdown-wrap">
                <label for="wq-archive-type-filter" class="wq-archive__filter-label">
                    <?php esc_html_e('媒介', 'wqs-archive'); ?>
                </label>
                <select
                    id="wq-archive-type-filter"
                    class="wq-archive__select"
                    aria-label="<?php esc_attr_e('按媒介筛选', 'wqs-archive'); ?>"
                >
                    <option value=""><?php esc_html_e('全部媒介', 'wqs-archive'); ?></option>
                </select>
            </div>

            <div class="wq-archive__dropdown-wrap">
                <label for="wq-archive-year-filter" class="wq-archive__filter-label">
                    <?php esc_html_e('年份', 'wqs-archive'); ?>
                </label>
                <select
                    id="wq-archive-year-filter"
                    class="wq-archive__select"
                    aria-label="<?php esc_attr_e('按年份筛选', 'wqs-archive'); ?>"
                >
                    <option value=""><?php esc_html_e('全部年份', 'wqs-archive'); ?></option>
                </select>
            </div>
        </div>

        <hr class="wq-archive__rule wq-archive__rule--medium">

    </section>

    <!-- ================================================
         结果统计区
         ================================================ -->
    <div class="wq-archive__results-meta" aria-live="polite">
        <span class="wq-archive__results-count" id="wq-archive-results-count">
            <?php esc_html_e('加载中...', 'wqs-archive'); ?>
        </span>
    </div>

    <!-- ================================================
         AJAX 结果网格
         ================================================ -->
    <main class="wq-archive__grid-container" aria-label="<?php esc_attr_e('作品网格', 'wqs-archive'); ?>">
        <div class="wq-archive__grid" id="wq-archive-grid">
            <div class="wq-archive__loading" aria-busy="true">
                <span class="wq-archive__loading-text"><?php esc_html_e('加载中...', 'wqs-archive'); ?></span>
            </div>
        </div>

        <div class="wq-archive__no-results" id="wq-archive-no-results" hidden>
            <p><?php esc_html_e('未找到匹配的内容，请尝试其他筛选条件。', 'wqs-archive'); ?></p>
        </div>
    </main>

    <!-- ================================================
         加载更多
         ================================================ -->
    <div class="wq-archive__pagination" id="wq-archive-pagination" hidden>
        <button class="wq-archive__load-more" id="wq-archive-load-more" type="button">
            <?php esc_html_e('加载更多', 'wqs-archive'); ?>
        </button>
    </div>

</div><!-- .wq-archive -->

<?php get_footer();
