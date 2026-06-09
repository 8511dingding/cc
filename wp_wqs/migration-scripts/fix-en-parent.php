<?php
/**
 * Fix parent assignments for newly created -en categories
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "Fixing parent assignments for -en categories...\n\n";

// Get all -en categories without parent or with wrong parent
$stmt = $pdo->query("
    SELECT t.term_id, t.name, t.slug, tt.parent, tt.term_taxonomy_id
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-en'
    AND t.slug NOT IN ('photography-en', 'exhibitions-en', 'reviews-en', 'video-en', 'shooting-en', 'others-en', 'biography-en', 'contact-en')
    ORDER BY t.name
");
$en_categories = $stmt->fetchAll();

$fixed = 0;
foreach ($en_categories as $en_cat) {
    // Get the Chinese version's slug
    $zh_slug = str_replace('-en', '-zh', $en_cat['slug']);

    // Find the Chinese version and its parent
    $stmt = $pdo->prepare("
        SELECT t.term_id, t.slug, tt.parent
        FROM wp_terms t
        JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
        WHERE tt.taxonomy = 'category' AND t.slug = ?
    ");
    $stmt->execute([$zh_slug]);
    $zh_cat = $stmt->fetch();

    if (!$zh_cat || $zh_cat['parent'] == 0) {
        // No parent to assign
        continue;
    }

    // Find the English parent
    $zh_parent_slug = $zh_cat['slug'];
    $en_parent_slug = str_replace('-zh', '-en', $zh_parent_slug);

    $stmt = $pdo->prepare("
        SELECT term_id FROM wp_terms WHERE slug = ?
    ");
    $stmt->execute([$en_parent_slug]);
    $en_parent_id = $stmt->fetchColumn();

    if ($en_parent_id) {
        // Update the parent
        $stmt = $pdo->prepare("UPDATE wp_term_taxonomy SET parent = ? WHERE term_id = ?");
        $stmt->execute([$en_parent_id, $en_cat['term_id']]);

        $en_parent_slug_display = str_replace('-', ' ', $en_parent_slug);
        echo "Fixed: {$en_cat['name']} -> parent: $en_parent_id ($en_parent_slug_display)\n";
        $fixed++;
    }
}

echo "\nTotal fixed: $fixed\n";

// Now let's also check the base -en categories that exist (not newly created)
echo "\nChecking base -en categories parent status:\n";
$stmt = $pdo->query("
    SELECT t.term_id, t.name, t.slug, tt.parent
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug IN ('photography-en', 'exhibitions-en', 'reviews-en', 'video-en', 'shooting-en', 'others-en', 'biography-en', 'contact-en')
");
$base_cats = $stmt->fetchAll();
foreach ($base_cats as $cat) {
    echo "  ID {$cat['term_id']}: {$cat['name']} (slug: {$cat['slug']}) - parent: {$cat['parent']}\n";
}