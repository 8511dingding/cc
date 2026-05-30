<?php
/**
 * Migration Script: Joomla to WordPress
 * Migrates content from old wqs_joomla database to WordPress
 *
 * Usage: php migrate-to-wordpress.php
 */

// Database configuration - OLD Joomla site
$old_db = [
    'host' => '127.0.0.1',
    'port' => 3307,
    'user' => 'root',
    'password' => 'GM3750-jm',
    'name' => 'wqs_joomla',
    'prefix' => 'jos_'
];

// Database configuration - NEW WordPress site
$new_db = [
    'host' => '127.0.0.1',
    'port' => 3307,
    'user' => 'root',
    'password' => 'GM3750-jm',
    'name' => 'wqs_wordpress',
    'prefix' => 'wp_'
];

// Category mapping: old catid => new category name
$category_map = [
    8 => '1997-1999 Photography',
    9 => '2000 Photography',
    10 => '2001 Photography',
    11 => '2002 Photography',
    12 => '2003 Photography',
    13 => '2004 Photography',
    14 => '2005 Photography',
    15 => '2007 Photography',
    16 => '2008 Photography',
    17 => '2009 Photography',
    18 => '2010 Photography',
    19 => '2011 Photography',
    20 => '2012 Photography',
    21 => '2013 Photography',
    22 => '2020 Photography',
    23 => '2015 Photography',
    24 => '2016 Photography',
    25 => '14-18 Photography',
    26 => '2018 Photography',
    27 => '2019 Photography',
    28 => 'X Photography',
    30 => '96-03 Exhibitions',
    31 => '1996 Exhibitions',
    32 => '2000 Exhibitions',
    33 => '2001 Exhibitions',
    34 => '2002 Exhibitions',
    35 => '2003 Exhibitions',
    36 => '2004 Exhibitions',
    37 => '2005 Exhibitions',
    38 => '2006 Exhibitions',
    39 => '2007 Exhibitions',
    40 => '2008 Exhibitions',
    41 => '2009 Exhibitions',
    42 => '2010 Exhibitions',
    43 => '2011 Exhibitions',
    44 => '2012 Exhibitions',
    45 => '2013 Exhibitions',
    46 => '2014 Exhibitions',
    47 => '2015 Exhibitions',
    48 => '2016 Exhibitions',
    49 => '2017 Exhibitions',
    50 => '2018-2019 Exhibitions',
    51 => '2020 Exhibitions',
    52 => 'X Exhibitions',
    53 => 'Shooting',
    54 => '1997-1999 Shooting',
    55 => '2000 Shooting',
    56 => '2001 Shooting',
    57 => '2002 Shooting',
    58 => '2003 Shooting',
    59 => '2004 Shooting',
    60 => '2005 Shooting',
    61 => '2006 Shooting',
    62 => '2007 Shooting',
    63 => '2008 Shooting',
    64 => '2009 Shooting',
    65 => '2010 Shooting',
    66 => '2011 Shooting',
    67 => '2012 Shooting',
    68 => '2013 Shooting',
    69 => '2014 Shooting',
    70 => '2015 Shooting',
    71 => '98-01 Reviews',
    72 => '2002 Reviews',
    73 => '2003 Reviews',
    74 => '2004 Reviews',
    75 => '2005 Reviews',
    76 => '2006 Reviews',
    77 => '2007 Reviews',
    78 => '2008 Reviews',
    79 => '2009 Reviews',
    80 => '2010 Reviews',
    81 => '2011 Reviews',
    82 => '2012 Reviews',
    83 => '2013 Reviews',
    84 => '2014 Reviews',
    85 => '2015 Reviews',
    86 => '2016 Reviews',
    87 => '2017 Reviews',
    88 => '2018 Reviews',
    89 => '2019 Reviews',
    90 => '2020 Reviews',
    91 => '2021 Reviews',
    92 => '2022 Reviews',
];

// Section mapping: old sectionid => category type
$section_map = [
    1 => 'Photography',      // Photography section
    2 => 'Video',            // Video section
    3 => 'Others',           // Others section
    4 => 'Exhibitions',      // Exhibitions section
    5 => 'Reviews',          // Reviews section
    6 => 'Biography',        // Biography section
    7 => 'Contact',          // Contact section
    9 => 'Shooting',         // Shooting section
];

/**
 * Connect to database
 */
function connect_db($config) {
    $dsn = "mysql:host={$config['host']};port={$config['port']};dbname={$config['name']};charset=utf8mb4";
    try {
        $pdo = new PDO($dsn, $config['user'], $config['password'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
        ]);
        return $pdo;
    } catch (PDOException $e) {
        die("Database connection failed: " . $e->getMessage() . "\n");
    }
}

/**
 * Insert term (category) into WordPress
 */
function insert_term($pdo, $name, $taxonomy = 'category', $parent = 0) {
    $slug = sanitize_title($name);

    // Check if exists
    $stmt = $pdo->prepare("SELECT term_id FROM {$GLOBALS['new_db']['prefix']}terms WHERE slug = ?");
    $stmt->execute([$slug]);
    $term = $stmt->fetch();

    if ($term) {
        return $term['term_id'];
    }

    // Insert term
    $pdo->prepare("INSERT INTO {$GLOBALS['new_db']['prefix']}terms (name, slug) VALUES (?, ?)")
        ->execute([$name, $slug]);
    $term_id = $pdo->lastInsertId();

    // Insert term_taxonomy
    $pdo->prepare("INSERT INTO {$GLOBALS['new_db']['prefix']}term_taxonomy (term_id, taxonomy, description, count) VALUES (?, ?, ?, 0)")
        ->execute([$term_id, $taxonomy, '']);

    $tt_id = $pdo->lastInsertId();

    return $term_id;
}

/**
 * Sanitize title for slug
 */
function sanitize_title($title) {
    $title = preg_replace('/[^a-z0-9\x{4e00}-\x{9fa5}]/u', '-', strtolower($title));
    $title = preg_replace('/-+/', '-', $title);
    $title = trim($title, '-');
    return $title;
}

/**
 * Clean HTML content and fix image paths
 */
function clean_content($content) {
    // Replace old image paths with new local paths
    $content = str_replace(
        'http://www.wangqingsong.com/images/stories/',
        '/images/stories/',
        $content
    );

    // Fix internal links
    $content = preg_replace(
        '#index\.php\?option=com_content&view=article&id=(\d+)#',
        '/?p=$1',
        $content
    );

    // Remove mce_ attributes
    $content = preg_replace('/\s*mce_[\w=":\-]+/', '', $content);

    return $content;
}

/**
 * Main migration
 */
echo "=== Starting Migration ===\n\n";

// Connect to databases
echo "Connecting to databases...\n";
$old_pdo = connect_db($old_db);
$new_pdo = connect_db($new_db);

// Create categories for each section
echo "Creating categories...\n";
$section_categories = [];
foreach ($section_map as $sectionid => $section_name) {
    $term_id = insert_term($new_pdo, $section_name, 'category');
    $section_categories[$sectionid] = $term_id;
    echo "  - Created category: {$section_name}\n";
}

// Create subcategories for years
echo "Creating year-based categories...\n";
$category_term_ids = [];
foreach ($category_map as $catid => $cat_name) {
    // Determine parent section
    $parent_id = 0;
    foreach ($section_map as $sectionid => $section_name) {
        if (stripos($cat_name, $section_name) !== false || $sectionid == 1) {
            $parent_id = $section_categories[$sectionid] ?? 0;
            break;
        }
    }
    $term_id = insert_term($new_pdo, $cat_name, 'category', $parent_id);
    $category_term_ids[$catid] = $term_id;
    if (strlen($cat_name) < 30) {
        echo "  - Created subcategory: {$cat_name}\n";
    }
}

// Fetch all content articles from old site
echo "\nFetching content from old site...\n";
$stmt = $old_pdo->query("
    SELECT c.*, cat.title as category_title, cat.section as section_id
    FROM {$old_db['prefix']}content c
    LEFT JOIN {$old_db['prefix']}categories cat ON c.catid = cat.id
    WHERE c.catid NOT IN (1,2,3,4,5,6,7,29)
    AND c.state = 1
    ORDER BY c.catid, c.ordering
");

$all_content = $stmt->fetchAll();
$total = count($all_content);
echo "Found {$total} content items to migrate.\n\n";

// Migrate each content item
echo "Migrating content...\n";
$migrated = 0;
$skipped = 0;

foreach ($all_content as $item) {
    $catid = $item['catid'];

    // Skip if not in category map
    if (!isset($category_term_ids[$catid]) && !in_array($catid, [1,2,3,4,5,6,7,29])) {
        $skipped++;
        continue;
    }

    // Prepare post data
    $title = $item['title'];
    $content = clean_content($item['introtext'] . $item['fulltext']);
    $alias = $item['alias'] ?: sanitize_title($title);
    $created = $item['created'] && $item['created'] != '0000-00-00 00:00:00' ? $item['created'] : date('Y-m-d H:i:s');
    $modified = $item['modified'] && $item['modified'] != '0000-00-00 00:00:00' ? $item['modified'] : $created;

    // Insert post
    $new_pdo->prepare("
        INSERT INTO {$new_db['prefix']}posts
        (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status,
         comment_status, ping_status, post_name, post_modified, post_modified_gmt,
         post_type, to_ping, pinged, post_content_filtered)
        VALUES (1, ?, ?, ?, ?, '', 'publish',
         'closed', 'closed', ?, ?, ?, 'post', '', '', '')
    ")->execute([$created, $created, $content, $title, $alias, $modified, $modified]);

    $post_id = $new_pdo->lastInsertId();

    // Set category
    if (isset($category_term_ids[$catid])) {
        $term_taxonomy_id = $new_pdo->query("
            SELECT tt.term_taxonomy_id FROM {$new_db['prefix']}term_taxonomy tt
            WHERE tt.term_id = {$category_term_ids[$catid]} AND tt.taxonomy = 'category'
        ")->fetchColumn();

        if ($term_taxonomy_id) {
            $new_pdo->prepare("
                INSERT INTO {$new_db['prefix']}term_relationships (object_id, term_taxonomy_id, term_order)
                VALUES (?, ?, 0)
            ")->execute([$post_id, $term_taxonomy_id]);

            // Update count
            $new_pdo->prepare("
                UPDATE {$new_db['prefix']}term_taxonomy
                SET count = (SELECT COUNT(*) FROM {$new_db['prefix']}term_relationships WHERE term_taxonomy_id = ?)
                WHERE term_taxonomy_id = ?
            ")->execute([$term_taxonomy_id, $term_taxonomy_id]);
        }
    }

    $migrated++;
    if ($migrated % 50 == 0) {
        echo "  Migrated {$migrated}/{$total}...\n";
    }
}

echo "\n=== Migration Complete ===\n";
echo "Migrated: {$migrated} items\n";
echo "Skipped: {$skipped} items\n";
echo "\nPlease check WordPress admin at http://localhost:8081/wp-admin\n";