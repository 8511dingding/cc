<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check genuine Chinese posts (posts with Chinese titles that should remain as ZH)
$stmt = $pdo->query("
    SELECT p.ID, p.post_title, m.meta_value as lang
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'language'
    WHERE p.post_type = 'post' AND p.post_status = 'publish'
    AND m.meta_value = 'zh'
    ORDER BY p.ID
    LIMIT 20
");
echo "ZH posts (first 20):\n";
while ($row = $stmt->fetch()) {
    echo sprintf("%d: %s\n", $row['ID'], $row['post_title']);
}

// Count total
$stmt2 = $pdo->query("
    SELECT COUNT(*)
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'language'
    WHERE p.post_type = 'post' AND p.post_status = 'publish'
    AND m.meta_value = 'zh'
");
echo "\nTotal ZH posts: " . $stmt2->fetchColumn() . "\n";