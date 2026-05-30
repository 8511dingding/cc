<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check all entries in wp_pll_translations for posts 101 and 1431
$stmt = $pdo->query('
    SELECT tt.translation_id, tt.language, tt.source_language, tt.element_id, p.post_title
    FROM wp_pll_translations tt
    JOIN wp_posts p ON tt.element_id = p.ID
    WHERE tt.translation_id =
        (SELECT translation_id FROM wp_pll_translations WHERE element_id = 101 LIMIT 1)
    ORDER BY tt.language
');
echo "Full translation group for post 101:\n";
while ($row = $stmt->fetch()) {
    echo "  trans_id=" . $row['translation_id'] . ", lang=" . $row['language'] . ", source=" . $row['source_language'] . ", elem=" . $row['element_id'] . ", title=" . $row['post_title'] . "\n";
}

// Check if maybe the issue is that we need more columns in wp_pll_translations
// Let me check the standard Polylang table structure
echo "\nCurrent table structure:\n";
$stmt2 = $pdo->query("DESCRIBE wp_pll_translations");
while ($row = $stmt2->fetch()) {
    echo "  " . $row['Field'] . ": " . $row['Type'] . "\n";
}