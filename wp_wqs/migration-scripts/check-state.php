<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');
echo "=== Current State ===\n";
$stmt = $pdo->query("SELECT m.meta_value as lang, COUNT(DISTINCT m.post_id) as cnt FROM wp_postmeta m WHERE m.meta_key = 'language' GROUP BY m.meta_value");
while ($row = $stmt->fetch()) {
    echo "  " . $row['lang'] . ": " . $row['cnt'] . "\n";
}

$stmt2 = $pdo->query("SELECT COUNT(*) FROM wp_pll_translations");
echo "\nTranslation entries: " . $stmt2->fetchColumn() . "\n";

$stmt3 = $pdo->query("SELECT term_taxonomy_id, COUNT(*) FROM wp_term_relationships WHERE term_taxonomy_id IN (277, 280) GROUP BY term_taxonomy_id");
echo "\nTerm relationships:\n";
while ($row = $stmt3->fetch()) {
    echo "  term_id=" . $row['term_taxonomy_id'] . ": " . $row['COUNT(*)'] . "\n";
}

echo "\nSample of correctly linked EN-ZH pairs:\n";
$stmt4 = $pdo->query("
    SELECT t1.element_id as en_id, t2.element_id as zh_id
    FROM wp_pll_translations t1
    JOIN wp_pll_translations t2 ON t1.translation_id = t2.translation_id AND t2.language = 'zh'
    WHERE t1.language = 'en'
    AND t1.element_id != t2.element_id
    LIMIT 5
");
while ($row = $stmt4->fetch()) {
    $stmt_en = $pdo->prepare("SELECT post_title FROM wp_posts WHERE ID = ?");
    $stmt_en->execute([$row['en_id']]);
    $en_title = $stmt_en->fetchColumn();

    $stmt_zh = $pdo->prepare("SELECT post_title FROM wp_posts WHERE ID = ?");
    $stmt_zh->execute([$row['zh_id']]);
    $zh_title = $stmt_zh->fetchColumn();

    echo "  EN [{$row['en_id']}]: $en_title\n";
    echo "  ZH [{$row['zh_id']}]: $zh_title\n\n";
}