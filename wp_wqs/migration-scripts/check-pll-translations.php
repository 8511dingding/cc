<?php
/**
 * Verify Polylang translations are correct
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// Get all -en categories with their translation info
$stmt = $pdo->query("
    SELECT t.term_id, t.name, t.slug, pll.translation_id, pll.language
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    JOIN wp_pll_translations pll ON tt.term_taxonomy_id = pll.element_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-en'
    ORDER BY t.name
");
$en_cats = $stmt->fetchAll();

echo "English categories and their translation groups:\n\n";

$count = 0;
foreach ($en_cats as $cat) {
    $count++;
    // Find all translations in this group
    $stmt2 = $pdo->prepare("
        SELECT t.name, t.slug, pll.language
        FROM wp_pll_translations pll
        JOIN wp_term_taxonomy tt ON pll.element_id = tt.term_taxonomy_id
        JOIN wp_terms t ON tt.term_id = t.term_id
        WHERE pll.translation_id = ?
        ORDER BY pll.language
    ");
    $stmt2->execute([$cat['translation_id']]);
    $translations = $stmt2->fetchAll();

    $trans_names = [];
    foreach ($translations as $t) {
        $trans_names[] = "{$t['language']}: {$t['name']}";
    }

    echo "[$count] {$cat['name']} (slug: {$cat['slug']})\n";
    echo "    Translation group {$cat['translation_id']}: " . implode(", ", $trans_names) . "\n\n";
}

echo "\nTotal -en categories: $count\n";