<?php
/**
 * Search results template.
 *
 * @package WQS_Portfolio
 */

get_header();

$search_term = get_search_query();
$is_zh = wqs_get_current_language() === 'zh';
$groups = array(
    'photography' => $is_zh ? '摄影' : 'Photography',
    'exhibitions' => $is_zh ? '展览' : 'Exhibitions',
    'reviews' => $is_zh ? '评论' : 'Reviews',
    'shooting' => $is_zh ? '工作照' : 'Shooting',
);
$counts = array_fill_keys(array_keys($groups), 0);
$other_count = 0;
$search_ids = get_posts(array(
    'post_type'        => 'post',
    'post_status'      => 'publish',
    'posts_per_page'   => -1,
    'fields'           => 'ids',
    's'                => $search_term,
    'lang'             => '',
    'suppress_filters' => true,
));

foreach ($search_ids as $post_id) {
    if (wqs_get_effective_post_language($post_id) !== wqs_get_current_language()) {
        continue;
    }
    $post_terms = wp_get_post_terms($post_id, 'category');
    if (is_wp_error($post_terms)) {
        continue;
    }
    $matched_group = false;
    foreach ($post_terms as $term) {
        $group = wqs_get_archive_group_for_term($term);
        if (isset($counts[$group])) {
            $counts[$group]++;
            $matched_group = true;
            break;
        }
    }
    if (!$matched_group) {
        $other_count++;
    }
}
?>

<main id="main-content" class="site-main wqs-search-results">
    <div class="container">
        <section class="wqs-search-summary">
            <form role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>">
                <label for="wqs-results-search"><?php echo esc_html($is_zh ? '搜索结果' : 'Search results'); ?></label>
                <div class="wqs-search-summary__field">
                    <input id="wqs-results-search" type="search" name="s" value="<?php echo esc_attr($search_term); ?>" aria-label="<?php echo esc_attr($is_zh ? '重新搜索' : 'Search again'); ?>">
                    <button type="submit" aria-label="<?php echo esc_attr($is_zh ? '搜索' : 'Search'); ?>">&#8594;</button>
                </div>
                <?php if (function_exists('pll_current_language')) : ?>
                    <input type="hidden" name="lang" value="<?php echo esc_attr(wqs_get_current_language()); ?>">
                <?php endif; ?>
            </form>
            <div class="wqs-search-summary__meta">
                <strong>
                    <?php
                    printf(
                        esc_html($is_zh ? '“%1$s”共找到 %2$d 个结果' : '%2$d results for “%1$s”'),
                        esc_html($search_term),
                        (int) $wp_query->found_posts
                    );
                    ?>
                </strong>
                <div class="wqs-search-summary__counts">
                    <?php foreach ($groups as $group => $label) : ?>
                        <span><b><?php echo esc_html($counts[$group]); ?></b><?php echo esc_html($label); ?></span>
                    <?php endforeach; ?>
                    <?php if ($other_count > 0) : ?>
                        <span><b><?php echo esc_html($other_count); ?></b><?php echo esc_html($is_zh ? '其他' : 'Other'); ?></span>
                    <?php endif; ?>
                </div>
            </div>
        </section>

        <?php if (have_posts()) : ?>
            <div class="works-grid wqs-search-grid">
                <?php
                $index = 0;
                while (have_posts()) :
                    the_post();
                    $index++;
                    wqs_render_archive_grid_item($index);
                endwhile;
                ?>
            </div>
            <div class="posts-pagination">
                <?php echo paginate_links(array('mid_size' => 2, 'prev_text' => '&larr;', 'next_text' => '&rarr;')); ?>
            </div>
        <?php else : ?>
            <p class="no-results"><?php echo esc_html($is_zh ? '没有找到相关内容。' : 'No matching content was found.'); ?></p>
        <?php endif; ?>
    </div>
</main>

<?php get_footer(); ?>
