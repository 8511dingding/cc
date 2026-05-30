<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check all language-related terms
$stmt = $pdo->query('
    SELECT t.term_id, t.name, t.slug, tt.taxonomy, tt.count
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = "language"
');
echo "Language terms:\n";
while ($row = $stmt->fetch()) {
    echo "  {$row['term_id']}: {$row['name']} (slug: {$row['slug']}, count: {$row['count']})\n";
}