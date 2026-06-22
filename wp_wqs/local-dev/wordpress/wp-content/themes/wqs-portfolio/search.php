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
$group_ids = array_fill_keys(array_keys($groups), array());
$language_result_ids = array();
$selected_group = isset($_GET['wqs_group']) ? sanitize_key(wp_unslash($_GET['wqs_group'])) : '';
if (!isset($groups[$selected_group])) {
    $selected_group = '';
}
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
    $language_result_ids[] = $post_id;
    $post_terms = wp_get_post_terms($post_id, 'category');
    if (is_wp_error($post_terms)) {
        continue;
    }
    foreach ($post_terms as $term) {
        $group = wqs_get_archive_group_for_term($term);
        if (isset($counts[$group])) {
            $counts[$group]++;
            $group_ids[$group][] = $post_id;
            break;
        }
    }
}

$selected_ids = $selected_group !== '' ? $group_ids[$selected_group] : $language_result_ids;
$paged = max(1, (int) get_query_var('paged'));
$results_query = new WP_Query(array(
    'post_type'           => 'post',
    'post_status'         => 'publish',
    'posts_per_page'      => 24,
    'paged'               => $paged,
    'ignore_sticky_posts' => true,
    'lang'                => '',
    'suppress_filters'    => true,
    'post__in'            => !empty($selected_ids) ? $selected_ids : array(0),
    'orderby'             => 'post__in',
));
$result_total = count($selected_ids);

$search_filter_url = static function ($search_term, $group = '') {
    $args = array('s' => $search_term);
    if ($group !== '') {
        $args['wqs_group'] = $group;
    }
    if (function_exists('pll_current_language')) {
        $args['lang'] = wqs_get_current_language();
    }

    return add_query_arg($args, home_url('/'));
};
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
                        $result_total
                    );
                    ?>
                </strong>
                <div class="wqs-search-summary__counts">
                    <?php foreach ($groups as $group => $label) : ?>
                        <a class="<?php echo $selected_group === $group ? 'is-active' : ''; ?>" href="<?php echo esc_url($search_filter_url($search_term, $group)); ?>"<?php echo $selected_group === $group ? ' aria-current="page"' : ''; ?>>
                            <b><?php echo esc_html($counts[$group]); ?></b>
                            <span><?php echo esc_html($label); ?></span>
                        </a>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>

        <?php if ($results_query->have_posts()) : ?>
            <div class="works-grid wqs-search-grid">
                <?php
                $index = 0;
                while ($results_query->have_posts()) :
                    $results_query->the_post();
                    $index++;
                    wqs_render_archive_grid_item($index);
                endwhile;
                ?>
            </div>
            <div class="posts-pagination">
                <?php
                echo paginate_links(array(
                    'total'     => $results_query->max_num_pages,
                    'current'   => $paged,
                    'mid_size'  => 2,
                    'prev_text' => '&larr;',
                    'next_text' => '&rarr;',
                    'add_args'  => array_filter(array(
                        's'         => $search_term,
                        'wqs_group' => $selected_group,
                        'lang'      => function_exists('pll_current_language') ? wqs_get_current_language() : '',
                    )),
                ));
                ?>
            </div>
        <?php else : ?>
            <p class="no-results"><?php echo esc_html($is_zh ? '没有找到相关内容。' : 'No matching content was found.'); ?></p>
        <?php endif; ?>
        <?php wp_reset_postdata(); ?>
    </div>
</main>

<?php get_footer(); ?>
