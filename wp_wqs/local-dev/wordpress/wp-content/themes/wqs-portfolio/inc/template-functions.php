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
 * Archive sidebar groups and their category roots.
 */
function wqs_get_archive_sidebar_groups()
{
    return array(
        'photography' => array(
            'option'      => 'wqs_photography_categories',
            'title'       => __('Photography', 'wqs-portfolio'),
            'description' => __('Photography works from 1997 to present', 'wqs-portfolio'),
            'empty'       => __('No works found.', 'wqs-portfolio'),
            'mode'        => 'grid',
            'roots'       => array(
                'en' => array('photography-en', 'photography'),
                'zh' => array('photography-zh', 'photography'),
            ),
            'keywords'    => array('photography', '摄影'),
        ),
        'exhibitions' => array(
            'option'      => 'wqs_exhibition_categories',
            'title'       => __('Exhibitions', 'wqs-portfolio'),
            'description' => __('Exhibition history', 'wqs-portfolio'),
            'empty'       => __('No exhibitions found.', 'wqs-portfolio'),
            'mode'        => 'grid',
            'roots'       => array(
                'en' => array('exhibitions-en', 'exhibitions'),
                'zh' => array('exhibitions', 'exhibitions-zh'),
            ),
            'keywords'    => array('exhibition', '展览'),
        ),
        'shooting' => array(
            'option'      => 'wqs_shooting_categories',
            'title'       => __('Shooting', 'wqs-portfolio'),
            'description' => __('Behind the scenes', 'wqs-portfolio'),
            'empty'       => __('No works found.', 'wqs-portfolio'),
            'mode'        => 'grid',
            'roots'       => array(
                'en' => array('shooting-en', 'shooting'),
                'zh' => array('shooting', 'shooting-zh'),
            ),
            'keywords'    => array('shooting', '工作照'),
        ),
        'reviews' => array(
            'option'      => 'wqs_review_categories',
            'title'       => __('Reviews', 'wqs-portfolio'),
            'description' => __('Press and media coverage', 'wqs-portfolio'),
            'empty'       => __('No reviews found.', 'wqs-portfolio'),
            'mode'        => 'reviews',
            'roots'       => array(
                'en' => array('reviews-en', 'reviews'),
                'zh' => array('reviews', 'reviews-zh'),
            ),
            'keywords'    => array('review', '评论'),
        ),
    );
}

/**
 * Parse configured archive sidebar category slugs for a group.
 */
function wqs_get_archive_configured_category_slugs($group)
{
    $groups = wqs_get_archive_sidebar_groups();
    if (empty($groups[$group]['option'])) {
        return array();
    }

    $setting = get_option($groups[$group]['option'], '');
    if (empty($setting) || !is_string($setting)) {
        return array();
    }

    $slugs = preg_split('/[\s,]+/', $setting);
    $slugs = array_filter(array_map('sanitize_title', $slugs));

    return array_values(array_unique($slugs));
}

/**
 * Return a category term by the first matching slug.
 */
function wqs_get_category_term_by_slugs($slugs)
{
    foreach ((array) $slugs as $slug) {
        $term = null;
        $terms = get_terms(array(
            'taxonomy'   => 'category',
            'slug'       => sanitize_title($slug),
            'hide_empty' => false,
            'number'     => 1,
            'lang'       => '',
        ));

        if (!is_wp_error($terms) && !empty($terms)) {
            $term = $terms[0];
        }

        if ($term && !is_wp_error($term)) {
            return $term;
        }
    }

    return null;
}

/**
 * Find the translated version of a category term.
 */
function wqs_get_category_term_for_language($term, $lang = null)
{
    if (!$term || is_wp_error($term)) {
        return null;
    }

    if ($lang === null) {
        $lang = wqs_get_current_language();
    }

    if (function_exists('pll_get_term')) {
        $translated_id = pll_get_term($term->term_id, $lang);
        if (!empty($translated_id)) {
            $translated = get_term((int) $translated_id, 'category');
            if ($translated && !is_wp_error($translated)) {
                return $translated;
            }
        }
    }

    $slug = $term->slug;
    $base_slug = preg_replace('/-(en|zh)$/', '', $slug);
    $candidates = array($slug);

    if ($lang === 'en') {
        $candidates[] = $base_slug . '-en';
        $candidates[] = $base_slug;
    } elseif ($lang === 'zh') {
        $candidates[] = $base_slug;
        $candidates[] = $base_slug . '-zh';
    }

    $translated = wqs_get_category_term_by_slugs(array_unique($candidates));

    return $translated ? $translated : $term;
}

/**
 * Add a category term to a keyed list.
 */
function wqs_add_related_category_term(&$terms, $term)
{
    if (!$term || is_wp_error($term)) {
        return;
    }

    $terms[(int) $term->term_id] = $term;
}

/**
 * Get all known language/original variants for a category term.
 */
function wqs_get_related_category_terms($term)
{
    $terms = array();
    if (!$term || is_wp_error($term)) {
        return $terms;
    }

    wqs_add_related_category_term($terms, $term);

    if (function_exists('pll_get_term')) {
        foreach (array('en', 'zh') as $lang) {
            $translated_id = pll_get_term($term->term_id, $lang);
            if (!empty($translated_id)) {
                wqs_add_related_category_term($terms, get_term((int) $translated_id, 'category'));
            }
        }
    }

    $base_slug = preg_replace('/-(en|zh)$/', '', $term->slug);
    $candidate_slugs = array($term->slug, $base_slug, $base_slug . '-en', $base_slug . '-zh');
    foreach (array_unique($candidate_slugs) as $slug) {
        wqs_add_related_category_term($terms, wqs_get_category_term_by_slugs(array($slug)));
    }

    return $terms;
}

/**
 * Whether a queried term is one of the configured root terms for an archive group.
 */
function wqs_is_archive_root_term($group, $term)
{
    if (!$term || is_wp_error($term)) {
        return true;
    }

    $groups = wqs_get_archive_sidebar_groups();
    if (empty($groups[$group]['roots'])) {
        return false;
    }

    foreach ($groups[$group]['roots'] as $slugs) {
        foreach ($slugs as $slug) {
            $root = wqs_get_category_term_by_slugs(array($slug));
            foreach (wqs_get_related_category_terms($root) as $related_root) {
                if ((int) $related_root->term_id === (int) $term->term_id) {
                    return true;
                }
            }
        }
    }

    return false;
}

/**
 * Get category IDs that should feed an archive page.
 */
function wqs_get_archive_content_term_ids($group, $current_term = null)
{
    $groups = wqs_get_archive_sidebar_groups();
    if (empty($groups[$group])) {
        return array();
    }

    $lang = wqs_get_current_language();
    $terms = array();
    $is_root_archive = !$current_term || wqs_is_archive_root_term($group, $current_term);

    if ($is_root_archive) {
        foreach ($groups[$group]['roots'] as $slugs) {
            foreach ($slugs as $slug) {
                foreach (wqs_get_related_category_terms(wqs_get_category_term_by_slugs(array($slug))) as $term) {
                    wqs_add_related_category_term($terms, $term);
                }
            }
        }
    } else {
        foreach (wqs_get_related_category_terms($current_term) as $term) {
            wqs_add_related_category_term($terms, $term);
        }
    }

    foreach (wqs_get_related_category_terms(wqs_get_archive_root_term($group, $lang)) as $term) {
        wqs_add_related_category_term($terms, $term);
    }

    return array_keys($terms);
}

/**
 * Build the archive query, including migrated cross-language categories.
 */
function wqs_get_category_archive_query($group, $current_term = null)
{
    $term_ids = wqs_get_archive_content_term_ids($group, $current_term);
    if (empty($term_ids)) {
        return array('query' => new WP_Query(array('post__in' => array(0))), 'type' => 'post');
    }

    $base_args = array(
        'post_status'         => 'publish',
        'posts_per_page'      => -1,
        'orderby'             => 'date',
        'order'               => 'DESC',
        'ignore_sticky_posts' => true,
        'lang'                => '',
        'tax_query'           => array(
            array(
                'taxonomy'         => 'category',
                'field'            => 'term_id',
                'terms'            => $term_ids,
                'include_children' => true,
            ),
        ),
    );

    $post_query = new WP_Query(array_merge($base_args, array('post_type' => 'post')));
    if ($post_query->have_posts()) {
        return array('query' => $post_query, 'type' => 'post');
    }

    wp_reset_postdata();

    $media_query = new WP_Query(array_merge($base_args, array(
        'post_type'      => 'attachment',
        'post_status'    => 'inherit',
        'post_mime_type' => 'image',
    )));

    return array('query' => $media_query, 'type' => 'media');
}

/**
 * Get the root category for an archive group in the current language.
 */
function wqs_get_archive_root_term($group, $lang = null)
{
    $groups = wqs_get_archive_sidebar_groups();
    if (empty($groups[$group])) {
        return null;
    }

    if ($lang === null) {
        $lang = wqs_get_current_language();
    }

    $root_slugs = array();
    if (!empty($groups[$group]['roots'][$lang])) {
        $root_slugs = array_merge($root_slugs, $groups[$group]['roots'][$lang]);
    }
    foreach ($groups[$group]['roots'] as $slugs) {
        $root_slugs = array_merge($root_slugs, $slugs);
    }

    $term = wqs_get_category_term_by_slugs(array_unique($root_slugs));
    if (!$term) {
        return null;
    }

    return wqs_get_category_term_for_language($term, $lang);
}

/**
 * Sort archive sidebar terms by year when present, newest first.
 */
function wqs_sort_archive_sidebar_terms($terms)
{
    usort($terms, function ($a, $b) {
        preg_match('/(\d{2,4})/', $a->name . ' ' . $a->slug, $a_matches);
        preg_match('/(\d{2,4})/', $b->name . ' ' . $b->slug, $b_matches);

        $a_year = isset($a_matches[1]) ? (int) (strlen($a_matches[1]) === 2 ? '20' . $a_matches[1] : $a_matches[1]) : 0;
        $b_year = isset($b_matches[1]) ? (int) (strlen($b_matches[1]) === 2 ? '20' . $b_matches[1] : $b_matches[1]) : 0;

        if ($a_year !== $b_year) {
            return $b_year - $a_year;
        }

        return strcasecmp($a->name, $b->name);
    });

    return $terms;
}

/**
 * Get sidebar terms for an archive group.
 */
function wqs_get_archive_sidebar_terms($group, $lang = null)
{
    $groups = wqs_get_archive_sidebar_groups();
    if (empty($groups[$group])) {
        return array();
    }

    if ($lang === null) {
        $lang = wqs_get_current_language();
    }

    $terms = array();
    $seen = array();
    $configured_slugs = wqs_get_archive_configured_category_slugs($group);
    $root_term = wqs_get_archive_root_term($group, $lang);

    if (!empty($configured_slugs)) {
        foreach ($configured_slugs as $slug) {
            $term = wqs_get_category_term_by_slugs(array($slug));
            $term = wqs_get_category_term_for_language($term, $lang);
            if (!$term || is_wp_error($term)) {
                continue;
            }

            if ($root_term && (int) $term->term_id === (int) $root_term->term_id && wqs_show_all_categories()) {
                continue;
            }

            if (!isset($seen[$term->term_id])) {
                $terms[] = $term;
                $seen[$term->term_id] = true;
            }
        }

        return $terms;
    }

    if ($root_term) {
        $children = get_terms(array(
            'taxonomy'   => 'category',
            'hide_empty' => true,
            'parent'     => $root_term->term_id,
            'orderby'    => 'name',
            'order'      => 'ASC',
        ));

        if (!is_wp_error($children) && !empty($children)) {
            return wqs_sort_archive_sidebar_terms($children);
        }
    }

    $all_terms = get_terms(array(
        'taxonomy'   => 'category',
        'hide_empty' => true,
        'orderby'    => 'name',
        'order'      => 'ASC',
    ));

    if (is_wp_error($all_terms) || empty($all_terms)) {
        return array();
    }

    foreach ($all_terms as $term) {
        foreach ($groups[$group]['keywords'] as $keyword) {
            if (stripos($term->slug, $keyword) !== false || stripos($term->name, $keyword) !== false) {
                $localized = wqs_get_category_term_for_language($term, $lang);
                if ($root_term && $localized && (int) $localized->term_id === (int) $root_term->term_id && wqs_show_all_categories()) {
                    break;
                }
                if ($localized && !isset($seen[$localized->term_id])) {
                    $terms[] = $localized;
                    $seen[$localized->term_id] = true;
                }
                break;
            }
        }
    }

    return wqs_sort_archive_sidebar_terms($terms);
}

/**
 * Render archive sidebar links from Appearance > Archive Sidebar settings.
 */
function wqs_render_archive_sidebar($group, $title = '')
{
    $groups = wqs_get_archive_sidebar_groups();
    if (empty($groups[$group])) {
        return;
    }

    $lang = wqs_get_current_language();
    $root_term = wqs_get_archive_root_term($group, $lang);
    $terms = wqs_get_archive_sidebar_terms($group, $lang);
    $current_term = is_category() ? get_queried_object() : null;
    $title = $title ? $title : $groups[$group]['title'];
    ?>
    <aside class="archive-sidebar">
        <nav class="archive-submenu">
            <h3 class="submenu-title"><?php echo esc_html($title); ?></h3>
            <ul class="submenu-list">
                <?php if (wqs_show_all_categories() && $root_term) : ?>
                    <?php
                    $all_url = get_term_link($root_term, 'category');
                    $is_all_active = $current_term && (int) $current_term->term_id === (int) $root_term->term_id;
                    ?>
                    <?php if (!is_wp_error($all_url)) : ?>
                    <li class="submenu-item">
                        <a href="<?php echo esc_url($all_url); ?>" class="submenu-link<?php echo $is_all_active ? ' active' : ''; ?>"<?php echo $is_all_active ? ' aria-current="page"' : ''; ?>>
                            <?php esc_html_e('All', 'wqs-portfolio'); ?>
                        </a>
                    </li>
                    <?php endif; ?>
                <?php endif; ?>

                <?php foreach ($terms as $term) : ?>
                    <?php
                    $term_url = get_term_link($term, 'category');
                    if (is_wp_error($term_url)) {
                        continue;
                    }
                    $is_active = $current_term && (int) $current_term->term_id === (int) $term->term_id;
                    ?>
                    <li class="submenu-item">
                        <a href="<?php echo esc_url($term_url); ?>" class="submenu-link<?php echo $is_active ? ' active' : ''; ?>"<?php echo $is_active ? ' aria-current="page"' : ''; ?>>
                            <?php echo esc_html($term->name); ?>
                        </a>
                    </li>
                <?php endforeach; ?>
            </ul>
        </nav>
    </aside>
    <?php
}

/**
 * Get the configured archive group that owns a category term.
 */
function wqs_get_archive_group_for_term($term)
{
    if (!$term || is_wp_error($term)) {
        return '';
    }

    $groups = wqs_get_archive_sidebar_groups();
    foreach ($groups as $group => $config) {
        foreach (array_keys($config['roots']) as $lang) {
            $root = wqs_get_archive_root_term($group, $lang);
            if (!$root) {
                continue;
            }

            if ((int) $term->term_id === (int) $root->term_id || cat_is_ancestor_of($root->term_id, $term->term_id)) {
                return $group;
            }
        }

        $configured_terms = wqs_get_archive_sidebar_terms($group);
        foreach ($configured_terms as $configured_term) {
            if ((int) $term->term_id === (int) $configured_term->term_id) {
                return $group;
            }
        }

        foreach ($config['keywords'] as $keyword) {
            if (stripos($term->slug, $keyword) !== false || stripos($term->name, $keyword) !== false) {
                return $group;
            }
        }
    }

    return '';
}

/**
 * Render one grid item in category archives.
 */
function wqs_render_archive_grid_item($index)
{
    $post_year = get_the_date('Y');
    $item_cats = get_the_category();
    $cat_slugs = array();

    if ($item_cats) {
        foreach ($item_cats as $cat) {
            $cat_slugs[] = $cat->slug;
        }
    }

    $thumb_url = '';
    $thumb_width = 0;
    $thumb_height = 0;
    $is_extreme = false;

    if (has_post_thumbnail()) {
        $thumb_data = wp_get_attachment_image_src(get_post_thumbnail_id(), 'large');
        if ($thumb_data) {
            $thumb_url = $thumb_data[0];
            $thumb_width = $thumb_data[1];
            $thumb_height = $thumb_data[2];
            $is_extreme = wqs_is_extreme_aspect_ratio($thumb_width, $thumb_height);
        }
    }

    if (empty($thumb_url)) {
        $first_image = wqs_get_first_content_image(get_the_ID());
        if ($first_image && $first_image['url']) {
            $thumb_url = $first_image['url'];
            $thumb_width = $first_image['width'];
            $thumb_height = $first_image['height'];
            $is_extreme = wqs_is_extreme_aspect_ratio($thumb_width, $thumb_height);
        }
    }
    ?>
    <article id="post-<?php the_ID(); ?>" <?php post_class('works-item archive-item'); ?>
             data-aos="fade-up"
             data-aos-delay="<?php echo esc_attr(($index % 4) * 100); ?>"
             data-year="<?php echo esc_attr($post_year); ?>"
             data-title="<?php echo esc_attr(strtolower(get_the_title())); ?>"
             data-categories="<?php echo esc_attr(implode(',', $cat_slugs)); ?>">
        <div class="works-item-thumbnail">
            <a href="<?php the_permalink(); ?>">
                <?php if ($thumb_url) : ?>
                    <img src="<?php echo esc_url($thumb_url); ?>"
                         alt="<?php echo esc_attr(get_the_title()); ?>"
                         class="<?php echo $is_extreme ? 'extreme-aspect' : ''; ?>"
                         loading="lazy">
                <?php else : ?>
                    <img src="https://picsum.photos/800/600?grayscale" alt="<?php echo esc_attr(get_the_title()); ?>">
                <?php endif; ?>
            </a>
        </div>
        <div class="works-item-content">
            <h3 class="works-item-title">
                <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
            </h3>
            <span class="works-item-year"><?php echo esc_html($post_year); ?></span>
        </div>
    </article>
    <?php
}

/**
 * Render one media fallback grid item in category archives.
 */
function wqs_render_archive_media_grid_item($index)
{
    $attachment_id = get_the_ID();
    $post_year = get_the_date('Y');
    $image = wp_get_attachment_image_src($attachment_id, 'large');
    $full_url = wp_get_attachment_url($attachment_id);
    $thumb_url = $image ? $image[0] : $full_url;
    $thumb_width = $image ? $image[1] : 0;
    $thumb_height = $image ? $image[2] : 0;
    $is_extreme = wqs_is_extreme_aspect_ratio($thumb_width, $thumb_height);
    ?>
    <article id="post-<?php the_ID(); ?>" <?php post_class('works-item archive-item archive-media-item'); ?>
             data-aos="fade-up"
             data-aos-delay="<?php echo esc_attr(($index % 4) * 100); ?>"
             data-year="<?php echo esc_attr($post_year); ?>"
             data-title="<?php echo esc_attr(strtolower(get_the_title())); ?>">
        <div class="works-item-thumbnail">
            <a href="<?php echo esc_url($full_url); ?>">
                <?php if ($thumb_url) : ?>
                    <img src="<?php echo esc_url($thumb_url); ?>"
                         alt="<?php echo esc_attr(get_the_title()); ?>"
                         class="<?php echo $is_extreme ? 'extreme-aspect' : ''; ?>"
                         loading="lazy">
                <?php endif; ?>
            </a>
        </div>
        <div class="works-item-content">
            <h3 class="works-item-title">
                <a href="<?php echo esc_url($full_url); ?>"><?php the_title(); ?></a>
            </h3>
            <span class="works-item-year"><?php echo esc_html($post_year); ?></span>
        </div>
    </article>
    <?php
}

/**
 * Render AOS setup for archive templates.
 */
function wqs_render_archive_aos_script()
{
    ?>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof AOS !== 'undefined') {
            AOS.init({ duration: 800, easing: 'ease-out-cubic', once: true, offset: 50 });
        }

        // Archive filter bar
        var filterBar = document.querySelector('.archive-filter-bar');
        if (filterBar) {
            var searchInput = filterBar.querySelector('.filter-search-input');
            var yearSelect = filterBar.querySelector('.filter-year-select');
            var clearBtn = filterBar.querySelector('.filter-search-clear');
            var countVisible = filterBar.querySelector('.filter-count-visible');
            var countTotal = filterBar.querySelector('.filter-count-total');
            var archiveItems = document.querySelectorAll('.archive-item');
            var group = filterBar.getAttribute('data-group');

            // Set total count
            if (countTotal) {
                countTotal.textContent = archiveItems.length;
            }

            function applyFilter() {
                var keyword = searchInput.value.trim().toLowerCase();
                var selectedYear = yearSelect ? yearSelect.value : 'all';
                var visibleCount = 0;

                clearBtn.classList.toggle('visible', keyword.length > 0);

                archiveItems.forEach(function(item) {
                    var itemYear = item.getAttribute('data-year') || '';
                    var itemTitle = item.getAttribute('data-title') || '';
                    var itemContent = '';
                    var itemExcerpt = item.querySelector('.review-title') || item.querySelector('.works-item-title');
                    if (itemExcerpt) {
                        itemContent = itemExcerpt.textContent.toLowerCase();
                    }

                    var matchYear = (selectedYear === 'all' || itemYear === selectedYear);
                    var matchSearch = (keyword.length === 0 || itemTitle.includes(keyword) || itemContent.includes(keyword));

                    if (matchYear && matchSearch) {
                        item.classList.remove('hidden-by-filter');
                        visibleCount++;
                    } else {
                        item.classList.add('hidden-by-filter');
                    }
                });

                if (countVisible) {
                    countVisible.textContent = visibleCount;
                }

                // Trigger AOS refresh if available
                if (typeof AOS !== 'undefined') {
                    AOS.refresh();
                }

                // Hide pagination when filtering
                var pagination = document.querySelector('.posts-pagination');
                if (pagination) {
                    pagination.style.display = (keyword.length > 0 || selectedYear !== 'all') ? 'none' : '';
                }
            }

            searchInput.addEventListener('input', applyFilter);
            if (yearSelect) {
                yearSelect.addEventListener('change', applyFilter);
            }
            if (clearBtn) {
                clearBtn.addEventListener('click', function() {
                    searchInput.value = '';
                    applyFilter();
                    searchInput.focus();
                });
            }

            // Initial count
            applyFilter();
        }
    });
    </script>
    <?php
}

/**
 * Render a configured category archive page.
 */
function wqs_render_category_archive($group, $args = array())
{
    $groups = wqs_get_archive_sidebar_groups();
    if (empty($groups[$group])) {
        return;
    }

    $config = wp_parse_args($args, $groups[$group]);
    $current_term = is_category() ? get_queried_object() : null;
    $root_term = wqs_get_archive_root_term($group);
    $heading = $config['title'];

    if ($current_term && (!$root_term || (int) $current_term->term_id !== (int) $root_term->term_id)) {
        $heading = $current_term->name;
    }

    $main_classes = 'site-main archive-with-sidebar';
    if ($config['mode'] === 'reviews') {
        $main_classes .= ' reviews-archive';
    }

    $archive_result = wqs_get_category_archive_query($group, $current_term);
    $archive_query = $archive_result['query'];
    $archive_item_type = $archive_result['type'];
    ?>
    <main id="main-content" class="<?php echo esc_attr($main_classes); ?>">
        <div class="archive-layout">
            <?php wqs_render_archive_sidebar($group, $config['title']); ?>

            <div class="archive-content">
                <header class="archive-header" data-aos="fade-up">
                    <h1><?php echo esc_html($heading); ?></h1>
                    <p class="archive-description">
                        <?php echo esc_html($config['description']); ?>
                    </p>
                </header>

                <?php if ($archive_query->have_posts()) : ?>
                    <?php
                    // Collect all years from posts for the filter dropdown
                    $post_years = array();
                    $first_post_year = null;
                    while ($archive_query->have_posts()) : $archive_query->the_post();
                        $y = get_the_date('Y');
                        if ($first_post_year === null) $first_post_year = $y;
                        $post_years[$y] = $y;
                    endwhile;
                    $post_years = array_unique($post_years);
                    arsort($post_years);
                    $archive_query->rewind_posts();

                    // Collect all post titles for smart search
                    $post_titles = array();
                    while ($archive_query->have_posts()) : $archive_query->the_post();
                        $post_titles[] = strtolower(get_the_title());
                    endwhile;
                    $archive_query->rewind_posts();
                    ?>

                    <div class="archive-filter-bar" data-group="<?php echo esc_attr($group); ?>">
                        <div class="filter-search-wrap">
                            <label for="archive-search-<?php echo esc_attr($group); ?>" class="sr-only"><?php esc_html_e('Search works', 'wqs-portfolio'); ?></label>
                            <input type="text" id="archive-search-<?php echo esc_attr($group); ?>" class="filter-search-input" placeholder="<?php esc_attr_e('Search works...', 'wqs-portfolio'); ?>" autocomplete="off" aria-label="<?php esc_attr_e('Search works', 'wqs-portfolio'); ?>">
                            <button type="button" class="filter-search-clear" title="<?php esc_attr_e('Clear search', 'wqs-portfolio'); ?>" aria-label="<?php esc_attr_e('Clear search', 'wqs-portfolio'); ?>">&times;</button>
                        </div>
                        <label for="archive-year-<?php echo esc_attr($group); ?>" class="sr-only"><?php esc_html_e('Filter by year', 'wqs-portfolio'); ?></label>
                        <select id="archive-year-<?php echo esc_attr($group); ?>" class="filter-year-select" aria-label="<?php esc_attr_e('Filter by year', 'wqs-portfolio'); ?>">
                            <option value="all"><?php esc_html_e('All Years', 'wqs-portfolio'); ?></option>
                            <?php foreach ($post_years as $year) : ?>
                                <option value="<?php echo esc_attr($year); ?>"><?php echo esc_html($year); ?></option>
                            <?php endforeach; ?>
                        </select>
                        <span class="filter-results-count" aria-live="polite" aria-atomic="true">
                            <span class="filter-count-visible">0</span> / <span class="filter-count-total">0</span>
                        </span>
                    </div>

                    <?php if ($config['mode'] === 'reviews' && $archive_item_type === 'post') : ?>
                        <div class="reviews-list" data-aos="fade-up" data-aos-delay="200">
                            <?php while ($archive_query->have_posts()) : $archive_query->the_post(); ?>
                                <?php $post_year = get_the_date('Y'); ?>
                                <article id="post-<?php the_ID(); ?>" <?php post_class('review-item archive-item'); ?>
                                         data-year="<?php echo esc_attr($post_year); ?>"
                                         data-title="<?php echo esc_attr(strtolower(get_the_title())); ?>">
                                    <div class="review-date"><?php echo esc_html(get_the_date('Y.m.d')); ?></div>
                                    <h2 class="review-title">
                                        <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                                    </h2>
                                </article>
                            <?php endwhile; ?>
                        </div>
                    <?php else : ?>
                        <div class="works-grid archive-grid">
                            <?php
                            $i = 0;
                            while ($archive_query->have_posts()) :
                                $archive_query->the_post();
                                $i++;
                                if ($archive_item_type === 'media') {
                                    wqs_render_archive_media_grid_item($i);
                                } else {
                                    wqs_render_archive_grid_item($i);
                                }
                            endwhile;
                            ?>
                        </div>
                    <?php endif; ?>

                    <?php wp_reset_postdata(); ?>
                <?php else : ?>
                    <p class="no-results"><?php echo esc_html($config['empty']); ?></p>
                <?php endif; ?>
            </div>
        </div>
    </main>
    <?php
    wqs_render_archive_aos_script();
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
