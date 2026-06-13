<?php
/**
 * Script to copy Chinese content to English posts' custom fields
 *
 * Run via: php copy_chinese_to_english.php
 */

// Database connection
$db_host = '127.0.0.1:3307';
$db_user = 'root';
$db_pass = 'GM3750-jm';
$db_name = 'wqs_wordpress';

$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$conn->set_charset('utf8mb4');

// 1. Create "Original Chinese" category if not exists
$result = $conn->query("SELECT term_id FROM wp_terms WHERE slug = 'original-chinese' LIMIT 1");
$row = $result->fetch_assoc();

if (!$row) {
    $conn->query("INSERT INTO wp_terms (name, slug) VALUES ('Original Chinese', 'original-chinese')");
    $category_id = $conn->insert_id;
    $conn->query("INSERT INTO wp_term_taxonomy (term_id, taxonomy, description, parent, count) VALUES ($category_id, 'category', 'Original Chinese content preserved from migration', 0, 0)");
    echo "Created category: Original Chinese (ID: $category_id)\n";
} else {
    $category_id = $row['term_id'];
    echo "Category 'Original Chinese' already exists (ID: $category_id)\n";
}

// 2. Get all English-Chinese post pairs
$sql = "SELECT t1.element_id AS english_id, t2.element_id AS chinese_id
        FROM wp_pll_translations t1
        JOIN wp_pll_translations t2 ON t1.translation_id = t2.translation_id AND t1.language != t2.language
        JOIN wp_posts p_en ON p_en.ID = t1.element_id AND p_en.post_type = 'post' AND p_en.post_status = 'publish'
        JOIN wp_posts p_cn ON p_cn.ID = t2.element_id AND p_cn.post_type = 'post' AND p_cn.post_status = 'publish'
        WHERE t1.language = 'en' AND t2.language = 'zh'
        ORDER BY t1.element_id";

$pairs_result = $conn->query($sql);
$processed = 0;
$errors = 0;

echo "\nProcessing " . $pairs_result->num_rows . " translation pairs...\n";

while ($pair = $pairs_result->fetch_assoc()) {
    $english_id = (int)$pair['english_id'];
    $chinese_id = (int)$pair['chinese_id'];

    // Get Chinese post content and title
    $chinese_post = $conn->query("SELECT post_content, post_title FROM wp_posts WHERE ID = $chinese_id")->fetch_assoc();

    if (!$chinese_post) {
        echo "ERROR: Chinese post $chinese_id not found\n";
        $errors++;
        continue;
    }

    $chinese_content = $conn->real_escape_string($chinese_post['post_content']);
    $chinese_title = $conn->real_escape_string($chinese_post['post_title']);

    // Delete existing custom fields for this English post (to avoid duplicates)
    $conn->query("DELETE FROM wp_postmeta WHERE post_id = $english_id AND meta_key IN ('chinese_content', 'chinese_title', 'chinese_post_id')");

    // Add Chinese content as custom field
    $conn->query("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES ($english_id, 'chinese_content', '$chinese_content')");
    $conn->query("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES ($english_id, 'chinese_title', '$chinese_title')");
    $conn->query("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES ($english_id, 'chinese_post_id', $chinese_id)");

    // Add Chinese post to Original Chinese category
    // Check if already in category
    $check = $conn->query("SELECT 1 FROM wp_term_relationships WHERE object_id = $chinese_id AND term_taxonomy_id = (SELECT term_taxonomy_id FROM wp_term_taxonomy WHERE term_id = $category_id)");
    if (!$check->fetch_assoc()) {
        $conn->query("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id) VALUES ($chinese_id, (SELECT term_taxonomy_id FROM wp_term_taxonomy WHERE term_id = $category_id))");
        // Update count
        $conn->query("UPDATE wp_term_taxonomy SET count = count + 1 WHERE term_id = $category_id");
    }

    $processed++;

    if ($processed % 50 == 0) {
        echo "Processed $processed pairs...\n";
    }
}

echo "\nDone! Processed $processed pairs, $errors errors.\n";

// Show sample
echo "\nSample - Post 101:\n";
$sample = $conn->query("SELECT meta_key, meta_value FROM wp_postmeta WHERE post_id = 101 AND meta_key LIKE 'chinese%'");
while ($row = $sample->fetch_assoc()) {
    echo "  {$row['meta_key']}: " . substr($row['meta_value'], 0, 100) . "...\n";
}

$conn->close();