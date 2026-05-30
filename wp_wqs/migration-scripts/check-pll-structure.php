<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check what a properly working Polylang setup would look like
$stmt = $pdo->query("DESCRIBE wp_pll_translations");
echo "Current wp_pll_translations structure:\n";
while ($row = $stmt->fetch()) {
    echo "  {$row['Field']}: {$row['Type']} Null={$row['Null']} Key={$row['Key']} Default={$row['Default']}\n";
}

// Check wp_pll_posts structure
$stmt2 = $pdo->query("DESCRIBE wp_pll_posts");
echo "\nwp_pll_posts structure:\n";
while ($row = $stmt2->fetch()) {
    echo "  {$row['Field']}: {$row['Type']} Null={$row['Null']} Key={$row['Key']} Default={$row['Default']}\n";
}

// Show content of wp_pll_posts for a few posts
$stmt3 = $pdo->query("SELECT * FROM wp_pll_posts WHERE post_id IN (101, 1431, 331) ORDER BY post_id");
echo "\nwp_pll_posts content for posts 101, 1431, 331:\n";
while ($row = $stmt3->fetch()) {
    print_r($row);
}

// Show content of wp_pll_translations for post 101
$stmt4 = $pdo->query("SELECT * FROM wp_pll_translations WHERE translation_id = 101");
echo "\nwp_pll_translations for translation_id=101:\n";
while ($row = $stmt4->fetch()) {
    print_r($row);
}