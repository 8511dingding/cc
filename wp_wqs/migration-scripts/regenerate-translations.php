<?php
/**
 * Regenerate translation groups with proper translation_id structure
 * translation_id should be a unique group ID, NOT equal to element_id
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "=== Regenerating Translation Groups with Proper translation_id ===\n\n";

// Step 1: Clear existing translation groups
$pdo->exec("DELETE FROM wp_pll_translations");
echo "Cleared wp_pll_translations\n";

// Step 2: Get all EN-ZH pairs from JoomFish
$pdo_old = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_joomla;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$stmt = $pdo_old->query("
    SELECT reference_id, reference_field, value, language_id
    FROM jos_jf_content
    WHERE reference_table = 'content' AND reference_field = 'title'
    ORDER BY reference_id
");

$translations = [];
while ($row = $stmt->fetch()) {
    $ref_id = $row['reference_id'];
    if (!isset($translations[$ref_id])) {
        $translations[$ref_id] = ['en_title' => '', 'zh_title' => ''];
    }
    if ($row['language_id'] == 2) {
        $translations[$ref_id]['zh_title'] = trim($row['value']);
    }
}

$stmt2 = $pdo_old->query("SELECT id, title FROM jos_content");
$joomla_en_titles = [];
while ($row = $stmt2->fetch()) {
    $joomla_en_titles[$row['id']] = $row['title'];
}

$jf_mapping = [];
foreach ($translations as $ref_id => $data) {
    if (isset($joomla_en_titles[$ref_id]) && !empty($data['zh_title'])) {
        $jf_mapping[trim($joomla_en_titles[$ref_id])] = $data['zh_title'];
    }
}

echo "JoomFish translation pairs: " . count($jf_mapping) . "\n\n";

// Step 3: Build WP post index by title
$stmt_wp = $pdo->query("SELECT ID, post_title, post_name FROM wp_posts WHERE post_type = 'post' AND post_status = 'publish'");
$wp_posts = $stmt_wp->fetchAll();
$wp_by_title = [];
foreach ($wp_posts as $p) {
    $wp_by_title[$p['post_title']] = $p['ID'];
}

echo "WordPress posts: " . count($wp_posts) . "\n\n";

// Step 4: Regenerate translation groups
// IMPORTANT: translation_id must be a unique ID, NOT equal to element_id
// We'll use element_id + a large offset to ensure uniqueness
$group_id = 10000; // Start groups at a high number to avoid collision

$linked = 0;
foreach ($jf_mapping as $en_title => $zh_title) {
    $en_id = $wp_by_title[$en_title] ?? null;
    $zh_id = $wp_by_title[$zh_title] ?? null;

    if (!$en_id || !$zh_id) {
        continue;
    }

    $group_id++;

    // EN entry: translation_id = group_id (not element_id), source_language = NULL
    $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'en', NULL, ?)")->execute([$group_id, $en_id]);

    // ZH entry: translation_id = same group_id, source_language = 'en'
    $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'zh', 'en', ?)")->execute([$group_id, $zh_id]);

    $linked++;
}

echo "Created $linked EN-ZH translation groups\n";

// Step 5: Also handle the homepage (post 331) with a unique group
$group_id++;
$pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'en', NULL, ?)")->execute([$group_id, 331]);
$pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'zh', 'en', ?)")->execute([$group_id, 331]);
echo "Created translation group for homepage\n";

// Verify
echo "\n=== Verification ===\n";
$stmt_verify = $pdo->query("SELECT translation_id, language, element_id FROM wp_pll_translations WHERE element_id IN (101, 1431, 331) ORDER BY element_id, language");
echo "Translation entries for posts 101, 1431, 331:\n";
while ($row = $stmt_verify->fetch()) {
    echo "  group={$row['translation_id']}, lang={$row['language']}, elem={$row['element_id']}\n";
}

// Clear Polylang cache
$pdo->query("DELETE FROM wp_options WHERE option_name = '_transient_pll_languages_list'");
echo "\nCleared Polylang cache\n";