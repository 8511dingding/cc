<?php
/**
 * Fix corrupted image paths in posts
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$stmt = $pdo->query("SELECT ID, post_content FROM wp_posts WHERE post_type IN ('post', 'page') AND post_content LIKE '%images/stories%'");
$posts = $stmt->fetchAll(PDO::FETCH_ASSOC);

$fixed = 0;
foreach ($posts as $post) {
    $content = $post['post_content'];
    $new_content = $content;

    // Fix doubled paths like: /images/stories/.../file.jpg/stories/.../file.jpg
    // Extract the first path portion before the duplication
    $new_content = preg_replace('#(/images/stories/[^"\']+)\.jpg/stories/\1\.jpg#', '$1.jpg', $new_content);
    $new_content = preg_replace('#(/images/stories/[^"\']+)\.jpeg/stories/\1\.jpeg#', '$1.jpeg', $new_content);
    $new_content = preg_replace('#(/images/stories/[^"\']+)\.png/stories/\1\.png#', '$1.png', $new_content);
    $new_content = preg_replace('#(/images/stories/[^"\']+)\.gif/stories/\1\.gif#', '$1.gif', $new_content);
    $new_content = preg_replace('#(/images/stories/[^"\']+)\.webp/stories/\1\.webp#', '$1.webp', $new_content);

    // Fix trailing words like "left", "right", "center" after image path in src
    $new_content = preg_replace('#(/images/stories/[^\s"\']+\.(?:jpg|jpeg|png|gif|webp))\s+(left|right|center|top|bottom)(\s|"|\')#', '$1$3', $new_content);

    // Fix any remaining corrupted src patterns - if we see .jpg followed by more path stuff
    // Pattern: src="/images/stories/...something.jpg/stories/..."
    $new_content = preg_replace_callback(
        '#src="(/images/stories/[^"]+\.(?:jpg|jpeg|png|gif|webp))/stories/[^"]+"#',
        function($m) { return 'src="' . $m[1] . '"'; },
        $new_content
    );

    if ($new_content !== $content) {
        $pdo->prepare("UPDATE wp_posts SET post_content = ? WHERE ID = ?")->execute([$new_content, $post['ID']]);
        $fixed++;
    }
}

echo "Fixed corrupted paths in $fixed posts\n";

// Show sample of remaining image paths
echo "\nSample remaining image paths:\n";
$stmt = $pdo->query("SELECT ID, post_content FROM wp_posts WHERE post_type = 'post' AND post_content LIKE '%images/stories%' LIMIT 3");
$posts = $stmt->fetchAll(PDO::FETCH_ASSOC);
foreach ($posts as $post) {
    echo "Post ID: {$post['ID']}\n";
    if (preg_match_all('/src="([^"]+)"/', $post['post_content'], $m)) {
        foreach (array_slice($m[1], 0, 3) as $src) {
            echo "  src: $src\n";
        }
    }
    echo "\n";
}