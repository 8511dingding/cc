<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Check homepage post
$stmt = $pdo->prepare("SELECT ID, post_title, post_name FROM wp_posts WHERE ID = ?");
$stmt->execute([331]);
$home = $stmt->fetch();
echo "Homepage post:\n";
print_r($home);

// Check pll_translations for homepage
$stmt2 = $pdo->prepare("SELECT * FROM wp_pll_translations WHERE element_id = ?");
$stmt2->execute([331]);
echo "\npll_translations for homepage:\n";
while ($row = $stmt2->fetch()) {
    print_r($row);
}

// Check pll_posts for homepage
$stmt3 = $pdo->prepare("SELECT * FROM wp_pll_posts WHERE post_id = ?");
$stmt3->execute([331]);
echo "\npll_posts for homepage:\n";
while ($row = $stmt3->fetch()) {
    print_r($row);
}

// Check postmeta for homepage
$stmt4 = $pdo->prepare("SELECT meta_key, meta_value FROM wp_postmeta WHERE post_id = ?");
$stmt4->execute([331]);
echo "\npostmeta for homepage:\n";
while ($row = $stmt4->fetch()) {
    if (in_array($row['meta_key'], ['language', 'en_post_id', 'zh_post_id'])) {
        echo "  {$row['meta_key']}: {$row['meta_value']}\n";
    }
}

// Check term_relationships for homepage
$stmt5 = $pdo->prepare("SELECT term_taxonomy_id FROM wp_term_relationships WHERE object_id = ?");
$stmt5->execute([331]);
echo "\nterm_relationships for homepage:\n";
while ($row = $stmt5->fetch()) {
    echo "  term_taxonomy_id: " . $row['term_taxonomy_id'] . "\n";
}