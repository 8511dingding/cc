<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);

// Get all -en categories and check their parent assignments
$stmt = $pdo->query("
    SELECT t.term_id, t.name, t.slug, tt.parent, p.name as parent_name, p.slug as parent_slug
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    LEFT JOIN wp_terms p ON tt.parent = p.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-en'
    ORDER BY tt.parent, t.name
");
$cats = $stmt->fetchAll();

echo "Categories with parent assignments:\n\n";
$with_parent = 0;
$without_parent = 0;
foreach ($cats as $c) {
    if ($c['parent'] > 0) {
        $with_parent++;
        echo "  [ID " . $c['term_id'] . "] " . $c['name'] . " (parent: " . $c['parent_name'] . " - " . $c['parent_slug'] . ")\n";
    } else {
        $without_parent++;
        echo "  [ID " . $c['term_id'] . "] " . $c['name'] . " (NO PARENT)\n";
    }
}
echo "\nWith parent: $with_parent\n";
echo "Without parent: $without_parent\n";
echo "\nTop-level -en categories (parent = 0):\n";
foreach ($cats as $c) {
    if ($c['parent'] == 0) {
        echo "  ID " . $c['term_id'] . ": " . $c['name'] . " (" . $c['slug'] . ")\n";
    }
}