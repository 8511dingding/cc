<?php
/**
 * Check category structure
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// Get categories WITHOUT -zh or -en suffix (base categories)
$stmt = $pdo->query("
    SELECT t.term_id, t.name, t.slug, tt.parent
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug NOT LIKE '%-zh'
    AND t.slug NOT LIKE '%-en'
    ORDER BY t.name
");
$base_categories = $stmt->fetchAll();

echo "Base categories (no -zh or -en suffix): " . count($base_categories) . "\n\n";

// Count how many have Chinese versions
$stmt_zh = $pdo->query("
    SELECT COUNT(*) FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-zh'
");
$zh_count = $stmt_zh->fetchColumn();

echo "Chinese versions (-zh): " . $zh_count . "\n";

// Count how many have English versions
$stmt_en = $pdo->query("
    SELECT COUNT(*) FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-en'
");
$en_count = $stmt_en->fetchColumn();

echo "English versions (-en): " . $en_count . "\n";

// Show base categories that don't have -zh version
$zh_slugs = [];
$stmt = $pdo->query("
    SELECT slug FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category' AND slug LIKE '%-zh'
");
while ($row = $stmt->fetch()) {
    $zh_slugs[] = $row['slug'];
}

echo "\n=== Base categories MISSING Chinese (-zh) version ===\n";
$missing_zh = 0;
foreach ($base_categories as $base) {
    $expected_zh = $base['slug'] . '-zh';
    if (!in_array($expected_zh, $zh_slugs)) {
        echo "ID " . $base['term_id'] . ": " . $base['name'] . " (slug: " . $base['slug'] . ")\n";
        $missing_zh++;
        if ($missing_zh >= 20) {
            echo "... and more\n";
            break;
        }
    }
}
echo "Total missing zh: " . $missing_zh . "\n";