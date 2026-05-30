<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check for remaining self-referencing posts
$stmt = $pdo->query("
    SELECT p.ID, p.post_title
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'en_post_id'
    WHERE m.meta_value = p.ID
    AND p.post_type = 'post'
");
echo "Self-referencing posts remaining: " . $stmt->rowCount() . "\n";

// Verify a few of the previously problematic posts
$stmt2 = $pdo->prepare("
    SELECT p.ID, p.post_title, m.meta_value as lang
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'language'
    WHERE p.ID IN (1520, 1521, 1522, 1523, 1524)
    ORDER BY p.ID
");
$stmt2->execute();
echo "\nPreviously problematic posts now:\n";
while ($row = $stmt2->fetch()) {
    echo "  {$row['ID']}: {$row['post_title']} (lang: {$row['lang']})\n";
}

// Check pll_translations for these posts
$stmt3 = $pdo->prepare("SELECT * FROM wp_pll_translations WHERE element_id IN (1520, 1521, 1522, 1523, 1524)");
$stmt3->execute();
echo "\nPlL translations for these posts:\n";
while ($row = $stmt3->fetch()) {
    echo "  elem_id={$row['element_id']}, trans_id={$row['translation_id']}, lang={$row['language']}, source={$row['source_language']}\n";
}

// Check term_relationships for these posts
$stmt4 = $pdo->prepare("
    SELECT object_id, term_taxonomy_id
    FROM wp_term_relationships
    WHERE object_id IN (1520, 1521, 1522, 1523, 1524)
    AND term_taxonomy_id IN (277, 280)
    ORDER BY object_id, term_taxonomy_id
");
$stmt4->execute();
echo "\nTerm relationships for these posts:\n";
while ($row = $stmt4->fetch()) {
    echo "  object_id={$row['object_id']}, term_taxonomy_id={$row['term_taxonomy_id']}\n";
}