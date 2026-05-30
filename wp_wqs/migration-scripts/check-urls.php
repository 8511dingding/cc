<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Get the actual URL for post 101 and 1431 from the database
$stmt = $pdo->prepare("SELECT ID, post_name, post_date FROM wp_posts WHERE ID IN (101, 1431)");
$stmt->execute();
$posts = $stmt->fetchAll(PDO::FETCH_ASSOC);

foreach ($posts as $p) {
    $url = "/" . date("Y/m/d", strtotime($p["post_date"])) . "/" . $p["post_name"] . "/";
    echo "Post " . $p["ID"] . ": $url\n";
}