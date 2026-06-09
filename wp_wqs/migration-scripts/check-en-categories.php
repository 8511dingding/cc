<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);

// Count categories with -en suffix
$stmt = $pdo->query("
    SELECT COUNT(*) as cnt FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-en'
");
echo "Categories with -en suffix: " . $stmt->fetchColumn() . "\n";

// List all -en categories
$stmt = $pdo->query("
    SELECT t.term_id, t.name, t.slug FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-en'
    ORDER BY t.name
");
$cats = $stmt->fetchAll();
echo "\nAll -en categories:\n";
foreach ($cats as $c) {
    echo "  ID " . $c['term_id'] . ": " . $c['name'] . " (" . $c['slug'] . ")\n";
}