<?php
/**
 * Template Name: 王庆松艺术档案库 (MoMA Style)
 * Template Description: 复刻 MoMA Collection 风格的艺术家档案库检索与展示页面
 * Template Type: page
 *
 * @package WordPress
 * @subpackage TwentyTwentyFive
 * @since Twenty Twenty-Five 1.0
 */

// 获取所有可用的筛选选项
$item_types = get_terms(array(
    'taxonomy'   => 'item_type',
    'hide_empty' => true,
    'orderby'    => 'name',
));

$creation_years = get_terms(array(
    'taxonomy'   => 'creation_year',
    'hide_empty' => true,
    'orderby'    => 'name',
    'order'      => 'DESC',
));

// 规范化 URL 获取当前筛选状态
$current_type = isset($_GET['item_type']) ? sanitize_text_field($_GET['item_type']) : '';
$current_year = isset($_GET['creation_year']) ? sanitize_text_field($_GET['creation_year']) : '';
$current_post_type = isset($_GET['post_type']) ? sanitize_text_field($_GET['post_type']) : 'artwork';
$search_query = isset($_GET['s']) ? sanitize_text_field($_GET['s']) : '';
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?php wp_title('—', true, 'right'); bloginfo('name'); ?></title>
    <?php wp_head(); ?>
    <link rel="stylesheet" href="<?php echo esc_url(WQ_ARCHIVE_PLUGIN_URL . 'assets/css/archive.css'); ?>">
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

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
        <!-- 粗水平线分隔 -->
        <hr class="wq-archive__rule wq-archive__rule--heavy">
    </header>

    <!-- ================================================
         检索栏 (Search & Filter Bar)
         MoMA 风格：扁平化表单控件，无圆角阴影
         ================================================ -->
    <section class="wq-archive__filter-bar" aria-label="<?php esc_attr_e('筛选与搜索', 'wq-archive'); ?>">

        <!-- 搜索框 -->
        <div class="wq-archive__search-wrap">
            <label for="wq-archive-search" class="wq-archive__filter-label">
                <?php esc_html_e('搜索', 'wq-archive'); ?>
            </label>
            <input
                type="search"
                id="wq-archive-search"
                class="wq-archive__search-input"
                placeholder="<?php esc_attr_e('关键词...', 'wq-archive'); ?>"
                value="<?php echo esc_attr($search_query); ?>"
                aria-describedby="wq-archive-search-desc"
            >
        </div>

        <!-- 粗水平线分隔 -->
        <hr class="wq-archive__rule wq-archive__rule--medium">

        <!-- 内容类型切换 (Tabs) -->
        <div class="wq-archive__type-tabs" role="tablist" aria-label="<?php esc_attr_e('内容类型', 'wq-archive'); ?>">
            <span class="wq-archive__filter-label"><?php esc_html_e('类型', 'wq-archive'); ?></span>
            <div class="wq-archive__tabs-list">
                <button
                    class="wq-archive__tab wq-archive__tab--active"
                    role="tab"
                    data-post-type="artwork"
                    aria-selected="true"
                    type="button"
                ><?php esc_html_e('作品', 'wq-archive'); ?></button>
                <button
                    class="wq-archive__tab"
                    role="tab"
                    data-post-type="exhibition"
                    aria-selected="false"
                    type="button"
                ><?php esc_html_e('展览', 'wq-archive'); ?></button>
                <button
                    class="wq-archive__tab"
                    role="tab"
                    data-post-type="shooting"
                    aria-selected="false"
                    type="button"
                ><?php esc_html_e('工作照', 'wq-archive'); ?></button>
            </div>
        </div>

        <!-- 粗水平线分隔 -->
        <hr class="wq-archive__rule wq-archive__rule--medium">

        <!-- 下拉筛选 -->
        <div class="wq-archive__dropdowns">
            <!-- 媒介类型下拉 -->
            <div class="wq-archive__dropdown-wrap">
                <label for="wq-archive-type-filter" class="wq-archive__filter-label">
                    <?php esc_html_e('媒介', 'wq-archive'); ?>
                </label>
                <select
                    id="wq-archive-type-filter"
                    class="wq-archive__select"
                    aria-label="<?php esc_attr_e('按媒介筛选', 'wq-archive'); ?>"
                >
                    <option value=""><?php esc_html_e('全部媒介', 'wq-archive'); ?></option>
                    <?php if (!is_wp_error($item_types)): ?>
                        <?php foreach ($item_types as $type): ?>
                            <option value="<?php echo esc_attr($type->slug); ?>" <?php selected($current_type, $type->slug); ?>>
                                <?php echo esc_html($type->name); ?>
                            </option>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </select>
            </div>

            <!-- 年份下拉 -->
            <div class="wq-archive__dropdown-wrap">
                <label for="wq-archive-year-filter" class="wq-archive__filter-label">
                    <?php esc_html_e('年份', 'wq-archive'); ?>
                </label>
                <select
                    id="wq-archive-year-filter"
                    class="wq-archive__select"
                    aria-label="<?php esc_attr_e('按年份筛选', 'wq-archive'); ?>"
                >
                    <option value=""><?php esc_html_e('全部年份', 'wq-archive'); ?></option>
                    <?php if (!is_wp_error($creation_years)): ?>
                        <?php foreach ($creation_years as $year): ?>
                            <option value="<?php echo esc_attr($year->slug); ?>" <?php selected($current_year, $year->slug); ?>>
                                <?php echo esc_html($year->name); ?>
                            </option>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </select>
            </div>
        </div>

        <!-- 粗水平线分隔 -->
        <hr class="wq-archive__rule wq-archive__rule--medium">

    </section>

    <!-- ================================================
         结果统计区
         ================================================ -->
    <div class="wq-archive__results-meta" aria-live="polite">
        <span class="wq-archive__results-count" id="wq-archive-results-count">
            <?php
            printf(
                /* translators: %d = number of results */
                esc_html(_n('%d 项结果', '%d 项结果', 0, 'wq-archive')),
                0
            );
            ?>
        </span>
    </div>

    <!-- ================================================
         AJAX 结果网格 (Masonry / CSS Grid)
         MoMA 风格：无卡片阴影、无圆角，极简黑白对比
         ================================================ -->
    <main class="wq-archive__grid-container" aria-label="<?php esc_attr_e('作品网格', 'wq-archive'); ?>">
        <div class="wq-archive__grid" id="wq-archive-grid">
            <!-- 初始加载提示 -->
            <div class="wq-archive__loading" aria-busy="true">
                <span class="wq-archive__loading-text"><?php esc_html_e('加载中...', 'wq-archive'); ?></span>
            </div>
        </div>

        <!-- 无结果提示 -->
        <div class="wq-archive__no-results" id="wq-archive-no-results" hidden>
            <p><?php esc_html_e('未找到匹配的内容，请尝试其他筛选条件。', 'wq-archive'); ?></p>
        </div>
    </main>

    <!-- ================================================
         加载更多 / 分页
         ================================================ -->
    <div class="wq-archive__pagination" id="wq-archive-pagination" hidden>
        <button class="wq-archive__load-more" id="wq-archive-load-more" type="button">
            <?php esc_html_e('加载更多', 'wq-archive'); ?>
        </button>
    </div>

</div><!-- .wq-archive -->

<!-- 注入 AJAX 参数 -->
<script>
window.wqArchive = {
    ajaxUrl: '<?php echo esc_url(admin_url('admin-ajax.php')); ?>',
    nonce: '<?php echo esc_attr(wp_create_nonce('wq_archive_nonce')); ?>',
    currentPostType: '<?php echo esc_attr($current_post_type); ?>',
    currentType: '<?php echo esc_attr($current_type); ?>',
    currentYear: '<?php echo esc_attr($current_year); ?>',
    searchQuery: '<?php echo esc_attr($search_query); ?>'
};
</script>
<script src="<?php echo esc_url(WQ_ARCHIVE_PLUGIN_URL . 'assets/js/archive.js'); ?>"></script>

<?php wp_footer(); ?>
</body>
</html>