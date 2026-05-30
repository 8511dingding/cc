<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Get post 161 content
$stmt = $pdo->prepare("SELECT post_content, post_title FROM wp_posts WHERE ID = 161");
$stmt->execute();
$post = $stmt->fetch(PDO::FETCH_ASSOC);

echo "Post 161 title: " . $post['post_title'] . "\n";
echo "Post 161 content length: " . strlen($post['post_content']) . "\n";

// Update page 331 with post 161 content
$stmt2 = $pdo->prepare("UPDATE wp_posts SET post_content = :content WHERE ID = 331");
$stmt2->bindValue(':content', $post['post_content'], PDO::PARAM_STR);
$stmt2->execute();

echo "Updated page 331 with post 161 content\n";

// Verify
$stmt3 = $pdo->prepare("SELECT post_content FROM wp_posts WHERE ID = 331");
$stmt3->execute();
$content = $stmt3->fetchColumn();
echo "Page 331 content length: " . strlen($content) . "\n";