<?php
/**
 * Import images into WordPress Media Library
 * Organizes images by category/year
 */

ini_set('max_execution_time', '300');

$upload_dir = '/Applications/ServBay/www/wqs_2026/wp-content/uploads';
if (!file_exists($upload_dir)) {
    mkdir($upload_dir, 0755, true);
}

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$images_base = '/Applications/ServBay/www/wqs_2026/images/stories';
$patterns_base = '/Applications/ServBay/www/wqs_2026/wp-content/themes/glamazon-fse/inc/patterns';

// Get existing media to avoid duplicates
$stmt = $pdo->query("SELECT meta_value FROM wp_postmeta WHERE meta_key = '_wp_attached_file'");
$existing_files = $stmt->fetchAll(PDO::FETCH_COLUMN);
$existing_set = array_flip($existing_files);

// Category mapping for images
$category_map = [
    'photography' => 'Photography',
    'exhibition' => 'Exhibitions',
    'reviews' => 'Reviews',
    'shooting' => 'Shooting',
    'video' => 'Video',
    'biography' => 'Biography',
    'others' => 'Others',
    'contact' => 'Contact',
];

function sanitize_filename($filename) {
    $filename = preg_replace('/[^a-z0-9._-]/i', '-', $filename);
    return $filename;
}

function get_or_create_category($pdo, $name, $parent_id = 0) {
    $slug = sanitize_title($name);
    $stmt = $pdo->prepare("SELECT term_id FROM wp_terms WHERE slug = ?");
    $stmt->execute([$slug]);
    $term = $stmt->fetch();

    if ($term) {
        return $term['term_id'];
    }

    $pdo->prepare("INSERT INTO wp_terms (name, slug) VALUES (?, ?)")->execute([$name, $slug]);
    $term_id = $pdo->lastInsertId();

    $pdo->prepare("INSERT INTO wp_term_taxonomy (term_id, taxonomy, description, parent, count) VALUES (?, 'category', '', ?, 0)")
        ->execute([$term_id, $parent_id]);

    return $term_id;
}

function sanitize_title($title) {
    $title = preg_replace('/[^a-z0-9\x{4e00}-\x{9fa5}]/u', '-', strtolower($title));
    $title = preg_replace('/-+/', '-', $title);
    $title = trim($title, '-');
    return $title;
}

function copy_image_to_uploads($source, $dest_dir, $filename) {
    $dest = $dest_dir . '/' . $filename;
    if (!file_exists($dest)) {
        if (!copy($source, $dest)) {
            return false;
        }
    }
    return $dest;
}

// Get or create Media category
$media_cat_id = get_or_create_category($pdo, 'Media Library');

$imported = 0;
$skipped = 0;
$errors = [];

// Scan all image categories
foreach ($category_map as $folder => $category_name) {
    $category_path = $images_base . '/' . $folder;
    if (!is_dir($category_path)) {
        continue;
    }

    // Get or create category
    $cat_id = get_or_create_category($pdo, $category_name);

    // Recursively scan for images
    $iterator = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($category_path, RecursiveDirectoryIterator::SKIP_DOTS),
        RecursiveIteratorIterator::SELF_FIRST
    );

    foreach ($iterator as $file) {
        if (!$file->isFile()) continue;

        $ext = strtolower($file->getExtension());
        if (!in_array($ext, ['jpg', 'jpeg', 'png', 'gif', 'webp'])) continue;

        $relative_path = str_replace($images_base . '/', '', $file->getPathname());
        $filename = sanitize_filename($file->getBasename());

        // Check if already imported
        $upload_path = 'uploads/' . $relative_path;
        if (isset($existing_set[$upload_path])) {
            $skipped++;
            continue;
        }

        // Create year-based folder in uploads
        $year = date('Y');
        if (preg_match('/(19|20)\d{2}/', $file->getPath(), $m)) {
            $year = $m[0];
        }

        $dest_dir = $upload_dir . '/' . $year;
        if (!file_exists($dest_dir)) {
            mkdir($dest_dir, 0755, true);
        }

        // Copy to uploads folder
        $dest_file = copy_image_to_uploads($file->getPathname(), $dest_dir, $filename);
        if (!$dest_file) {
            $errors[] = "Failed to copy: " . $file->getPathname();
            continue;
        }

        // Create attachment post
        $now = date('Y-m-d H:i:s');
        $pdo->prepare("
            INSERT INTO wp_posts
            (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status,
             post_name, post_parent, post_type, to_ping, pinged, post_content_filtered)
            VALUES (1, ?, ?, '', ?, '', 'inherit', ?, 0, 'attachment', '', '', '')
        ")->execute([$now, $now, $filename, sanitize_title(pathinfo($filename, PATHINFO_FILENAME))]);

        $attachment_id = $pdo->lastInsertId();

        // Get relative path for DB
        $db_path = str_replace('/Applications/ServBay/www/wqs_2026/wp-content/', '', $dest_file);

        // Add metadata
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, '_wp_attached_file', ?)")
            ->execute([$attachment_id, $db_path]);

        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, '_wp_attachment_metadata', ?)")
            ->execute([$attachment_id, serialize([
                'width' => 0,
                'height' => 0,
                'file' => $db_path,
            ])]);

        // Assign to category
        $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")
            ->execute([$attachment_id, $cat_id]);

        // Also assign to Media Library category
        $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")
            ->execute([$attachment_id, $media_cat_id]);

        $imported++;

        if ($imported % 50 == 0) {
            echo "Imported $imported images...\n";
        }
    }
}

echo "\n=== Import Complete ===\n";
echo "Imported: $imported images\n";
echo "Skipped: $skipped images (already exist)\n";
if (count($errors) > 0) {
    echo "Errors: " . count($errors) . "\n";
    foreach ($errors as $e) {
        echo "  - $e\n";
    }
}

// Update category counts
$pdo->query("UPDATE wp_term_taxonomy SET count = (SELECT COUNT(*) FROM wp_term_relationships WHERE term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id) WHERE taxonomy = 'category'");

echo "\nDone! Check WordPress Media Library.\n";