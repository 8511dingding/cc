<?php
/**
 * Update image paths in posts to use WordPress media library
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// Get all attachments and their paths
$stmt = $pdo->query("
    SELECT p.ID, pm.meta_value as filepath
    FROM wp_posts p
    JOIN wp_postmeta pm ON p.ID = pm.post_id
    WHERE p.post_type = 'attachment' AND pm.meta_key = '_wp_attached_file'
");
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
$attachments = [];
foreach ($rows as $row) {
    $attachments[$row['filepath']] = $row['ID'];
}

// Create mapping from old paths to new URLs
$path_to_url = [];
foreach ($attachments as $filepath => $id) {
    // Old path like: /images/stories/photography/9799/index/1997_our_life_is_sweeter_than_honey.jpg
    // New URL: /wp-content/uploads/1997/images/stories/photography/9799/index/1997_our_life_is_sweeter_than_honey.jpg
    $parts = pathinfo($filepath);
    $filename = $parts['basename'];

    // Try to find matching old path pattern
    $path_to_url['/images/stories/' . str_replace('uploads/', '', $filepath)] = '/wp-content/uploads/' . $filepath;
}

echo "Found " . count($path_to_url) . " image paths to update.\n";

// Update posts
$updated = 0;
$stmt = $pdo->query("SELECT ID, post_content FROM wp_posts WHERE post_type IN ('post', 'page') AND post_content LIKE '%images/stories%'");
$posts = $stmt->fetchAll();

foreach ($posts as $post) {
    $content = $post['post_content'];
    $new_content = $content;

    foreach ($path_to_url as $old_path => $new_url) {
        // Replace in src attributes
        $new_content = str_replace('src="' . $old_path, 'src="' . $new_url, $new_content);
        $new_content = str_replace("src='" . $old_path, "src='" . $new_url, $new_content);

        // Replace in href attributes (for links to images)
        $new_content = str_replace('href="' . $old_path, 'href="' . $new_url, $new_content);
        $new_content = str_replace("href='" . $old_path, "href='" . $new_url, $new_content);

        // Replace in srcset
        $new_content = str_replace($old_path, $new_url, $new_content);
    }

    if ($new_content !== $content) {
        $pdo->prepare("UPDATE wp_posts SET post_content = ? WHERE ID = ?")->execute([$new_content, $post['ID']]);
        $updated++;
    }
}

echo "Updated $updated posts.\n";

// Also fix corrupted paths (there are some weird patterns in the HTML)
$stmt = $pdo->query("SELECT ID, post_content FROM wp_posts WHERE post_type IN ('post', 'page')");
$posts = $stmt->fetchAll();

$corruption_fixed = 0;
foreach ($posts as $post) {
    $content = $post['post_content'];

    // Fix patterns like: /images/stories/.../something.jpg"/stories/.../something.jpg
    $new_content = preg_replace('#(/images/stories/[^"]+)"([^"]+")#', '$1$2', $content);

    // Fix src attributes that got duplicated
    $new_content = preg_replace('#src="([^"]+)/images/#', 'src="/images/', $new_content);

    if ($new_content !== $content) {
        $pdo->prepare("UPDATE wp_posts SET post_content = ? WHERE ID = ?")->execute([$new_content, $post['ID']]);
        $corruption_fixed++;
    }
}

echo "Fixed corrupted paths in $corruption_fixed posts.\n";
echo "Done!\n";