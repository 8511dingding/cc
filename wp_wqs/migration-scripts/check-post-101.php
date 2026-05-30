<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check postmeta for posts 101 and 1431
foreach ([101, 1431] as $id) {
    $stmt = $pdo->prepare("SELECT meta_key, meta_value FROM wp_postmeta WHERE post_id = ?");
    $stmt->execute([$id]);
    echo "Post $id meta:\n";
    while ($row = $stmt->fetch()) {
        echo "  {$row['meta_key']}: {$row['meta_value']}\n";
    }
    echo "\n";
}

// Check what URL the zh version should have
$stmt = $pdo->prepare("SELECT post_name FROM wp_posts WHERE ID = ?");
$stmt->execute([1431]);
$zh_slug = $stmt->fetchColumn();
echo "ZH slug for 1431: $zh_slug\n";

// Check term_relationships
$stmt2 = $pdo->prepare("SELECT term_taxonomy_id FROM wp_term_relationships WHERE object_id = ?");
$stmt2->execute([1431]);
echo "Term taxonomy IDs for 1431: " . implode(', ', $stmt2->fetchAll(PDO::FETCH_COLUMN)) . "\n";

$stmt3 = $pdo->prepare("SELECT term_taxonomy_id FROM wp_term_relationships WHERE object_id = ?");
$stmt3->execute([101]);
echo "Term taxonomy IDs for 101: " . implode(', ', $stmt3->fetchAll(PDO::FETCH_COLUMN)) . "\n";