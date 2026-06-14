<?php
/**
 * Standalone script to regenerate _wp_attachment_metadata for all attachments
 * Uses direct database connection, no WordPress needed
 */

$db_host = '127.0.0.1';
$db_port = 3306;
$db_user = 'root';
$db_pass = 'GM3750-jm';
$db_name = 'wqs_wordpress';
$upload_dir = '/Users/jianing/Ning\'s Git/wp_wqs/local-dev/wordpress/wp-content/uploads/';

$conn = new mysqli($db_host, $db_user, $db_pass, $db_name, $db_port);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$conn->set_charset('utf8mb4');

// Get all attachments
$result = $conn->query("
    SELECT p.ID, pm.meta_value as attached_file
    FROM wp_posts p
    INNER JOIN wp_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_wp_attached_file'
    WHERE p.post_type = 'attachment'
    ORDER BY p.ID
");

$updated = 0;
$errors = 0;

while ($row = $result->fetch_assoc()) {
    $attachment_id = $row['ID'];
    $attached_file = $row['attached_file'];

    $file_path = $upload_dir . $attached_file;

    if (!file_exists($file_path)) {
        echo "Missing file for ID $attachment_id: $file_path\n";
        $errors++;
        continue;
    }

    $file_info = getimagesize($file_path);
    if ($file_info === false) {
        echo "Cannot get image info for ID $attachment_id: $file_path\n";
        $errors++;
        continue;
    }

    $width = $file_info[0];
    $height = $file_info[1];
    $mime_type = $file_info['mime'];
    $filesize = filesize($file_path);

    // Build metadata array
    $metadata = [
        'width' => $width,
        'height' => $height,
        'file' => $attached_file,
        'filesize' => $filesize,
        'sizes' => [],
        'image_meta' => []
    ];

    // Generate thumbnail info
    $path_info = pathinfo($file_path);
    $dirname = $path_info['dirname'];
    $basename = $path_info['basename'];
    $filename = $path_info['filename'];
    $extension = $path_info['extension'];

    // Check for existing thumbnails
    $thumbnail_sizes = ['thumbnail', 'medium', 'large', 'medium_large', '1536x1536', '2048x2048'];
    foreach ($thumbnail_sizes as $size) {
        // Try common thumbnail naming patterns
        $thumb_patterns = [
            $dirname . '/' . $filename . '-' . $size . '.' . $extension,
            $dirname . '/' . $filename . '-' . $width . 'x' . $height . '.' . $extension,
        ];

        foreach ($thumb_patterns as $thumb_path) {
            if (file_exists($thumb_path)) {
                $thumb_info = getimagesize($thumb_path);
                if ($thumb_info) {
                    $metadata['sizes'][$size] = [
                        'file' => basename($thumb_path),
                        'width' => $thumb_info[0],
                        'height' => $thumb_info[1],
                        'mime-type' => $thumb_info['mime'],
                        'filesize' => filesize($thumb_path)
                    ];
                    break;
                }
            }
        }
    }

    // Serialize metadata
    $serialized = serialize($metadata);

    // Check if metadata exists
    $check = $conn->query("SELECT meta_id FROM wp_postmeta WHERE post_id = $attachment_id AND meta_key = '_wp_attachment_metadata'");

    if ($check->num_rows > 0) {
        // Update
        $conn->query("UPDATE wp_postmeta SET meta_value = '" . $conn->real_escape_string($serialized) . "' WHERE post_id = $attachment_id AND meta_key = '_wp_attachment_metadata'");
    } else {
        // Insert
        $conn->query("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES ($attachment_id, '_wp_attachment_metadata', '" . $conn->real_escape_string($serialized) . "')");
    }

    // Also update post_mime_type if empty
    $mime_type_map = [
        'image/jpeg' => 'image/jpeg',
        'image/png' => 'image/png',
        'image/gif' => 'image/gif',
        'image/webp' => 'image/webp',
        'application/pdf' => 'application/pdf',
    ];

    if (isset($mime_type_map[$mime_type])) {
        $conn->query("UPDATE wp_posts SET post_mime_type = '" . $mime_type_map[$mime_type] . "' WHERE ID = $attachment_id AND (post_mime_type = '' OR post_mime_type IS NULL)");
    }

    $updated++;
    if ($updated % 100 == 0) {
        echo "Processed $updated attachments...\n";
    }
}

echo "\nDone! Updated: $updated, Errors: $errors\n";

$conn->close();