<?php
/**
 * Fix self-referencing EN-ZH posts
 * These posts have self-referencing en_post_id and zh_post_id, and duplicate language=zh meta
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$pdo_old = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_joomla;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "=== Fixing Self-Referencing EN-ZH Posts ===\n\n";

// Self-referencing post IDs (where en_post_id = post_id)
$self_ref_ids = [1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1528, 1529, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 1595, 1596, 1598, 1599, 1601, 1602, 1603, 1607];

// Check if any of these have genuine ZH counterparts in JoomFish
echo "Checking JoomFish for these posts:\n";
$genuine_zh_pairs = 0;
$no_zh_pairs = 0;

foreach ($self_ref_ids as $wp_id) {
    $stmt = $pdo->prepare("SELECT post_title FROM wp_posts WHERE ID = ?");
    $stmt->execute([$wp_id]);
    $title = $stmt->fetchColumn();

    // Find reference_id for this title in jos_content
    $stmt2 = $pdo_old->prepare("SELECT id FROM jos_content WHERE title = ?");
    $stmt2->execute([$title]);
    $ref_id = $stmt2->fetchColumn();

    if ($ref_id) {
        // Check JoomFish for this reference_id - look for language_id=2 (ZH)
        $stmt3 = $pdo_old->prepare("
            SELECT reference_id, value, language_id
            FROM jos_jf_content
            WHERE reference_id = ? AND reference_table = 'content' AND reference_field = 'title' AND language_id = 2
        ");
        $stmt3->execute([$ref_id]);
        $zh_entry = $stmt3->fetch();

        if ($zh_entry && trim($zh_entry['value']) !== $title) {
            // Found a different ZH title
            $zh_title = trim($zh_entry['value']);
            $genuine_zh_pairs++;

            // Look up the WP post with this ZH title
            $stmt4 = $pdo->prepare("SELECT ID FROM wp_posts WHERE post_title = ? AND post_type = 'post'");
            $stmt4->execute([$zh_title]);
            $zh_wp_id = $stmt4->fetchColumn();

            if ($zh_wp_id) {
                echo "WP[$wp_id] '$title' <-> ZH[$zh_wp_id] '$zh_title'\n";
            }
        } else {
            $no_zh_pairs++;
        }
    }
}

echo "\nGenuine ZH pairs found: $genuine_zh_pairs\n";
echo "No genuine ZH translation: $no_zh_pairs\n\n";

// Now fix: Set these 54 posts as English-only (language=en, no zh_post_id/en_post_id meta)
echo "Setting these posts as English-only with proper language term...\n";

$lang_en = 277;

$updated = 0;
foreach ($self_ref_ids as $wp_id) {
    // Insert language=en meta
    $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'en')")->execute([$wp_id]);

    // Insert language term
    $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")->execute([$wp_id, $lang_en]);

    $updated++;
}

echo "Updated $updated posts as English-only\n\n";

// Verify
echo "=== Verification ===\n";
$stmt = $pdo->query("SELECT COUNT(DISTINCT m.post_id) FROM wp_postmeta m WHERE m.meta_key = 'language' AND m.meta_value = 'en'");
echo "EN posts: " . $stmt->fetchColumn() . "\n";

$stmt2 = $pdo->query("SELECT COUNT(DISTINCT m.post_id) FROM wp_postmeta m WHERE m.meta_key = 'language' AND m.meta_value = 'zh'");
echo "ZH posts: " . $stmt2->fetchColumn() . "\n";

$stmt3 = $pdo->query("SELECT COUNT(DISTINCT tr.object_id) FROM wp_term_relationships tr WHERE tr.term_taxonomy_id = $lang_en");
echo "Posts with EN term: " . $stmt3->fetchColumn() . "\n";

// Check a few samples
echo "\nSample of fixed posts:\n";
$stmt4 = $pdo->query("
    SELECT p.ID, p.post_title, m.meta_value as lang
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'language'
    WHERE p.ID IN (1520, 1521, 1522)
");
while ($row = $stmt4->fetch()) {
    echo "  {$row['ID']}: {$row['post_title']} ({$row['lang']})\n";
}