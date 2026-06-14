<?php
/**
 * Regenerate attachment metadata to fix media library display issues
 */

define('WP_USE_THEMES', false);
require_once('/Users/jianing/Ning\'s Git/wp_wqs/local-dev/wordpress/wp-load.php');

// Skip permission check for CLI execution

$attachments = get_posts([
    'post_type' => 'attachment',
    'post_status' => 'inherit',
    'posts_per_page' => -1,
    'orderby' => 'ID',
    'order' => 'ASC',
]);

$count = 0;
$errors = 0;

foreach ($attachments as $attachment) {
    $file_path = get_attached_file($attachment->ID);

    if (!file_exists($file_path)) {
        error_log("File not found for attachment {$attachment->ID}: {$file_path}");
        $errors++;
        continue;
    }

    $metadata = wp_generate_attachment_metadata($attachment->ID, $file_path);

    if (!is_wp_error($metadata) && !empty($metadata)) {
        wp_update_attachment_metadata($attachment->ID, $metadata);
        $count++;
    } else {
        $errors++;
    }
}

echo "Regenerated metadata for {$count} attachments. Errors: {$errors}\n";