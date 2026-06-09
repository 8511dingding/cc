<?php
/**
 * Debug: Check Chinese categories and their parents
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// Get all -zh categories and their parents
$stmt = $pdo->query("
    SELECT t.term_id, t.name, t.slug, tt.parent, p.name as parent_name, p.slug as parent_slug
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    LEFT JOIN wp_terms p ON tt.parent = p.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-zh'
    ORDER BY tt.parent, t.name
");
$zh_categories = $stmt->fetchAll();

echo "Chinese (-zh) categories and their parents:\n\n";
$no_parent = 0;
$with_parent = 0;
foreach ($zh_categories as $c) {
    if ($c['parent'] == 0) {
        $no_parent++;
        echo "[NO PARENT] ID {$c['term_id']}: {$c['name']} ({$c['slug']})\n";
    } else {
        $with_parent++;
        echo "[PARENT: {$c['parent_slug']}] ID {$c['term_id']}: {$c['name']} ({$c['slug']})\n";
    }
}
echo "\nWith parent: $with_parent\n";
echo "Without parent: $no_parent\n";