<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check term_relationships for language taxonomies
$stmt = $pdo->query('
    SELECT term_taxonomy_id, COUNT(*) as cnt
    FROM wp_term_relationships
    WHERE term_taxonomy_id IN (277, 280)
    GROUP BY term_taxonomy_id
');
echo "Term relationships:\n";
while ($row = $stmt->fetch()) {
    echo "  term_taxonomy_id=" . $row['term_taxonomy_id'] . ": " . $row['cnt'] . " relationships\n";
}

// Check postmeta counts
$stmt2 = $pdo->query('
    SELECT meta_value, COUNT(*) as cnt
    FROM wp_postmeta
    WHERE meta_key = "language"
    GROUP BY meta_value
');
echo "\nPostmeta language counts:\n";
while ($row = $stmt2->fetch()) {
    echo "  " . $row['meta_value'] . ": " . $row['cnt'] . "\n";
}

// Verify post 101 has proper relationships
$stmt3 = $pdo->query('SELECT object_id, term_taxonomy_id FROM wp_term_relationships WHERE object_id = 101');
echo "\nTerm relationships for post 101:\n";
while ($row = $stmt3->fetch()) {
    echo "  object_id=" . $row['object_id'] . ", term_taxonomy_id=" . $row['term_taxonomy_id'] . "\n";
}

// Verify post 1431 has proper relationships
$stmt4 = $pdo->query('SELECT object_id, term_taxonomy_id FROM wp_term_relationships WHERE object_id = 1431');
echo "\nTerm relationships for post 1431:\n";
while ($row = $stmt4->fetch()) {
    echo "  object_id=" . $row['object_id'] . ", term_taxonomy_id=" . $row['term_taxonomy_id'] . "\n";
}