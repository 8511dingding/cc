<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Find posts with language=en but no EN term_taxonomy_id=277
$stmt = $pdo->query('
    SELECT p.ID, p.post_title, m.meta_value as lang
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = "language"
    LEFT JOIN wp_term_relationships tr ON p.ID = tr.object_id AND tr.term_taxonomy_id = 277
    WHERE m.meta_value = "en" AND tr.object_id IS NULL
    AND p.post_type = "post"
');
echo "EN posts without EN term (but should have):\n";
while ($row = $stmt->fetch()) {
    echo "  " . $row['ID'] . ": " . $row['post_title'] . "\n";
}

// Check postmeta - why is there count 193 for en but term count is 192?
$stmt2 = $pdo->query('SELECT COUNT(DISTINCT post_id) FROM wp_postmeta WHERE meta_key = "language" AND meta_value = "en"');
echo "\nDistinct EN posts in postmeta: " . $stmt2->fetchColumn() . "\n";

$stmt3 = $pdo->query('SELECT COUNT(DISTINCT object_id) FROM wp_term_relationships WHERE term_taxonomy_id = 277');
echo "Distinct posts in term_taxonomy_id=277: " . $stmt3->fetchColumn() . "\n";

// Find duplicate meta entries
$stmt4 = $pdo->query('
    SELECT post_id, COUNT(*) as cnt
    FROM wp_postmeta
    WHERE meta_key = "language" AND meta_value = "en"
    GROUP BY post_id
    HAVING cnt > 1
');
echo "\nEN posts with duplicate language meta:\n";
while ($row = $stmt4->fetch()) {
    echo "  post_id=" . $row['post_id'] . ": " . $row['cnt'] . " entries\n";
}