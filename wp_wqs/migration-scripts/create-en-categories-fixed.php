<?php
/**
 * Create missing English (-en) categories for existing Chinese (-zh) categories
 * FIXED VERSION - creates correct Polylang translation links
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// Mapping of Chinese to English terms
$zh_to_en = [
    '摄影' => 'Photography',
    '展览' => 'Exhibitions',
    '工作照' => 'Shooting',
    '评论' => 'Reviews',
];

// Get all Chinese categories with -zh suffix
$stmt = $pdo->query("
    SELECT t.term_id, t.name, t.slug, tt.parent, tt.term_taxonomy_id
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-zh'
    ORDER BY t.name
");
$zh_categories = $stmt->fetchAll();

// Get existing English versions
$stmt = $pdo->query("
    SELECT t.slug
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = 'category'
    AND t.slug LIKE '%-en'
");
$existing_en_slugs = $stmt->fetchAll(PDO::FETCH_COLUMN);

// Find categories to create
$to_create = [];
foreach ($zh_categories as $zh) {
    $expected_en_slug = str_replace('-zh', '-en', $zh['slug']);

    // Special case: photography-zh-zh -> photography-en (not photography-en-en)
    if ($expected_en_slug === 'photography-en-en') {
        $expected_en_slug = 'photography-en';
    }

    if (!in_array($expected_en_slug, $existing_en_slugs)) {
        // Generate English name
        $en_name = str_replace(
            array_keys($zh_to_en),
            array_values($zh_to_en),
            $zh['name']
        );
        $to_create[] = [
            'zh_id' => $zh['term_id'],
            'zh_ttid' => $zh['term_taxonomy_id'],
            'zh_name' => $zh['name'],
            'zh_slug' => $zh['slug'],
            'en_name' => $en_name,
            'en_slug' => $expected_en_slug,
            'parent' => $zh['parent']
        ];
    }
}

echo "Found " . count($to_create) . " categories to create\n\n";

// Get next translation ID (higher than any existing)
$stmt = $pdo->query("SELECT MAX(translation_id) FROM wp_pll_translations");
$next_translation_id = ($stmt->fetchColumn() ?: 10000) + 1;
echo "Starting translation ID: $next_translation_id\n\n";

$created = 0;
$pdo->beginTransaction();

try {
    foreach ($to_create as $cat) {
        echo "Creating: {$cat['en_name']} ({$cat['en_slug']})\n";
        echo "  -> Translation of: {$cat['zh_name']} ({$cat['zh_slug']})\n";

        // Insert the English term
        $pdo->prepare("INSERT INTO wp_terms (name, slug) VALUES (?, ?)")
            ->execute([$cat['en_name'], $cat['en_slug']]);
        $en_term_id = $pdo->lastInsertId();

        // Insert term_taxonomy (parent = 0 for now, since all Chinese cats have parent = 0)
        $pdo->prepare("INSERT INTO wp_term_taxonomy (term_id, taxonomy, description, parent, count) VALUES (?, 'category', '', 0, 0)")
            ->execute([$en_term_id]);
        $en_ttid = $pdo->lastInsertId();

        // Create NEW translation group with both Chinese and English
        // First update the Chinese category to be in this new group
        $pdo->prepare("UPDATE wp_pll_translations SET translation_id = ? WHERE element_id = ? AND element_id != 0")
            ->execute([$next_translation_id, $cat['zh_ttid']]);

        // Then insert the English category into the same group
        $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, element_id) VALUES (?, 'en', ?)")
            ->execute([$next_translation_id, $en_ttid]);

        echo "  -> Created new translation group $next_translation_id\n";
        $next_translation_id++;
        $created++;
        echo "\n";
    }

    $pdo->commit();
    echo "\n=== Complete ===\n";
    echo "Created: $created categories\n";
} catch (Exception $e) {
    $pdo->rollBack();
    die("Error: " . $e->getMessage() . "\n");
}