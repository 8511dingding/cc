<?php
/**
 * Repair migrated review image URLs, create featured images, and backfill
 * original content creation times.
 *
 * Run from the repository root:
 * php migration-scripts/repair-review-images-and-created-dates.php --apply
 */

define('WP_USE_THEMES', false);
require dirname(__DIR__) . '/local-dev/wordpress/wp-load.php';

$apply = in_array('--apply', $argv, true);
$rebuild_dates = in_array('--rebuild-dates', $argv, true);
$stats = array(
    'posts_scanned'       => 0,
    'content_repaired'    => 0,
    'featured_created'    => 0,
    'created_at_backfill' => 0,
    'missing_sources'     => array(),
);

require_once ABSPATH . 'wp-admin/includes/image.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';

/**
 * Import one preserved legacy image as a unique WordPress attachment.
 */
function wqs_repair_import_featured_image($source_file, $post_id)
{
    $path_parts = explode('/', str_replace('\\', '/', $source_file));
    $basename = sanitize_file_name(basename($source_file));
    $parent = sanitize_file_name($path_parts[count($path_parts) - 2] ?? 'review');
    $filename = sprintf('review-%d-%s-%s', $post_id, $parent, $basename);
    $upload = wp_upload_bits($filename, null, file_get_contents($source_file));

    if (!empty($upload['error'])) {
        return new WP_Error('upload_failed', $upload['error']);
    }

    $filetype = wp_check_filetype($upload['file']);
    $attachment_id = wp_insert_attachment(
        array(
            'post_mime_type' => $filetype['type'],
            'post_title'     => get_the_title($post_id),
            'post_status'    => 'inherit',
            'post_parent'    => $post_id,
        ),
        $upload['file'],
        $post_id,
        true
    );

    if (is_wp_error($attachment_id)) {
        return $attachment_id;
    }

    wp_update_attachment_metadata(
        $attachment_id,
        wp_generate_attachment_metadata($attachment_id, $upload['file'])
    );
    update_post_meta($attachment_id, '_wp_attachment_image_alt', get_the_title($post_id));

    return $attachment_id;
}

/**
 * Infer an original creation time for migrated posts.
 */
function wqs_repair_infer_created_at($post)
{
    global $wpdb;

    $duplicate_date = $wpdb->get_var(
        $wpdb->prepare(
            "SELECT post_date
             FROM {$wpdb->posts}
             WHERE post_type = 'post'
               AND post_status = 'publish'
               AND post_title = %s
               AND ID <> %d
               AND post_date < %s
             ORDER BY post_date ASC
             LIMIT 1",
            $post->post_title,
            $post->ID,
            '2026-01-01 00:00:00'
        )
    );

    if ($duplicate_date) {
        return $duplicate_date;
    }

    if ((int) substr($post->post_date, 0, 4) < 2026) {
        return $post->post_date;
    }

    foreach (wp_get_post_categories($post->ID, array('fields' => 'all')) as $term) {
        $year_label = wqs_format_archive_year_label($term->slug);
        if (preg_match('/^(\d{4})/', $year_label, $matches)) {
            return $matches[1] . substr($post->post_date, 4);
        }
    }

    return $post->post_date;
}

$posts = get_posts(
    array(
        'post_type'        => 'post',
        'post_status'      => array('publish', 'draft', 'pending', 'future', 'private'),
        'posts_per_page'   => -1,
        'orderby'          => 'ID',
        'order'            => 'ASC',
        'suppress_filters' => true,
        'lang'             => '',
    )
);

foreach ($posts as $post) {
    $stats['posts_scanned']++;

    if ($rebuild_dates || get_post_meta($post->ID, '_wqs_created_at', true) === '') {
        $created_at = wqs_repair_infer_created_at($post);
        if ($apply) {
            update_post_meta($post->ID, '_wqs_created_at', $created_at);
        }
        $stats['created_at_backfill']++;
    }

    $is_review = false;
    foreach (wp_get_post_categories($post->ID, array('fields' => 'all')) as $term) {
        if (stripos($term->slug, 'review') !== false || stripos($term->name, 'review') !== false || strpos($term->name, '评论') !== false) {
            $is_review = true;
            break;
        }
    }

    if (!$is_review || $post->post_content === '') {
        continue;
    }

    preg_match_all('/<img\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>/i', $post->post_content, $matches);
    if (empty($matches[1])) {
        continue;
    }

    $content = $post->post_content;
    $first_source_file = '';

    foreach (array_unique($matches[1]) as $old_url) {
        $path = wp_parse_url(html_entity_decode($old_url), PHP_URL_PATH);
        if (!preg_match('#(?:^|/)(images/stories/.+)$#i', (string) $path, $path_match)) {
            continue;
        }

        $relative_path = $path_match[1];
        $source_file = ABSPATH . $relative_path;
        if (!is_file($source_file)) {
            $stats['missing_sources'][] = array(
                'post_id' => $post->ID,
                'url'     => $old_url,
            );
            continue;
        }

        if ($first_source_file === '') {
            $first_source_file = $source_file;
        }

        $content = str_replace($old_url, home_url('/' . $relative_path), $content);
    }

    if ($content !== $post->post_content) {
        if ($apply) {
            wp_update_post(
                array(
                    'ID'           => $post->ID,
                    'post_content' => $content,
                )
            );
        }
        $stats['content_repaired']++;
    }

    $featured_id = get_post_thumbnail_id($post->ID);
    $has_valid_featured = $featured_id && wqs_attachment_file_exists($featured_id);
    if (!$has_valid_featured && $first_source_file !== '') {
        if ($apply) {
            $attachment_id = wqs_repair_import_featured_image($first_source_file, $post->ID);
            if (!is_wp_error($attachment_id)) {
                set_post_thumbnail($post->ID, $attachment_id);
                $stats['featured_created']++;
            }
        } else {
            $stats['featured_created']++;
        }
    }
}

echo ($apply ? "APPLIED\n" : "DRY RUN\n");
echo wp_json_encode($stats, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
