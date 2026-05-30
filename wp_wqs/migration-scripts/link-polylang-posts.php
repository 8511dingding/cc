<?php
/**
 * Link EN and ZH posts using Polylang structure
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "=== Linking EN-ZH posts via Polylang ===\n\n";

// Language term IDs from Polylang
$lang_en = 277;  // English
$lang_zh = 280;  // 中文 (中国)

// Recreate table with correct structure
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

// Clear existing language relationships
$pdo->exec("DELETE FROM wp_term_relationships WHERE term_taxonomy_id IN ($lang_en, $lang_zh)");
echo "Cleared existing data.\n\n";

// Get all EN posts that have a Chinese translation
$stmt = $pdo->query("
    SELECT p.ID as en_id, m.meta_value as zh_id
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'zh_post_id'
    JOIN wp_posts zh ON m.meta_value = zh.ID AND zh.post_type = 'post'
    WHERE p.post_type = 'post' AND p.post_status = 'publish'
");
$pairs = $stmt->fetchAll();

echo "Found " . count($pairs) . " EN-ZH pairs to link\n\n";

// Link each pair
$linked = 0;
$errors = 0;

foreach ($pairs as $pair) {
    $en_id = $pair['en_id'];
    $zh_id = $pair['zh_id'];

    try {
        // Add language term relationships
        $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")
            ->execute([$en_id, $lang_en]);
        $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")
            ->execute([$zh_id, $lang_zh]);

        // Create EN translation entry
        $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (0, 'en', NULL, ?)")
            ->execute([$en_id]);
        $en_row_id = $pdo->lastInsertId();
        $pdo->exec("UPDATE wp_pll_translations SET translation_id = $en_row_id WHERE id = $en_row_id");

        // Create ZH translation entry
        $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'zh', 'en', ?)")
            ->execute([$en_row_id, $zh_id]);

        $linked++;
    } catch (Exception $e) {
        $errors++;
        if ($errors <= 5) {
            echo "Error linking $en_id -> $zh_id: " . $e->getMessage() . "\n";
        }
    }
}

echo "\n=== Complete ===\n";
echo "Linked: $linked EN-ZH pairs\n";
echo "Errors: $errors\n";

// Verify
echo "\nVerification:\n";
$stmt_count = $pdo->query("SELECT COUNT(*) FROM wp_pll_translations");
echo "Translation entries: " . $stmt_count->fetchColumn() . "\n";

$stmt_en = $pdo->query("SELECT COUNT(DISTINCT tr.object_id) FROM wp_term_relationships tr WHERE tr.term_taxonomy_id = $lang_en");
echo "Posts with English language: " . $stmt_en->fetchColumn() . "\n";

$stmt_zh = $pdo->query("SELECT COUNT(DISTINCT tr.object_id) FROM wp_term_relationships tr WHERE tr.term_taxonomy_id = $lang_zh");
echo "Posts with Chinese language: " . $stmt_zh->fetchColumn() . "\n";

// Sample linked pairs
echo "\nSample linked pairs:\n";
$stmt_sample = $pdo->query("
    SELECT t1.element_id as en_id, t2.element_id as zh_id
    FROM wp_pll_translations t1
    JOIN wp_pll_translations t2 ON t1.translation_id = t2.translation_id
    WHERE t1.language = 'en' AND t2.language = 'zh'
    ORDER BY t1.element_id
    LIMIT 5
");
while ($row = $stmt_sample->fetch()) {
    $stmt_en_title = $pdo->prepare("SELECT post_title FROM wp_posts WHERE ID = ?");
    $stmt_en_title->execute([$row['en_id']]);
    $en_title = $stmt_en_title->fetchColumn();

    $stmt_zh_title = $pdo->prepare("SELECT post_title FROM wp_posts WHERE ID = ?");
    $stmt_zh_title->execute([$row['zh_id']]);
    $zh_title = $stmt_zh_title->fetchColumn();

    echo "  EN [$row[en_id]]: $en_title\n";
    echo "  ZH [$row[zh_id]]: $zh_title\n\n";
}