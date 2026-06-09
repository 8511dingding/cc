<?php
/**
 * Delete the incorrectly created -en categories and their translations
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "Finding incorrectly created -en categories...\n\n";

// Find -en categories that were created (term_id > 550 and < 600 based on earlier output)
$stmt = $pdo->query("
    SELECT term_id, name, slug FROM wp_terms
    WHERE slug LIKE '%-en'
    AND term_id >= 550 AND term_id <= 600
    ORDER BY term_id
");
$bad_cats = $stmt->fetchAll();

echo "Found " . count($bad_cats) . " potentially incorrect categories:\n";
foreach ($bad_cats as $cat) {
    echo "  ID {$cat['term_id']}: {$cat['name']} ({$cat['slug']})\n";
}

echo "\nDeleting these categories...\n";
$deleted = 0;
foreach ($bad_cats as $cat) {
    // Get term_taxonomy_id
    $stmt = $pdo->prepare("SELECT term_taxonomy_id FROM wp_term_taxonomy WHERE term_id = ?");
    $stmt->execute([$cat['term_id']]);
    $tt_id = $stmt->fetchColumn();

    if ($tt_id) {
        // Delete from wp_pll_translations
        $pdo->prepare("DELETE FROM wp_pll_translations WHERE element_id = ?")->execute([$tt_id]);

        // Delete from wp_term_relationships
        $pdo->prepare("DELETE FROM wp_term_relationships WHERE term_taxonomy_id = ?")->execute([$tt_id]);

        // Delete from wp_term_taxonomy
        $pdo->prepare("DELETE FROM wp_term_taxonomy WHERE term_id = ?")->execute([$cat['term_id']]);

        // Delete from wp_terms
        $pdo->prepare("DELETE FROM wp_terms WHERE term_id = ?")->execute([$cat['term_id']]);

        echo "  Deleted: {$cat['name']} (ID: {$cat['term_id']})\n";
        $deleted++;
    }
}

echo "\nTotal deleted: $deleted\n";

// Verify count now
$stmt = $pdo->query("
    SELECT COUNT(*) FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category' AND t.slug LIKE '%-en'
");
echo "Remaining -en categories: " . $stmt->fetchColumn() . "\n";