<?php
/**
 * Clean up and properly link EN-ZH posts
 * Keep EN posts, properly link true ZH translations, delete incorrect ZH posts
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$pdo_old = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_joomla;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "=== Cleaning up and Properly Linking EN-ZH Posts ===\n\n";

// Language term IDs
$lang_en = 277;
$lang_zh = 280;

// Clear all existing data
$pdo->exec("DELETE FROM wp_pll_translations");
$pdo->exec("DELETE FROM wp_term_relationships WHERE term_taxonomy_id IN ($lang_en, $lang_zh)");
$pdo->exec("DELETE FROM wp_postmeta WHERE meta_key IN ('en_post_id', 'zh_post_id', 'language')");

// Recreate pll_translations table with element_id
$pdo->exec('DROP TABLE IF EXISTS wp_pll_translations');
$pdo->exec("
CREATE TABLE wp_pll_translations (
    id bigint(20) NOT NULL AUTO_INCREMENT,
    translation_id bigint(20) NOT NULL,
    language varchar(32) NOT NULL,
    source_language varchar(32) DEFAULT NULL,
    element_id bigint(20) NOT NULL,
    PRIMARY KEY (id),
    KEY translation_id (translation_id),
    KEY language (language),
    KEY element_id (element_id)
) DEFAULT CHARSET=utf8mb4
");

echo "Cleared all existing data.\n\n";

// Step 1: Get JoomFish translation mapping (reference_id -> EN title, ZH title)
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

// Build JoomFish mapping: EN title -> ZH title
$jf_mapping = [];
foreach ($translations as $ref_id => $data) {
    if (isset($joomla_en_titles[$ref_id]) && !empty($data['zh_title'])) {
        $jf_mapping[trim($joomla_en_titles[$ref_id])] = $data['zh_title'];
    }
}

echo "JoomFish translation pairs: " . count($jf_mapping) . "\n";

// Step 2: Get all WordPress posts
$stmt_wp = $pdo->query("SELECT ID, post_title, post_name FROM wp_posts WHERE post_type = 'post' AND post_status = 'publish'");
$wp_posts = $stmt_wp->fetchAll();

// Build indices by title
$by_title = [];
foreach ($wp_posts as $p) {
    $by_title[$p['post_title']] = $p['ID'];
}

// Step 3: For each EN title with a ZH translation, create proper link
$linked = 0;
$deleted_zh = [];

foreach ($jf_mapping as $en_title => $zh_title) {
    $en_id = $by_title[$en_title] ?? null;
    $zh_id = $by_title[$zh_title] ?? null;

    if (!$en_id || !$zh_id) {
        continue;
    }

    // Verify they're both real posts
    $stmt_en = $pdo->prepare("SELECT ID FROM wp_posts WHERE ID = ? AND post_type = 'post'");
    $stmt_en->execute([$en_id]);
    $stmt_zh = $pdo->prepare("SELECT ID FROM wp_posts WHERE ID = ? AND post_type = 'post'");
    $stmt_zh->execute([$zh_id]);

    if (!$stmt_en->fetch() || !$stmt_zh->fetch()) {
        continue;
    }

    // Set language meta
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'en')")->execute([$en_id]);
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'zh')")->execute([$zh_id]);

    // Cross-reference
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'zh_post_id', ?)")->execute([$en_id, $zh_id]);
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'en_post_id', ?)")->execute([$zh_id, $en_id]);

    // Language term
    $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")->execute([$en_id, $lang_en]);
    $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")->execute([$zh_id, $lang_zh]);

    // Polylang translations with element_id
    $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'en', NULL, ?)")->execute([$en_id, $en_id]);
    $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'zh', 'en', ?)")->execute([$en_id, $zh_id]);

    $linked++;
}

echo "Properly linked: $linked EN-ZH pairs\n\n";

// Step 4: Find ZH posts that should be deleted (English content wrongly tagged as ZH)
$stmt_zh_posts = $pdo->query("
    SELECT p.ID, p.post_title, m.meta_value as language
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'language'
    WHERE p.post_type = 'post' AND m.meta_value = 'zh'
");
$zh_with_lang = $stmt_zh_posts->fetchAll(PDO::FETCH_ASSOC);
$zh_ids_with_lang = array_column($zh_with_lang, 'ID');

$to_delete = [];
foreach ($wp_posts as $p) {
    // If post has Chinese characters in title, it's likely true Chinese
    // If no Chinese chars and has English content, it might be wrongly tagged
    if (preg_match('/[\x{4e00}-\x{9fa5}]/u', $p['post_title'])) {
        continue; // Has Chinese, keep it
    }
    // No Chinese in title - check if it's in the correct translation list
    $is_translation = false;
    foreach ($jf_mapping as $en_title => $zh_title) {
        if ($zh_title === $p['post_title']) {
            $is_translation = true;
            break;
        }
    }
    if (!$is_translation && in_array($p['ID'], $zh_ids_with_lang)) {
        $to_delete[] = $p['ID'];
    }
}

echo "ZH posts to delete (wrongly tagged English content): " . count($to_delete) . "\n";
if (count($to_delete) > 0) {
    echo "IDs to delete: " . implode(', ', array_slice($to_delete, 0, 20)) . "\n";
}

// Delete the wrongly tagged posts
foreach ($to_delete as $zh_id) {
    // Delete postmeta
    $pdo->prepare("DELETE FROM wp_postmeta WHERE post_id = ?")->execute([$zh_id]);
    // Delete term_relationships
    $pdo->prepare("DELETE FROM wp_term_relationships WHERE object_id = ?")->execute([$zh_id]);
    // Delete translations
    $pdo->prepare("DELETE FROM wp_pll_translations WHERE element_id = ?")->execute([$zh_id]);
    // Delete post
    $pdo->prepare("DELETE FROM wp_posts WHERE ID = ?")->execute([$zh_id]);
    $deleted_zh[] = $zh_id;
}

echo "\nDeleted " . count($deleted_zh) . " wrongly tagged ZH posts\n";

// Final verification
echo "\n=== Final State ===\n";
$stmt_final_en = $pdo->query("SELECT COUNT(DISTINCT m.post_id) FROM wp_postmeta m WHERE m.meta_key = 'language' AND m.meta_value = 'en'");
echo "EN posts: " . $stmt_final_en->fetchColumn() . "\n";

$stmt_final_zh = $pdo->query("SELECT COUNT(DISTINCT m.post_id) FROM wp_postmeta m WHERE m.meta_key = 'language' AND m.meta_value = 'zh'");
echo "ZH posts: " . $stmt_final_zh->fetchColumn() . "\n";

$stmt_final_pll = $pdo->query("SELECT COUNT(*) FROM wp_pll_translations");
echo "Translation entries: " . $stmt_final_pll->fetchColumn() . "\n";

// Sample verification
echo "\nSample linked pairs:\n";
$stmt_sample = $pdo->query("
    SELECT t1.element_id as en_id, t2.element_id as zh_id
    FROM wp_pll_translations t1
    JOIN wp_pll_translations t2 ON t1.translation_id = t2.translation_id AND t1.language = 'en'
    WHERE t1.element_id != t2.element_id
    LIMIT 5
");
while ($row = $stmt_sample->fetch()) {
    $stmt_en = $pdo->prepare("SELECT post_title FROM wp_posts WHERE ID = ?");
    $stmt_en->execute([$row['en_id']]);
    $en_title = $stmt_en->fetchColumn();

    $stmt_zh = $pdo->prepare("SELECT post_title FROM wp_posts WHERE ID = ?");
    $stmt_zh->execute([$row['zh_id']]);
    $zh_title = $stmt_zh->fetchColumn();

    echo "  EN [$row[en_id]]: $en_title\n";
    echo "  ZH [$row[zh_id]]: $zh_title\n\n";
}