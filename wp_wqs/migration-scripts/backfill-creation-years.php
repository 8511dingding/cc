<?php
/**
 * Backfill the exact creation year for Photography, Exhibitions, Reviews, and
 * Shooting posts.
 *
 * Usage:
 * php migration-scripts/backfill-creation-years.php
 * php migration-scripts/backfill-creation-years.php --apply
 */

define('WP_USE_THEMES', false);
require dirname(__DIR__) . '/local-dev/wordpress/wp-load.php';

$apply = in_array('--apply', $argv, true);
$groups = array('photography', 'exhibitions', 'reviews', 'shooting');
$stats = array(
    'posts'       => 0,
    'updated'     => 0,
    'unchanged'   => 0,
    'unresolved'  => array(),
    'by_group'    => array(),
    'by_language' => array('en' => 0, 'zh' => 0),
);

/**
 * Return unique four-digit years in a string within optional bounds.
 */
function wqs_creation_year_candidates($text, $minimum = 1900, $maximum = 2100)
{
    preg_match_all('/(?<!\d)(19\d{2}|20\d{2})(?!\d)/', wp_strip_all_tags((string) $text), $matches);

    return array_values(array_unique(array_filter(array_map('intval', $matches[1]), function ($year) use ($minimum, $maximum) {
        return $year >= $minimum && $year <= $maximum;
    })));
}

/**
 * Return exact years and ranges from the configured categories on a post.
 */
function wqs_creation_year_category_data($post_id, $group)
{
    $configured = array_map(function ($slug) {
        return preg_replace('/-(en|zh)$/', '', $slug);
    }, wqs_get_archive_configured_category_slugs($group));

    $exact = array();
    $ranges = array();

    foreach (wp_get_post_categories($post_id, array('fields' => 'all')) as $term) {
        $base = preg_replace('/-(en|zh)$/', '', $term->slug);
        if (!empty($configured) && !in_array($base, $configured, true)) {
            continue;
        }

        $label = wqs_format_archive_year_label($base);
        if (preg_match('/^\d{4}$/', $label)) {
            $exact[] = (int) $label;
        } elseif (preg_match('/^(\d{4})-(\d{4})$/', $label, $matches)) {
            $ranges[] = array((int) $matches[1], (int) $matches[2]);
        }
    }

    return array(
        'exact'  => array_values(array_unique($exact)),
        'ranges' => $ranges,
    );
}

/**
 * Infer one exact year from source categories and migrated content.
 */
function wqs_infer_creation_year($post, $group)
{
    $category_data = wqs_creation_year_category_data($post->ID, $group);
    if (count($category_data['exact']) === 1) {
        return $category_data['exact'][0];
    }

    if (count($category_data['exact']) > 1 || empty($category_data['ranges'])) {
        return 0;
    }

    $minimum = min(array_column($category_data['ranges'], 0));
    $maximum = max(array_column($category_data['ranges'], 1));

    if ($group === 'exhibitions') {
        $legacy_key = get_post_meta($post->ID, '_wqs_legacy_exhibition_key', true);
        if (preg_match('/^139-(\d+)$/', $legacy_key, $matches)) {
            $legacy_years = array(
                1 => 1996,
                2 => 1996,
                3 => 2000,
                4 => 2001,
                5 => 2002,
                6 => 2003,
                7 => 2005,
            );
            if (isset($legacy_years[(int) $matches[1]])) {
                return $legacy_years[(int) $matches[1]];
            }
        }
    }

    $title_years = wqs_creation_year_candidates($post->post_title, $minimum, $maximum);
    if (!empty($title_years)) {
        return $title_years[0];
    }

    if ($group === 'photography') {
        preg_match_all('#(?:photography|uploads)/(\d{4})/#i', $post->post_content, $path_matches);
        foreach (array_map('intval', $path_matches[1] ?? array()) as $year) {
            if ($year >= $minimum && $year <= $maximum) {
                return $year;
            }
        }
    }

    $content_years = wqs_creation_year_candidates($post->post_content, $minimum, $maximum);
    if (!empty($content_years)) {
        return $content_years[0];
    }

    $created_year = (int) substr((string) get_post_meta($post->ID, '_wqs_created_at', true), 0, 4);
    if ($created_year >= $minimum && $created_year <= $maximum) {
        return $created_year;
    }

    $post_year = (int) substr($post->post_date, 0, 4);
    return $post_year >= $minimum && $post_year <= $maximum ? $post_year : 0;
}

$seen = array();

foreach ($groups as $group) {
    $term_ids = wqs_get_archive_content_term_ids($group);
    $query = new WP_Query(array(
        'post_type'      => 'post',
        'post_status'    => 'publish',
        'posts_per_page' => -1,
        'lang'           => '',
        'tax_query'      => array(
            array(
                'taxonomy'         => 'category',
                'field'            => 'term_id',
                'terms'            => $term_ids,
                'include_children' => true,
            ),
        ),
    ));

    $stats['by_group'][$group] = 0;

    foreach ($query->posts as $post) {
        if (isset($seen[$post->ID])) {
            continue;
        }
        $seen[$post->ID] = true;

        $year = wqs_infer_creation_year($post, $group);
        if (!$year) {
            $stats['unresolved'][] = array(
                'id'    => $post->ID,
                'group' => $group,
                'title' => $post->post_title,
            );
            continue;
        }

        $stats['posts']++;
        $stats['by_group'][$group]++;
        $language = wqs_get_effective_post_language($post->ID);
        $stats['by_language'][$language]++;

        $existing = absint(get_post_meta($post->ID, '_wqs_creation_year', true));
        if ($existing === $year) {
            $stats['unchanged']++;
            continue;
        }

        if ($apply) {
            update_post_meta($post->ID, '_wqs_creation_year', $year);
        }
        $stats['updated']++;
    }
}

echo ($apply ? "APPLIED\n" : "DRY RUN\n");
echo wp_json_encode($stats, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n";
