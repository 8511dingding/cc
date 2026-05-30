<?php
/**
 * Import Chinese articles from JoomFish translations
 * Creates Chinese versions linked to existing English posts
 */

$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$old_pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_joomla;charset=utf8mb4', 'root', 'GM3750-jm', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

echo "=== Importing Chinese Articles ===\n\n";

// Get all Chinese translations for content
$stmt = $old_pdo->query("
    SELECT
        jfc.reference_id,
        c.title as en_title,
        MAX(CASE WHEN jfc.reference_field = 'title' THEN jfc.value END) as zh_title,
        MAX(CASE WHEN jfc.reference_field = 'introtext' THEN jfc.value END) as zh_introtext,
        MAX(CASE WHEN jfc.reference_field = 'fulltext' THEN jfc.value END) as zh_fulltext,
        cat.id as catid
    FROM jos_jf_content jfc
    JOIN jos_content c ON jfc.reference_id = c.id
    LEFT JOIN jos_categories cat ON c.catid = cat.id
    WHERE jfc.reference_table = 'content' AND jfc.language_id = 2
    GROUP BY jfc.reference_id, c.title, cat.id
    HAVING zh_title IS NOT NULL AND zh_title != ''
");
$translations = $stmt->fetchAll();

echo "Found " . count($translations) . " Chinese translations in JoomFish\n\n";

// Build English title to post ID mapping
$stmt = $pdo->query("SELECT ID, post_title FROM wp_posts WHERE post_type = 'post'");
$posts = $stmt->fetchAll();
$en_title_to_id = [];
foreach ($posts as $p) {
    $en_title_to_id[trim($p['post_title'])] = $p['ID'];
}

// Category mapping (reuse from migration)
$category_map = [
    8 => '1997-1999 Photography', 9 => '2000 Photography', 10 => '2001 Photography',
    11 => '2002 Photography', 12 => '2003 Photography', 13 => '2004 Photography',
    14 => '2005 Photography', 15 => '2007 Photography', 16 => '2008 Photography',
    17 => '2009 Photography', 18 => '2010 Photography', 19 => '2011 Photography',
    20 => '2012 Photography', 21 => '2013 Photography', 22 => '2020 Photography',
    23 => '2015 Photography', 24 => '2016 Photography', 25 => '14-18 Photography',
    26 => '2018 Photography', 27 => '2019 Photography', 28 => 'X Photography',
    30 => '96-03 Exhibitions', 31 => '1996 Exhibitions', 32 => '2000 Exhibitions',
    33 => '2001 Exhibitions', 34 => '2002 Exhibitions', 35 => '2003 Exhibitions',
    36 => '2004 Exhibitions', 37 => '2005 Exhibitions', 38 => '2006 Exhibitions',
    39 => '2007 Exhibitions', 40 => '2008 Exhibitions', 41 => '2009 Exhibitions',
    42 => '2010 Exhibitions', 43 => '2011 Exhibitions', 44 => '2012 Exhibitions',
    45 => '2013 Exhibitions', 46 => '2014 Exhibitions', 47 => '2015 Exhibitions',
    48 => '2016 Exhibitions', 49 => '2017 Exhibitions', 50 => '2018-2019 Exhibitions',
    51 => '2020 Exhibitions', 52 => 'X Exhibitions',
    53 => 'Shooting', 54 => '1997-1999 Shooting', 55 => '2000 Shooting',
    56 => '2001 Shooting', 57 => '2002 Shooting', 58 => '2003 Shooting',
    59 => '2004 Shooting', 60 => '2005 Shooting', 61 => '2006 Shooting',
    62 => '2007 Shooting', 63 => '2008 Shooting', 64 => '2009 Shooting',
    65 => '2010 Shooting', 66 => '2011 Shooting', 67 => '2012 Shooting',
    68 => '2013 Shooting', 69 => '2014 Shooting', 70 => '2015 Shooting',
    71 => '98-01 Reviews', 72 => '2002 Reviews', 73 => '2003 Reviews',
    74 => '2004 Reviews', 75 => '2005 Reviews', 76 => '2006 Reviews',
    77 => '2007 Reviews', 78 => '2008 Reviews', 79 => '2009 Reviews',
    80 => '2010 Reviews', 81 => '2011 Reviews', 82 => '2012 Reviews',
    83 => '2013 Reviews', 84 => '2014 Reviews', 85 => '2015 Reviews',
    86 => '2016 Reviews', 87 => '2017 Reviews', 88 => '2018 Reviews',
    89 => '2019 Reviews', 90 => '2020 Reviews', 91 => '2021 Reviews',
    92 => '2022 Reviews',
];

$imported = 0;
$skipped = 0;
$errors = [];

foreach ($translations as $t) {
    // Find English post
    $en_post_id = null;

    // Try exact match
    if (isset($en_title_to_id[$t['en_title']])) {
        $en_post_id = $en_title_to_id[$t['en_title']];
    } else {
        // Try match without trailing spaces
        $en_title_trimmed = trim($t['en_title']);
        foreach ($en_title_to_id as $en_title => $id) {
            if (trim($en_title) == $en_title_trimmed) {
                $en_post_id = $id;
                break;
            }
        }
    }

    if (!$en_post_id) {
        $skipped++;
        if ($skipped <= 5) {
            echo "Skipped (no EN post): {$t['en_title']}\n";
        }
        continue;
    }

    // Get the English post's category and other metadata
    $stmt = $pdo->prepare("
        SELECT tr.term_taxonomy_id, tt.term_id, t.name
        FROM wp_term_relationships tr
        JOIN wp_term_taxonomy tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
        JOIN wp_terms t ON tt.term_id = t.term_id
        WHERE tr.object_id = ? AND tt.taxonomy = 'category'
        LIMIT 1
    ");
    $stmt->execute([$en_post_id]);
    $category = $stmt->fetch();

    if (!$category) {
        $skipped++;
        continue;
    }

    $zh_title = trim(strip_tags($t['zh_title']));
    $zh_content = $t['zh_introtext'] . $t['zh_fulltext'];

    if (empty($zh_content) || strlen($zh_content) < 50) {
        // Skip if no meaningful content
        $skipped++;
        continue;
    }

    // Clean content - fix image paths
    $zh_content = str_replace(
        'http://www.wangqingsong.com/images/stories/',
        '/images/stories/',
        $zh_content
    );
    $zh_content = str_replace(
        'http://localhost/wangqingsong.com/images/stories/',
        '/images/stories/',
        $zh_content
    );

    // Remove mce_ attributes
    $zh_content = preg_replace('/\s*mce_(href|src|background)="[^"]*"/', '', $zh_content);
    $zh_content = preg_replace('/\s*class="mce[^"]*"/', '', $zh_content);
    $zh_content = preg_replace('/\s*rel="[^"]*"/', '', $zh_content);

    // Create Chinese post
    $now = date('Y-m-d H:i:s');
    $slug = sanitize_title($zh_title) . '-zh';

    // Check if Chinese version already exists
    $stmt = $pdo->prepare("SELECT ID FROM wp_posts WHERE post_type = 'post' AND post_name = ?");
    $stmt->execute([$slug]);
    if ($stmt->fetch()) {
        $skipped++;
        continue; // Already exists
    }

    try {
        $pdo->prepare("
            INSERT INTO wp_posts
            (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status,
             comment_status, ping_status, post_name, post_modified, post_modified_gmt,
             post_type, to_ping, pinged, post_content_filtered)
            VALUES (1, ?, ?, ?, ?, '', 'publish',
             'closed', 'closed', ?, ?, ?, 'post', '', '', '')
        ")->execute([$now, $now, $zh_content, $zh_title, $slug, $now, $now]);

        $zh_post_id = $pdo->lastInsertId();

        // Assign same category
        $pdo->prepare("
            INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order)
            VALUES (?, ?, 0)
        ")->execute([$zh_post_id, $category['term_taxonomy_id']]);

        // Link to English post via post meta
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'en_post_id', ?)")
            ->execute([$zh_post_id, $en_post_id]);
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'zh_post_id', ?)")
            ->execute([$en_post_id, $zh_post_id]);

        // Also set language info via Polylang-like meta (if Polylang tables exist later)
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'zh')")
            ->execute([$zh_post_id]);
        $pdo->prepare("INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (?, 'language', 'en')")
            ->execute([$en_post_id]);

        $imported++;

        if ($imported <= 10) {
            echo "Created ZH post $zh_post_id (linked to EN $en_post_id): $zh_title\n";
        }
    } catch (Exception $e) {
        $errors[] = "Error creating {$zh_title}: " . $e->getMessage();
    }
}

echo "\n=== Import Complete ===\n";
echo "Imported: $imported Chinese posts\n";
echo "Skipped: $skipped\n";
if (count($errors) > 0) {
    echo "Errors: " . count($errors) . "\n";
    foreach ($errors as $e) {
        echo "  $e\n";
    }
}

function sanitize_title($title) {
    $title = preg_replace('/[^a-z0-9\x{4e00}-\x{9fa5}]/u', '-', strtolower($title));
    $title = preg_replace('/-+/', '-', $title);
    $title = trim($title, '-');
    return $title;
}