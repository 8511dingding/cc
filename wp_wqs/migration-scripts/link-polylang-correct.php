<?php
/**
 * Properly link EN-ZH posts using Polylang structure
 * translation_id = source post ID (English post ID)
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$pdo_old = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_joomla;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "=== Linking EN-ZH posts via Polylang (Corrected) ===\n\n";

// Language term IDs from Polylang
$lang_en = 277;
$lang_zh = 280;

// Recreate table with correct structure
$pdo->exec('DROP TABLE IF EXISTS wp_pll_translations');
$pdo->exec("
CREATE TABLE wp_pll_translations (
    id bigint(20) NOT NULL AUTO_INCREMENT,
    translation_id bigint(20) NOT NULL,
    language varchar(32) NOT NULL,
    source_language varchar(32) DEFAULT NULL,
    PRIMARY KEY (id),
    KEY translation_id (translation_id),
    KEY language (language)
) DEFAULT CHARSET=utf8mb4
");

// Clear existing language relationships
$pdo->exec("DELETE FROM wp_term_relationships WHERE term_taxonomy_id IN ($lang_en, $lang_zh)");
$pdo->exec("DELETE FROM wp_postmeta WHERE meta_key IN ('en_post_id', 'zh_post_id', 'language')");
echo "Cleared existing data.\n\n";

// Get JoomFish translation mapping
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

// Get EN titles from jos_content
$stmt2 = $pdo_old->query("SELECT id, title FROM jos_content");
$joomla_en_titles = [];
while ($row = $stmt2->fetch()) {
    $joomla_en_titles[$row['id']] = $row['title'];
}

// Build complete mapping
$jf_mapping = [];
foreach ($translations as $ref_id => $data) {
    if (isset($joomla_en_titles[$ref_id])) {
        $jf_mapping[$ref_id] = [
            'en_title' => trim($joomla_en_titles[$ref_id]),
            'zh_title' => $data['zh_title']
        ];
    }
}

echo "Found " . count($jf_mapping) . " article pairs in JoomFish\n";

// Find WordPress posts by title
$stmt_wp = $pdo->query("SELECT ID, post_title, post_name FROM wp_posts WHERE post_type = 'post' AND post_status = 'publish'");
$wp_posts = $stmt_wp->fetchAll(PDO::FETCH_ASSOC);

// Build index by title
$wp_by_title = [];
foreach ($wp_posts as $p) {
    $wp_by_title[$p['post_title']] = $p['ID'];
}

echo "Found " . count($wp_posts) . " WordPress posts\n\n";

// Link each pair
$linked = 0;
foreach ($jf_mapping as $ref_id => $titles) {
    $en_title = $titles['en_title'];
    $zh_title = $titles['zh_title'];

    $en_wp_id = $wp_by_title[$en_title] ?? null;
    $zh_wp_id = $wp_by_title[$zh_title] ?? null;

    if (!$en_wp_id || !$zh_wp_id) {
        continue;
    }

    // Set language meta
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'en')")->execute([$en_wp_id]);
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'zh')")->execute([$zh_wp_id]);

    // Set cross-reference
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'zh_post_id', ?)")->execute([$en_wp_id, $zh_wp_id]);
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'en_post_id', ?)")->execute([$zh_wp_id, $en_wp_id]);

    // Set language term
    $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")->execute([$en_wp_id, $lang_en]);
    $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")->execute([$zh_wp_id, $lang_zh]);

    // Create Polylang translation entry
    // translation_id = source post ID (English post ID)
    $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language) VALUES (?, 'en', NULL)")->execute([$en_wp_id]);
    $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language) VALUES (?, 'zh', 'en')")->execute([$en_wp_id]);

    $linked++;

    if ($linked <= 5) {
        echo "Linked: EN [$en_wp_id] '$en_title' <-> ZH [$zh_wp_id] '$zh_title'\n";
    }
}

echo "\n=== Result ===\n";
echo "Total linked pairs: $linked\n";

// Verify
$stmt_count = $pdo->query("SELECT COUNT(*) FROM wp_pll_translations");
echo "Translation entries: " . $stmt_count->fetchColumn() . "\n";

$stmt_en = $pdo->query("SELECT COUNT(DISTINCT tr.object_id) FROM wp_term_relationships tr WHERE tr.term_taxonomy_id = $lang_en");
echo "EN posts with language: " . $stmt_en->fetchColumn() . "\n";

$stmt_zh = $pdo->query("SELECT COUNT(DISTINCT tr.object_id) FROM wp_term_relationships tr WHERE tr.term_taxonomy_id = $lang_zh");
echo "ZH posts with language: " . $stmt_zh->fetchColumn() . "\n";

// Test a specific pair
echo "\nTesting post 186 <-> 1600:\n";
$stmt_test = $pdo->prepare("SELECT * FROM wp_pll_translations WHERE translation_id = ?");
$stmt_test->execute([186]);
while ($row = $stmt_test->fetch()) {
    echo "  id={$row['id']}, trans_id={$row['translation_id']}, lang={$row['language']}, source={$row['source_language']}\n";
}