<?php
/**
 * Analyze which posts need to be created
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);
$pdo_old = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_joomla;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// Get JoomFish EN-ZH mapping
$stmt = $pdo_old->query("
    SELECT c.id as joomla_id, c.title as en_title, jf.value as zh_title, jf2.value as zh_introtext
    FROM jos_content c
    JOIN jos_jf_content jf ON c.id = jf.reference_id AND jf.language_id = 2 AND jf.reference_field = 'title'
    LEFT JOIN jos_jf_content jf2 ON c.id = jf2.reference_id AND jf2.language_id = 2 AND jf2.reference_field = 'introtext'
    WHERE c.state = 1
");
$joomfish_pairs = [];
while ($row = $stmt->fetch()) {
    $joomfish_pairs[$row['joomla_id']] = [
        'en_title' => trim($row['en_title']),
        'zh_title' => trim($row['zh_title']),
        'zh_introtext' => $row['zh_introtext'],
        'joomla_id' => $row['joomla_id']
    ];
}

echo "JoomFish pairs: " . count($joomfish_pairs) . "\n";

// Get current WordPress posts that have language=zh meta
$stmt_wp = $pdo->query("
    SELECT p.ID, p.post_title, m.meta_value
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'language' AND m.meta_value = 'zh'
    WHERE p.post_type = 'post' AND p.post_status = 'publish'
");
$existing_zh = [];
while ($row = $stmt_wp->fetch()) {
    $existing_zh[$row['post_title']] = $row['ID'];
}
echo "Existing ZH posts in WordPress: " . count($existing_zh) . "\n";

// Find pairs that exist in JoomFish but not in WordPress
$need_to_create = [];
$already_exist = [];
foreach ($joomfish_pairs as $joomla_id => $data) {
    if (isset($existing_zh[$data['zh_title']])) {
        $already_exist[$data['en_title']] = $existing_zh[$data['zh_title']];
    } else {
        $need_to_create[$data['en_title']] = $data;
    }
}

echo "Already exist in WordPress: " . count($already_exist) . "\n";
echo "Need to create: " . count($need_to_create) . "\n";

if (count($need_to_create) > 0) {
    echo "\nFirst 20 that need to be created:\n";
    $i = 0;
    foreach ($need_to_create as $en_title => $data) {
        if ($i++ > 20) break;
        echo "  EN: $en_title -> ZH: " . $data['zh_title'] . "\n";
    }
}