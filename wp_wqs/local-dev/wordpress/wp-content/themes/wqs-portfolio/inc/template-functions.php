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
            'mode'        => 'exhibitions',
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
        $configured_slugs = wqs_get_archive_configured_category_slugs($group);

        foreach ($configured_slugs as $slug) {
            foreach (wqs_get_related_category_terms(wqs_get_category_term_by_slugs(array($slug))) as $term) {
                wqs_add_related_category_term($terms, $term);
            }
        }

        if (empty($terms)) {
            foreach ($groups[$group]['roots'] as $slugs) {
                foreach ($slugs as $slug) {
                    foreach (wqs_get_related_category_terms(wqs_get_category_term_by_slugs(array($slug))) as $term) {
                        wqs_add_related_category_term($terms, $term);
                    }
                }
            }
        }
    } else {
        foreach (wqs_get_related_category_terms($current_term) as $term) {
            wqs_add_related_category_term($terms, $term);
        }
    }

    if (empty($terms)) {
        foreach (wqs_get_related_category_terms(wqs_get_archive_root_term($group, $lang)) as $term) {
            wqs_add_related_category_term($terms, $term);
        }
    }

    return array_keys($terms);
}

/**
 * Get migrated category landing posts that must not appear as archive items.
 */
function wqs_get_archive_landing_post_ids($term_ids)
{
    global $wpdb;

    $slugs = array();
    foreach ((array) $term_ids as $term_id) {
        $term = get_term((int) $term_id, 'category');
        if (!$term || is_wp_error($term)) {
            continue;
        }

        $slugs[] = $term->slug;
        $slugs[] = preg_replace('/-(en|zh)$/', '', $term->slug);
    }

    $slugs = array_values(array_unique(array_filter($slugs)));
    if (empty($slugs)) {
        return array();
    }

    $placeholders = implode(',', array_fill(0, count($slugs), '%s'));
    $sql = $wpdb->prepare(
        "SELECT ID FROM {$wpdb->posts} WHERE post_type = 'post' AND post_name IN ({$placeholders})",
        $slugs
    );

    return array_map('intval', $wpdb->get_col($sql));
}

/**
 * Get posts explicitly marked as migrated Chinese content.
 *
 * This bypasses corrupted Polylang category translation groups.
 */
function wqs_get_original_chinese_post_ids()
{
    global $wpdb;

    $sql = "
        SELECT DISTINCT tr.object_id
        FROM {$wpdb->term_relationships} tr
        INNER JOIN {$wpdb->term_taxonomy} tt
            ON tt.term_taxonomy_id = tr.term_taxonomy_id
            AND tt.taxonomy = 'category'
        INNER JOIN {$wpdb->terms} t
            ON t.term_id = tt.term_id
        WHERE t.slug = 'original-chinese'
    ";

    return array_map('intval', $wpdb->get_col($sql));
}

/**
 * Resolve the effective language of migrated posts with missing Polylang data.
 */
function wqs_get_effective_post_language($post_id)
{
    $legacy_language = get_post_meta($post_id, '_wqs_legacy_exhibition_lang', true);
    if (in_array($legacy_language, array('en', 'zh'), true)) {
        return $legacy_language;
    }

    $polylang_language = '';
    if (function_exists('pll_get_post_language')) {
        $polylang_language = pll_get_post_language($post_id, 'slug');
    }

    // Trust an explicit Polylang translation relationship even when an
    // English working title contains Chinese notes or test text.
    if (
        in_array($polylang_language, array('en', 'zh'), true) &&
        function_exists('pll_get_post_translations')
    ) {
        $translations = array_filter(array_map('absint', pll_get_post_translations($post_id)));
        if (count(array_unique($translations)) > 1) {
            return $polylang_language;
        }
    }

    // Migrated Chinese posts carry an explicit marker. The old year
    // categories themselves are not reliable language indicators because
    // many English posts still belong to categories Polylang labels Chinese.
    static $original_chinese_ids = null;
    if ($original_chinese_ids === null) {
        $original_chinese_ids = array_fill_keys(wqs_get_original_chinese_post_ids(), true);
    }

    if (isset($original_chinese_ids[(int) $post_id])) {
        return 'zh';
    }

    if (in_array($polylang_language, array('en', 'zh'), true)) {
        return $polylang_language;
    }

    // Only use category language as a fallback for posts that have no
    // Polylang language and no explicit migration marker.
    if (function_exists('pll_get_term_language')) {
        $category_languages = array();
        $categories = wp_get_post_terms($post_id, 'category');

        if (!is_wp_error($categories)) {
            foreach ($categories as $category) {
                $category_language = pll_get_term_language($category->term_id, 'slug');
                if (in_array($category_language, array('en', 'zh'), true)) {
                    $category_languages[$category_language] = true;
                }
            }
        }

        if (count($category_languages) === 1) {
            return (string) array_key_first($category_languages);
        }
    }

    $post = get_post($post_id);
    if ($post && preg_match_all('/[\x{3400}-\x{9FFF}]/u', $post->post_title) >= 2) {
        return 'zh';
    }

    return 'en';
}

/**
 * Get archive post IDs that belong to one effective language.
 */
function wqs_get_archive_language_post_ids($term_ids, $language)
{
    $post_ids = get_posts(array(
        'post_type'        => 'post',
        'post_status'      => 'publish',
        'posts_per_page'   => -1,
        'fields'           => 'ids',
        'lang'             => '',
        'suppress_filters' => true,
        'tax_query'        => array(
            array(
                'taxonomy'         => 'category',
                'field'            => 'term_id',
                'terms'            => $term_ids,
                'include_children' => true,
            ),
        ),
    ));

    return array_values(array_filter($post_ids, function ($post_id) use ($language) {
        return wqs_get_effective_post_language($post_id) === $language;
    }));
}

/**
 * Get the exact creation year stored for one archive post.
 */
function wqs_get_creation_year($post_id)
{
    $year = absint(get_post_meta($post_id, '_wqs_creation_year', true));
    if ($year >= 1900 && $year <= ((int) current_time('Y') + 10)) {
        return $year;
    }

    return (int) wqs_get_content_created_year($post_id);
}

/**
 * Convert a sidebar term into numeric creation-year bounds.
 */
function wqs_get_archive_term_year_bounds($term)
{
    if (!$term || is_wp_error($term)) {
        return array();
    }

    $base_slug = preg_replace('/-(en|zh)$/', '', $term->slug);
    $label = wqs_format_archive_year_label($base_slug);
    if (!preg_match('/^(\d{4})(?:-(\d{4}))?$/', $label, $matches)) {
        return array();
    }

    return array(
        'start' => (int) $matches[1],
        'end'   => isset($matches[2]) ? (int) $matches[2] : (int) $matches[1],
    );
}

/**
 * Build an archive query from hand-selected categories and explicit language markers.
 */
function wqs_get_category_archive_query($group, $current_term = null)
{
    $term_ids = wqs_get_archive_content_term_ids($group);
    if (empty($term_ids)) {
        return array('query' => new WP_Query(array('post__in' => array(0))), 'type' => 'post');
    }

    $tax_query = array(
        array(
            'taxonomy'         => 'category',
            'field'            => 'term_id',
            'terms'            => $term_ids,
            'include_children' => true,
        ),
    );
    $excluded_ids = wqs_get_archive_landing_post_ids($term_ids);
    $language_ids = wqs_get_archive_language_post_ids($term_ids, wqs_get_current_language());
    $included_ids = array_values(array_diff($language_ids, $excluded_ids));

    $base_args = array(
        'post_status'         => 'publish',
        'posts_per_page'      => -1,
        'ignore_sticky_posts' => true,
        'lang'                => '',
        'tax_query'           => $tax_query,
        'post__in'            => !empty($included_ids) ? $included_ids : array(0),
    );

    $year_bounds = wqs_is_archive_root_term($group, $current_term)
        ? array()
        : wqs_get_archive_term_year_bounds($current_term);

    if (!empty($year_bounds)) {
        $base_args['meta_query'] = array(
            array(
                'key'     => '_wqs_creation_year',
                'value'   => array($year_bounds['start'], $year_bounds['end']),
                'compare' => 'BETWEEN',
                'type'    => 'NUMERIC',
            ),
        );
    }

    $post_query = new WP_Query(array_merge($base_args, array(
        'post_type' => 'post',
        'meta_key'  => '_wqs_creation_year',
        'orderby'   => array(
            'meta_value_num' => 'DESC',
            'date'           => 'DESC',
        ),
    )));
    if ($post_query->have_posts()) {
        return array('query' => $post_query, 'type' => 'post');
    }

    wp_reset_postdata();

    $media_query = new WP_Query(array_merge($base_args, array(
        'post_type'      => 'attachment',
        'post_status'    => 'inherit',
        'post_mime_type' => 'image',
        'orderby'        => 'date',
        'order'          => 'DESC',
    )));

    return array('query' => $media_query, 'type' => 'media');
}

/**
 * Format the year or year range encoded in a configured category.
 */
function wqs_format_archive_year_label($value)
{
    if (!preg_match('/^(\d{2,4})(?:-(\d{2,4}))?/', (string) $value, $matches)) {
        return '';
    }

    $start = $matches[1];
    $end = isset($matches[2]) ? $matches[2] : '';

    if (strlen($start) === 2) {
        $start = ((int) $start >= 70 ? '19' : '20') . $start;
    }

    if ($end !== '' && strlen($end) === 2) {
        $century = substr($start, 0, 2);
        $candidate = (int) ($century . $end);
        if ($candidate < (int) $start) {
            $candidate += 100;
        }
        $end = (string) $candidate;
    }

    return $end !== '' ? $start . '-' . $end : $start;
}

/**
 * Get the archive year from the post's hand-selected category.
 */
function wqs_get_archive_item_year($post_id, $group, $current_term = null)
{
    if ($current_term && !wqs_is_archive_root_term($group, $current_term)) {
        $label = wqs_format_archive_year_label($current_term->slug);
        if ($label !== '') {
            return $label;
        }
    }

    $configured = wqs_get_archive_configured_category_slugs($group);
    $configured_bases = array();

    foreach ($configured as $slug) {
        $configured_bases[] = preg_replace('/-(en|zh)$/', '', $slug);
    }

    foreach (wp_get_post_categories($post_id, array('fields' => 'all')) as $term) {
        $base_slug = preg_replace('/-(en|zh)$/', '', $term->slug);
        if (!empty($configured_bases) && !in_array($base_slug, $configured_bases, true)) {
            continue;
        }

        $label = wqs_format_archive_year_label($base_slug);
        if ($label !== '') {
            return $label;
        }
    }

    return get_the_date('Y', $post_id);
}

/**
 * Return the original content creation time, separate from publish/update time.
 */
function wqs_get_content_created_at($post_id)
{
    $created_at = get_post_meta($post_id, '_wqs_created_at', true);
    if (is_string($created_at) && preg_match('/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/', $created_at)) {
        return $created_at;
    }

    $post = get_post($post_id);
    return $post ? $post->post_date : '';
}

/**
 * Format the original content creation time.
 */
function wqs_get_content_created_date($post_id, $format = 'Y.m.d')
{
    $created_at = wqs_get_content_created_at($post_id);
    if (!$created_at) {
        return '';
    }

    $date = date_create($created_at, wp_timezone());
    return $date ? wp_date($format, $date->getTimestamp(), wp_timezone()) : '';
}

/**
 * Return the creation year used by archive filtering.
 */
function wqs_get_content_created_year($post_id)
{
    return wqs_get_content_created_date($post_id, 'Y');
}

/**
 * Resolve a post thumbnail, falling back to the first image in its content.
 */
function wqs_get_archive_thumbnail($post_id, $use_placeholder = false)
{
    $thumbnail = array(
        'url'            => '',
        'width'          => 0,
        'height'         => 0,
        'is_extreme'     => false,
        'is_placeholder' => false,
    );

    $featured_image_id = get_post_thumbnail_id($post_id);
    if ($featured_image_id && wqs_attachment_file_exists($featured_image_id)) {
        $data = wp_get_attachment_image_src($featured_image_id, 'large');
        if ($data) {
            $thumbnail['url'] = $data[0];
            $thumbnail['width'] = $data[1];
            $thumbnail['height'] = $data[2];
        }
    }

    if (empty($thumbnail['url'])) {
        $first_image = wqs_get_first_content_image($post_id);
        if ($first_image && !empty($first_image['url'])) {
            $thumbnail['url'] = $first_image['url'];
            $thumbnail['width'] = $first_image['width'];
            $thumbnail['height'] = $first_image['height'];
        }
    }

    if (empty($thumbnail['url']) && $use_placeholder) {
        $thumbnail['url'] = wqs_get_placeholder_image_url();
        $thumbnail['width'] = 900;
        $thumbnail['height'] = 600;
        $thumbnail['is_placeholder'] = true;
    }

    $thumbnail['is_extreme'] = wqs_is_extreme_aspect_ratio(
        $thumbnail['width'],
        $thumbnail['height']
    );

    return $thumbnail;
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
    $ranges = array();

    foreach ($terms as $term) {
        $label = wqs_format_archive_year_label(preg_replace('/-(en|zh)$/', '', $term->slug));
        if (preg_match('/^(\d{4})-(\d{4})$/', $label, $matches)) {
            $ranges[] = array(
                'start' => (int) $matches[1],
                'end'   => (int) $matches[2],
            );
        }
    }

    $terms = array_values(array_filter($terms, function ($term) use ($ranges) {
        $label = wqs_format_archive_year_label(preg_replace('/-(en|zh)$/', '', $term->slug));
        if (!preg_match('/^\d{4}$/', $label)) {
            return true;
        }

        $year = (int) $label;
        foreach ($ranges as $range) {
            if ($year >= $range['start'] && $year <= $range['end']) {
                return false;
            }
        }

        return true;
    }));

    usort($terms, function ($a, $b) {
        $a_label = wqs_format_archive_year_label(preg_replace('/-(en|zh)$/', '', $a->slug));
        $b_label = wqs_format_archive_year_label(preg_replace('/-(en|zh)$/', '', $b->slug));

        preg_match('/^(\d{4})(?:-(\d{4}))?$/', $a_label, $a_matches);
        preg_match('/^(\d{4})(?:-(\d{4}))?$/', $b_label, $b_matches);

        $a_start = isset($a_matches[1]) ? (int) $a_matches[1] : 0;
        $b_start = isset($b_matches[1]) ? (int) $b_matches[1] : 0;
        $a_end = isset($a_matches[2]) ? (int) $a_matches[2] : $a_start;
        $b_end = isset($b_matches[2]) ? (int) $b_matches[2] : $b_start;

        if ($a_end !== $b_end) {
            return $b_end - $a_end;
        }

        if ($a_start !== $b_start) {
            return $b_start - $a_start;
        }

        return strcasecmp($a->name, $b->name);
    });

    return $terms;
}

/**
 * Return the compact year or year-range label used in archive sidebars.
 */
function wqs_get_archive_sidebar_term_label($term)
{
    $slug = preg_replace('/-(en|zh)$/', '', $term->slug);
    if (preg_match('/^(\d{2,4}(?:-\d{2,4})?)/', $slug, $matches)) {
        return $matches[1];
    }

    return $term->name;
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

        return wqs_sort_archive_sidebar_terms($terms);
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
                <?php if ($root_term) : ?>
                    <?php
                    $all_url = get_term_link($root_term, 'category');
                    $is_all_active = $current_term && (int) $current_term->term_id === (int) $root_term->term_id;
                    ?>
                    <?php if (!is_wp_error($all_url)) : ?>
                    <li class="submenu-item">
                        <a href="<?php echo esc_url($all_url); ?>" class="submenu-link<?php echo $is_all_active ? ' active' : ''; ?>"<?php echo $is_all_active ? ' aria-current="page"' : ''; ?>>
                            <?php esc_html_e('ALL', 'wqs-portfolio'); ?>
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
                            <?php echo esc_html(wqs_get_archive_sidebar_term_label($term)); ?>
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
function wqs_render_archive_grid_item($index, $group = '', $current_term = null)
{
    $post_year = wqs_get_creation_year(get_the_ID());
    $item_cats = get_the_category();
    $cat_slugs = array();

    if ($item_cats) {
        foreach ($item_cats as $cat) {
            $cat_slugs[] = $cat->slug;
        }
    }

    $thumbnail = wqs_get_archive_thumbnail(get_the_ID(), true);
    $thumb_url = $thumbnail['url'];
    $is_extreme = $thumbnail['is_extreme'];
    $item_classes = 'works-item archive-item';
    if ($thumbnail['is_placeholder']) {
        $item_classes .= ' is-placeholder';
    }
    ?>
    <article id="post-<?php the_ID(); ?>" <?php post_class($item_classes); ?>
             data-aos="fade-up"
             data-aos-delay="<?php echo esc_attr(($index % 4) * 100); ?>"
             data-year="<?php echo esc_attr($post_year); ?>"
             data-title="<?php echo esc_attr(strtolower(get_the_title())); ?>"
             data-categories="<?php echo esc_attr(implode(',', $cat_slugs)); ?>">
        <div class="works-item-thumbnail">
            <a href="<?php the_permalink(); ?>">
                <img src="<?php echo esc_url($thumb_url); ?>"
                     alt="<?php echo esc_attr(get_the_title()); ?>"
                     class="<?php echo $is_extreme ? 'extreme-aspect' : ''; ?>"
                     loading="lazy">
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

                    var matchYear = false;
                    if (selectedYear === 'all') {
                        matchYear = true;
                    } else if (itemYear === selectedYear) {
                        matchYear = true;
                    } else {
                        // Handle year ranges like "97-99" and "14-18"
                        var rangeMatch = selectedYear.match(/^(\d{2})-(\d{2})$/);
                        if (rangeMatch) {
                            var rangeStart = parseInt(rangeMatch[1], 10);
                            var rangeEnd = parseInt(rangeMatch[2], 10);
                            // Convert 2-digit years to 4-digit
                            if (rangeStart < 100) {
                                rangeStart = rangeStart >= 70 ? 1900 + rangeStart : 2000 + rangeStart;
                                rangeEnd = rangeEnd >= 70 ? 1900 + rangeEnd : 2000 + rangeEnd;
                            }
                            var itemYearNum = parseInt(itemYear, 10);
                            if (!isNaN(itemYearNum) && itemYearNum >= rangeStart && itemYearNum <= rangeEnd) {
                                matchYear = true;
                            }
                        }
                    }

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
    } elseif ($config['mode'] === 'exhibitions') {
        $main_classes .= ' exhibitions-archive';
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
                    // The dropdown always uses exact creation years, even when
                    // the sidebar combines several years into one range.
                    $year_options = array();
                    while ($archive_query->have_posts()) : $archive_query->the_post();
                        $year = $archive_item_type === 'post'
                            ? wqs_get_creation_year(get_the_ID())
                            : (int) get_the_date('Y');
                        if ($year) {
                            $year_options[$year] = $year;
                        }
                    endwhile;
                    krsort($year_options, SORT_NUMERIC);
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
                            <?php foreach ($year_options as $label) : ?>
                                <option value="<?php echo esc_attr($label); ?>"><?php echo esc_html($label); ?></option>
                            <?php endforeach; ?>
                        </select>
                        <span class="filter-results-count" aria-live="polite" aria-atomic="true">
                            <span class="filter-count-visible">0</span> / <span class="filter-count-total">0</span>
                        </span>
                    </div>

                    <?php if ($config['mode'] === 'reviews' && $archive_item_type === 'post') : ?>
                        <div class="reviews-list" data-aos="fade-up" data-aos-delay="200">
                            <?php while ($archive_query->have_posts()) : $archive_query->the_post(); ?>
                                <?php
                                $post_year = wqs_get_creation_year(get_the_ID());
                                $thumbnail = wqs_get_archive_thumbnail(get_the_ID(), true);
                                ?>
                                <article id="post-<?php the_ID(); ?>" <?php post_class('review-item archive-item'); ?>
                                         data-year="<?php echo esc_attr($post_year); ?>"
                                         data-title="<?php echo esc_attr(strtolower(get_the_title())); ?>">
                                    <a class="review-thumbnail<?php echo $thumbnail['is_placeholder'] ? ' is-placeholder' : ''; ?>" href="<?php the_permalink(); ?>" aria-hidden="true" tabindex="-1">
                                        <?php if (!empty($thumbnail['url'])) : ?>
                                            <img src="<?php echo esc_url($thumbnail['url']); ?>"
                                                 alt=""
                                                 class="<?php echo $thumbnail['is_extreme'] ? 'extreme-aspect' : ''; ?>"
                                                 loading="lazy">
                                        <?php endif; ?>
                                    </a>
                                    <h2 class="review-title">
                                        <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                                    </h2>
                                    <time class="review-date" datetime="<?php echo esc_attr($post_year); ?>">
                                        <?php echo esc_html($post_year); ?>
                                    </time>
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
                                    wqs_render_archive_grid_item($i, $group, $current_term);
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
