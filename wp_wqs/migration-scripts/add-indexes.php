<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Add indexes that might be missing
try {
    $pdo->exec("ALTER TABLE wp_pll_posts ADD INDEX idx_language (language)");
    echo "Added index on wp_pll_posts.language\n";
} catch (Exception $e) {
    echo "Index wp_pll_posts.language: " . $e->getMessage() . "\n";
}

try {
    $pdo->exec("ALTER TABLE wp_pll_translations ADD INDEX idx_language (language)");
    echo "Added index on wp_pll_translations.language\n";
} catch (Exception $e) {
    echo "Index wp_pll_translations.language: " . $e->getMessage() . "\n";
}

try {
    $pdo->exec("ALTER TABLE wp_pll_translations ADD INDEX idx_source_language (source_language)");
    echo "Added index on wp_pll_translations.source_language\n";
} catch (Exception $e) {
    echo "Index wp_pll_translations.source_language: " . $e->getMessage() . "\n";
}

// Verify all indexes
echo "\nAll indexes on wp_pll_translations:\n";
$stmt = $pdo->query("SHOW INDEX FROM wp_pll_translations");
while ($row = $stmt->fetch()) {
    echo "  " . $row['Key_name'] . ": " . $row['Column_name'] . "\n";
}

echo "\nAll indexes on wp_pll_posts:\n";
$stmt2 = $pdo->query("SHOW INDEX FROM wp_pll_posts");
while ($row = $stmt2->fetch()) {
    echo "  " . $row['Key_name'] . ": " . $row['Column_name'] . "\n";
}