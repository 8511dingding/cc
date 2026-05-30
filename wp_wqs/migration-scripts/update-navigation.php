<?php
/**
 * Update WordPress Navigation for FSE themes
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

// Get page IDs
$stmt = $pdo->query("SELECT ID, post_title, post_name FROM wp_posts WHERE post_type = 'page' AND post_status = 'publish'");
$pages = $stmt->fetchAll(PDO::FETCH_ASSOC);
$page_by_name = [];
foreach ($pages as $p) { $page_by_name[$p['post_name']] = $p; }

// Get category term IDs
$stmt = $pdo->query("SELECT term_id, name FROM wp_terms WHERE name IN ('Photography', 'Exhibitions', 'Reviews', 'Shooting')");
$categories = $stmt->fetchAll(PDO::FETCH_ASSOC);
$cat_by_name = [];
foreach ($categories as $c) { $cat_by_name[$c['name']] = $c; }

// Build navigation block content
$home_id = $page_by_name['home']['ID'] ?? 0;
$bio_id = $page_by_name['biography']['ID'] ?? 0;
$contact_id = $page_by_name['contact']['ID'] ?? 0;
$photo_term_id = $cat_by_name['Photography']['term_id'] ?? 0;
$exh_term_id = $cat_by_name['Exhibitions']['term_id'] ?? 0;
$rev_term_id = $cat_by_name['Reviews']['term_id'] ?? 0;
$shoot_term_id = $cat_by_name['Shooting']['term_id'] ?? 0;

$nav_content = '<!-- wp:navigation -->
<!-- wp:navigation-link {"label":"Home","type":"custom","url":"/"} /-->
<!-- wp:navigation-link {"label":"Biography","type":"custom","url":"/biography/"} /-->
<!-- wp:navigation-submenu {"label":"Photography","url":"#"} -->
<!-- wp:navigation-link {"label":"1997-1999 Photography","url":"/category/photography/1997-1999-photography/"} /-->
<!-- wp:navigation-link {"label":"2000 Photography","url":"/category/photography/2000-photography/"} /-->
<!-- wp:navigation-link {"label":"2001 Photography","url":"/category/photography/2001-photography/"} /-->
<!-- /wp:navigation-submenu -->
<!-- wp:navigation-link {"label":"Exhibitions","type":"custom","url":"/category/exhibitions/"} /-->
<!-- wp:navigation-link {"label":"Reviews","type":"custom","url":"/category/reviews/"} /-->
<!-- wp:navigation-link {"label":"Shooting","type":"custom","url":"/category/shooting/"} /-->
<!-- wp:navigation-link {"label":"Contact","type":"custom","url":"/contact/"} /-->
<!-- /wp:navigation -->';

// Get existing wp_navigation post
$stmt = $pdo->query("SELECT ID FROM wp_posts WHERE post_type = 'wp_navigation'");
$nav_post = $stmt->fetch();

if ($nav_post) {
    $pdo->prepare("UPDATE wp_posts SET post_content = ?, post_modified = NOW() WHERE ID = ?")
        ->execute([$nav_content, $nav_post['ID']]);
    echo "Updated navigation post ID: {$nav_post['ID']}\n";
} else {
    $pdo->prepare("INSERT INTO wp_posts (post_author, post_date, post_date_gmt, post_content, post_title, post_status, post_type) VALUES (1, NOW(), NOW(), ?, 'Navigation', 'publish', 'wp_navigation')")
        ->execute([$nav_content]);
    $nav_id = $pdo->lastInsertId();
    echo "Created navigation post ID: $nav_id\n";
}

echo "\nDone. Refresh the site.\n";