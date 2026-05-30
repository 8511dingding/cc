<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Create translation group for homepage
// EN entry
$pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'en', NULL, ?)")->execute([331, 331]);
echo "Added EN translation for homepage\n";

// ZH entry - points to same post (homepage has no Chinese version)
$pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'zh', 'en', ?)")->execute([331, 331]);
echo "Added ZH translation for homepage (self-referencing)\n";

// Verify
$stmt = $pdo->query("SELECT * FROM wp_pll_translations WHERE element_id = 331");
echo "\npll_translations for homepage:\n";
while ($row = $stmt->fetch()) {
    echo "  id=" . $row['id'] . ", trans_id=" . $row['translation_id'] . ", lang=" . $row['language'] . ", elem=" . $row['element_id'] . "\n";
}

// Now check the homepage URL again
echo "\nTesting language switcher on homepage...\n";