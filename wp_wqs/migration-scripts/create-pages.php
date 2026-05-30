<?php
/**
 * Create WordPress Pages from old Joomla content
 * Creates: Biography, Contact pages
 */

$old_db = [
    'host' => '127.0.0.1',
    'port' => 3307,
    'user' => 'root',
    'password' => 'GM3750-jm',
    'name' => 'wqs_joomla',
    'prefix' => 'jos_'
];

$new_db = [
    'host' => '127.0.0.1',
    'port' => 3307,
    'user' => 'root',
    'password' => 'GM3750-jm',
    'name' => 'wqs_wordpress',
    'prefix' => 'wp_'
];

function connect_db($config) {
    $dsn = "mysql:host={$config['host']};port={$config['port']};dbname={$config['name']};charset=utf8mb4";
    $pdo = new PDO($dsn, $config['user'], $config['password'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
    return $pdo;
}

function clean_content($content) {
    $content = str_replace(
        'http://www.wangqingsong.com/images/stories/',
        '/images/stories/',
        $content
    );
    $content = preg_replace('/\s*mce_[\w=":\-]+/', '', $content);
    return $content;
}

function create_page($pdo, $title, $content, $slug) {
    global $new_db;
    $stmt = $pdo->prepare("SELECT ID FROM {$new_db['prefix']}posts WHERE post_name = ? AND post_type = 'page'");
    $stmt->execute([$slug]);
    $existing = $stmt->fetch();

    if ($existing) {
        echo "  Page '{$title}' already exists, skipping...\n";
        return $existing['ID'];
    }

    $now = date('Y-m-d H:i:s');

    $pdo->prepare("
        INSERT INTO {$new_db['prefix']}posts
        (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt,
         post_status, comment_status, ping_status, post_name, post_modified, post_modified_gmt,
         post_type, to_ping, pinged, post_content_filtered)
        VALUES (1, ?, ?, ?, ?, '', 'publish', 'closed', 'closed', ?, ?, ?, 'page', '', '', '')
    ")->execute([$now, $now, $content, $title, $slug, $now, $now]);

    $page_id = $pdo->lastInsertId();
    echo "  Created page: {$title} (ID: {$page_id})\n";
    return $page_id;
}

echo "=== Creating WordPress Pages ===\n\n";

$old_pdo = connect_db($old_db);
$new_pdo = connect_db($new_db);

// Biography - using direct query to avoid reserved word issues
echo "Processing Biography...\n";
$biography_sql = "SELECT title, introtext FROM {$old_db['prefix']}content WHERE id = 6";
$stmt = $old_pdo->query($biography_sql);
$biography = $stmt->fetch();
$biography_content = clean_content($biography['introtext']);
create_page($new_pdo, 'Biography', $biography_content, 'biography');

// Contact
echo "Processing Contact...\n";
$contact_sql = "SELECT title, introtext FROM {$old_db['prefix']}content WHERE id = 7";
$stmt = $old_pdo->query($contact_sql);
$contact = $stmt->fetch();
$contact_content = clean_content($contact['introtext']);
create_page($new_pdo, 'Contact', $contact_content, 'contact');

// Homepage
echo "Creating Homepage...\n";
$homepage_content = '<h2>Welcome to Wang Qingsong Art</h2>
<p>Chinese contemporary artist. Photography, video, and staged tableaux.</p>
<p>Explore his works spanning from 1997 to present.</p>';
create_page($new_pdo, 'Home', $homepage_content, 'home');

// Set homepage
$homepage_id = $new_pdo->query("SELECT ID FROM {$new_db['prefix']}posts WHERE post_name = 'home' AND post_type = 'page'")->fetchColumn();
if ($homepage_id) {
    $new_pdo->prepare("UPDATE {$new_db['prefix']}options SET option_value = ? WHERE option_name = 'page_on_front'")->execute([$homepage_id]);
    $new_pdo->prepare("UPDATE {$new_db['prefix']}options SET option_value = 'page' WHERE option_name = 'show_on_front'")->execute([]);
    echo "\n  Set homepage: ID {$homepage_id}\n";
}

echo "\n=== Pages Created Successfully ===\n";
echo "Check http://localhost:8081\n";