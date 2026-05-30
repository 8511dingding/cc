<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check if EN and ZH posts have the same translation_id (group)
$stmt = $pdo->prepare("SELECT translation_id, language, element_id FROM wp_pll_translations WHERE element_id = ?");
$stmt->execute([101]);
echo "Post 101 (EN) translations:\n";
while ($row = $stmt->fetch()) {
    echo "  trans_id={$row['translation_id']}, lang={$row['language']}, elem={$row['element_id']}\n";
}

$stmt2 = $pdo->prepare("SELECT translation_id, language, element_id FROM wp_pll_translations WHERE element_id = ?");
$stmt2->execute([1431]);
echo "\nPost 1431 (ZH) translations:\n";
while ($row = $stmt2->fetch()) {
    echo "  trans_id={$row['translation_id']}, lang={$row['language']}, elem={$row['element_id']}\n";
}

// Check how many EN posts have ZH translations
$stmt3 = $pdo->query("
    SELECT COUNT(DISTINCT t1.translation_id)
    FROM wp_pll_translations t1
    JOIN wp_pll_translations t2 ON t1.translation_id = t2.translation_id AND t2.language = 'zh'
    WHERE t1.language = 'en'
");
echo "\nEN posts with ZH translations: " . $stmt3->fetchColumn() . "\n";

// Check all translations that have ZH
$stmt4 = $pdo->query("
    SELECT t1.translation_id, t1.element_id as en_id, t2.element_id as zh_id
    FROM wp_pll_translations t1
    JOIN wp_pll_translations t2 ON t1.translation_id = t2.translation_id AND t2.language = 'zh'
    WHERE t1.language = 'en'
    LIMIT 5
");
echo "\nSample translation groups:\n";
while ($row = $stmt4->fetch()) {
    echo "  trans_id={$row['translation_id']}: EN {$row['en_id']} <-> ZH {$row['zh_id']}\n";
}