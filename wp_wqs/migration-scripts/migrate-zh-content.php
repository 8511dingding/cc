<?php
/**
 * Migrate ZH content from JoomFish to WordPress for posts that don't have ZH versions yet
 * Fixed query to properly get title translations
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);
$pdo_old = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_joomla;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "=== Migrating ZH Posts from JoomFish (Fixed) ===\n\n";

// Step 1: Get JoomFish translations - only title field with language_id=2
$stmt = $pdo_old->query("
    SELECT reference_id, value as zh_title
    FROM jos_jf_content
    WHERE reference_table = 'content' AND reference_field = 'title' AND language_id = 2
");
$jf_titles = [];
while ($row = $stmt->fetch()) {
    $jf_titles[$row['reference_id']] = trim($row['zh_title']);
}
echo "JoomFish title translations: " . count($jf_titles) . "\n";

// Step 2: Get EN titles from jos_content
$stmt2 = $pdo_old->query("SELECT id, title, introtext FROM jos_content WHERE state = 1 AND access = 0");
$joomfish_pairs = [];
while ($row = $stmt2->fetch()) {
    $joomla_id = $row['id'];
    $en_title = trim($row['title']);
    $zh_title = $jf_titles[$joomla_id] ?? '';

    // Skip if no ZH title or if EN and ZH titles are the same
    if (empty($zh_title) || $en_title === $zh_title) {
        continue;
    }

    // Get ZH introtext from JoomFish
    $stmt_zh = $pdo_old->prepare("
        SELECT value FROM jos_jf_content
        WHERE reference_id = ? AND reference_table = 'content' AND reference_field = 'introtext' AND language_id = 2
    ");
    $stmt_zh->execute([$joomla_id]);
    $zh_row = $stmt_zh->fetch();
    $zh_introtext = $zh_row ? $zh_row['value'] : '';

    $joomfish_pairs[$joomla_id] = [
        'en_title' => $en_title,
        'zh_title' => $zh_title,
        'zh_introtext' => $zh_introtext,
    ];
}
echo "JoomFish pairs with different EN/ZH titles: " . count($joomfish_pairs) . "\n";

// Step 3: Get existing EN posts in WordPress indexed by title
$stmt_wp = $pdo->query("SELECT ID, post_title, post_name, post_date FROM wp_posts WHERE post_type = 'post' AND post_status = 'publish'");
$wp_en_posts = [];
while ($row = $stmt_wp->fetch()) {
    $wp_en_posts[trim($row['post_title'])] = [
        'ID' => $row['ID'],
        'post_name' => $row['post_name'],
        'post_date' => $row['post_date']
    ];
}
echo "EN posts in WordPress: " . count($wp_en_posts) . "\n";

// Step 4: Get existing ZH posts in WordPress
$stmt_zh = $pdo->query("
    SELECT p.ID, p.post_title
    FROM wp_posts p
    JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'language' AND m.meta_value = 'zh'
    WHERE p.post_type = 'post' AND p.post_status = 'publish'
");
$existing_zh_titles = [];
while ($row = $stmt_zh->fetch()) {
    $existing_zh_titles[trim($row['post_title'])] = $row['ID'];
}
echo "Existing ZH posts in WordPress: " . count($existing_zh_titles) . "\n";

// Step 5: Identify which pairs need to be created
$pairs_to_create = [];
foreach ($joomfish_pairs as $joomla_id => $data) {
    $en_title = $data['en_title'];
    $zh_title = $data['zh_title'];

    // Check if EN post exists in WordPress
    if (!isset($wp_en_posts[$en_title])) {
        continue;
    }

    // Check if ZH post already exists
    if (isset($existing_zh_titles[$zh_title])) {
        continue;
    }

    $pairs_to_create[$en_title] = [
        'en_id' => $wp_en_posts[$en_title]['ID'],
        'en_post_name' => $wp_en_posts[$en_title]['post_name'],
        'en_post_date' => $wp_en_posts[$en_title]['post_date'],
        'zh_title' => $zh_title,
        'zh_content' => $data['zh_introtext'],
        'joomla_id' => $joomla_id
    ];
}

echo "Pairs to create: " . count($pairs_to_create) . "\n\n";

// Step 6: Create the ZH posts
$lang_en = 277;
$lang_zh = 280;
$created = 0;
$skipped = 0;

foreach ($pairs_to_create as $en_title => $data) {
    $en_id = $data['en_id'];

    // Skip pages (Biography, Contact, etc.)
    if (stripos($en_title, 'biography') !== false ||
        stripos($en_title, 'contact') !== false ||
        stripos($en_title, 'others') !== false) {
        $skipped++;
        continue;
    }

    try {
        // Create ZH post with same slug and date as EN post
        $stmt_insert = $pdo->prepare("
            INSERT INTO wp_posts (
                post_author, post_date, post_date_gmt, post_modified, post_modified_gmt,
                post_title, post_name, post_content, post_excerpt, post_status, post_type,
                comment_status, ping_status, to_ping, pinged, post_content_filtered,
                post_parent, menu_order, guid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'publish', 'post', 'closed', 'closed', '', '', '', 0, 0, '')
        ");
        $stmt_insert->execute([
            1,
            $data['en_post_date'],
            $data['en_post_date'],
            $data['en_post_date'],
            $data['en_post_date'],
            $data['zh_title'],
            $data['en_post_name'],
            $data['zh_content'],
            '',
        ]);

        $zh_id = $pdo->lastInsertId();
        $created++;

        if ($created <= 10) {
            echo "Created: $en_title -> {$data['zh_title']} (ID: $zh_id)\n";
        }

        // Link the posts
        $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'en', '', ?)")->execute([$en_id, $en_id]);
        $pdo->prepare("INSERT INTO wp_pll_translations (translation_id, language, source_language, element_id) VALUES (?, 'zh', 'en', ?)")->execute([$en_id, $zh_id]);

        // Set language meta
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'en')")->execute([$en_id]);
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'zh')")->execute([$zh_id]);

        // Set cross-reference meta
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'zh_post_id', ?)")->execute([$en_id, $zh_id]);
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'en_post_id', ?)")->execute([$zh_id, $en_id]);

        // Set language term relationships
        $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")->execute([$en_id, $lang_en]);
        $pdo->prepare("INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (?, ?, 0)")->execute([$zh_id, $lang_zh]);

        // Set wp_pll_posts
        $pdo->prepare("INSERT INTO wp_pll_posts (post_id, language) VALUES (?, 'en')")->execute([$en_id]);
        $pdo->prepare("INSERT INTO wp_pll_posts (post_id, language) VALUES (?, 'zh')")->execute([$zh_id]);

    } catch (Exception $e) {
        echo "Error creating $en_title: " . $e->getMessage() . "\n";
    }
}

echo "\n=== Summary ===\n";
echo "Created: $created ZH posts\n";
echo "Skipped (pages): $skipped\n";

// Show what was created
if ($created > 0) {
    echo "\nCreated posts:\n";
    $stmt_list = $pdo->query("
        SELECT p.ID, p.post_title, p.post_name, m.meta_value as lang
        FROM wp_posts p
        JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = 'language'
        WHERE m.meta_value = 'zh' AND p.ID > 1630
        ORDER BY p.ID DESC
        LIMIT 20
    ");
    while ($row = $stmt_list->fetch()) {
        echo "  ID:{$row['ID']} {$row['post_title']} ({$row['post_name']})\n";
    }
}

// Clear caches
$pdo->query("DELETE FROM wp_options WHERE option_name LIKE '%_transient_pll%'");
$pdo->query("DELETE FROM wp_options WHERE option_name = 'rewrite_rules'");
echo "\nCleared caches\n";