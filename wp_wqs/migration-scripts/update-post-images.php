<?php
/**
 * Update image paths in posts to point to local /images/stories/ directory
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// First, let's check what's currently in the posts vs what's in the images directory
$upload_dir = '/Applications/ServBay/www/wqs_2026/images/stories';

// Build a mapping of available images
$available_images = [];
$iterator = new RecursiveIteratorIterator(
    new RecursiveDirectoryIterator($upload_dir, RecursiveDirectoryIterator::SKIP_DOTS),
    RecursiveIteratorIterator::SELF_FIRST
);
foreach ($iterator as $file) {
    if ($file->isFile()) {
        $ext = strtolower($file->getExtension());
        if (in_array($ext, ['jpg', 'jpeg', 'png', 'gif', 'webp'])) {
            $relative_path = str_replace($upload_dir . '/', '', $file->getPathname());
            $available_images[$relative_path] = '/images/stories/' . $relative_path;
        }
    }
}

echo "Found " . count($available_images) . " available images\n";

// Now let's check the original Joomla content and update WordPress posts
// Connect to old Joomla database
$old_pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_joomla;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// Get posts that should have images (photography category)
$stmt = $old_pdo->query("
    SELECT c.id, c.title, c.introtext, c.fulltext, cat.title as category
    FROM jos_content c
    JOIN jos_categories cat ON c.catid = cat.id
    WHERE c.catid NOT IN (1,2,3,4,5,6,7,29)
    AND c.state = 1
    AND (c.introtext LIKE '%images/stories%' OR c.fulltext LIKE '%images/stories%')
    ORDER BY c.id
");
$joomla_posts = $stmt->fetchAll();

echo "Found " . count($joomla_posts) . " Joomla posts with images\n\n";

// Process each post
$updated = 0;
$not_found = 0;

foreach ($joomla_posts as $jp) {
    // Find the WordPress post with the same title
    $title = trim($jp['title']);
    $stmt = $pdo->prepare("SELECT ID, post_content FROM wp_posts WHERE post_type = 'post' AND post_title LIKE ? LIMIT 1");
    $stmt->execute([$title]);
    $wp_post = $stmt->fetch();

    if (!$wp_post) {
        // Try with partial match
        $title_parts = explode(' ', $title);
        $first_word = $title_parts[0];
        $stmt = $pdo->prepare("SELECT ID, post_content FROM wp_posts WHERE post_type = 'post' AND post_title LIKE ? LIMIT 1");
        $stmt->execute(['%' . $first_word . '%']);
        $wp_post = $stmt->fetch();
    }

    if (!$wp_post) {
        $not_found++;
        continue;
    }

    // Build new content from original
    $content = $jp['introtext'] . $jp['fulltext'];

    // Replace old image URLs with local paths
    $content = str_replace(
        'http://www.wangqingsong.com/images/stories/',
        '/images/stories/',
        $content
    );
    $content = str_replace(
        'http://localhost/wangqingsong.com/images/stories/',
        '/images/stories/',
        $content
    );

    // Remove mce_ attributes that clutter the HTML
    $content = preg_replace('/\s*mce_(href|src|background)="[^"]*"/', '', $content);
    $content = preg_replace('/\s*class="mce[^"]*"/', '', $content);
    $content = preg_replace('/\s*style="[^"]*mce[^"]*"/', '', $content);

    // Remove extra attributes like rel="shadowbox"
    $content = preg_replace('/\s*rel="[^"]*"/', '', $content);

    // Fix internal links
    $content = preg_replace(
        '#index\.php\?option=com_content&view=article&id=(\d+)#',
        '/?p=$1',
        $content
    );

    // Update the post
    $stmt = $pdo->prepare("UPDATE wp_posts SET post_content = ? WHERE ID = ?");
    $stmt->execute([$content, $wp_post['ID']]);
    $updated++;

    if ($updated <= 5) {
        echo "Updated post {$wp_post['ID']}: {$title}\n";
    }
}

echo "\n=== Done ===\n";
echo "Updated: $updated posts\n";
echo "Not found in WordPress: $not_found posts\n";