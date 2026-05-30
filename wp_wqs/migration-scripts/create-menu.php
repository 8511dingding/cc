<?php
/**
 * Create WordPress Navigation Menu
 */

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

echo "=== Creating WordPress Navigation Menu ===\n\n";

$pdo = connect_db($new_db);

// Get or create menu
$menu_name = 'Main Navigation';
$stmt = $pdo->prepare("SELECT term_id FROM {$new_db['prefix']}terms WHERE name = ?");
$stmt->execute([$menu_name]);
$menu = $stmt->fetch();

if (!$menu) {
    $pdo->prepare("INSERT INTO {$new_db['prefix']}terms (name, slug) VALUES (?, ?)")
        ->execute([$menu_name, sanitize_title($menu_name)]);
    $menu_id = $pdo->lastInsertId();

    $pdo->prepare("INSERT INTO {$new_db['prefix']}term_taxonomy (term_id, taxonomy, description, count) VALUES (?, 'nav_menu', '', 0)")
        ->execute([$menu_id]);
    $menu_term_taxonomy_id = $pdo->lastInsertId();
    echo "Created menu: {$menu_name}\n";
} else {
    $menu_id = $menu['term_id'];
    echo "Menu already exists: {$menu_name}\n";
}

// Get menu term_taxonomy_id
$stmt = $pdo->prepare("SELECT term_taxonomy_id FROM {$new_db['prefix']}term_taxonomy WHERE term_id = ? AND taxonomy = 'nav_menu'");
$stmt->execute([$menu_id]);
$menu_ttid = $stmt->fetchColumn();

// Get all pages
$stmt = $pdo->query("SELECT ID, post_title, post_name FROM {$new_db['prefix']}posts WHERE post_type = 'page' AND post_status = 'publish'");
$pages = $stmt->fetchAll();
$page_ids = array_column($pages, 'ID', 'post_name');

// Get Photography category
$stmt = $pdo->prepare("SELECT term_id FROM {$new_db['prefix']}terms WHERE name = 'Photography'");
$stmt->execute();
$photography_term_id = $stmt->fetchColumn();

// Get Exhibitions category
$stmt = $pdo->prepare("SELECT term_id FROM {$new_db['prefix']}terms WHERE name = 'Exhibitions'");
$stmt->execute();
$exhibitions_term_id = $stmt->fetchColumn();

// Get Reviews category
$stmt = $pdo->prepare("SELECT term_id FROM {$new_db['prefix']}terms WHERE name = 'Reviews'");
$stmt->execute();
$reviews_term_id = $stmt->fetchColumn();

// Get Shooting category
$stmt = $pdo->prepare("SELECT term_id FROM {$new_db['prefix']}terms WHERE name = 'Shooting'");
$stmt->execute();
$shooting_term_id = $stmt->fetchColumn();

// Menu items to add
$menu_items = [
    ['title' => 'Home', 'type' => 'page', 'object_id' => $page_ids['home'] ?? 0, 'url' => '/', 'order' => 0],
    ['title' => 'Biography', 'type' => 'page', 'object_id' => $page_ids['biography'] ?? 0, 'url' => '/biography/', 'order' => 1],
    ['title' => 'Photography', 'type' => 'taxonomy', 'object_id' => $photography_term_id, 'url' => '/category/photography/', 'order' => 2],
    ['title' => 'Exhibitions', 'type' => 'taxonomy', 'object_id' => $exhibitions_term_id, 'url' => '/category/exhibitions/', 'order' => 3],
    ['title' => 'Reviews', 'type' => 'taxonomy', 'object_id' => $reviews_term_id, 'url' => '/category/reviews/', 'order' => 4],
    ['title' => 'Shooting', 'type' => 'taxonomy', 'object_id' => $shooting_term_id, 'url' => '/category/shooting/', 'order' => 5],
    ['title' => 'Contact', 'type' => 'page', 'object_id' => $page_ids['contact'] ?? 0, 'url' => '/contact/', 'order' => 6],
];

// Clear existing menu items for this menu
$stmt = $pdo->prepare("DELETE FROM {$new_db['prefix']}term_relationships WHERE term_taxonomy_id = ?");
$stmt->execute([$menu_ttid]);

// Add menu items
foreach ($menu_items as $item) {
    if (empty($item['object_id'])) {
        echo "  Skipping {$item['title']} - not found\n";
        continue;
    }

    // Insert post
    $pdo->prepare("
        INSERT INTO {$new_db['prefix']}posts
        (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status,
         comment_status, ping_status, post_name, post_type, to_ping, pinged, post_content_filtered)
        VALUES (1, NOW(), NOW(), '', ?, '', 'publish', 'closed', 'closed', ?, 'nav_menu_item', '', '', '')
    ")->execute([$item['title'], sanitize_title($item['title'] . '-' . uniqid())]);

    $post_id = $pdo->lastInsertId();

    // Insert term_relationship
    $pdo->prepare("
        INSERT INTO {$new_db['prefix']}term_relationships (object_id, term_taxonomy_id, term_order)
        VALUES (?, ?, ?)
    ")->execute([$post_id, $menu_ttid, $item['order']]);

    // Insert postmeta
    $pdo->prepare("INSERT INTO {$new_db['prefix']}postmeta (post_id, meta_key, meta_value) VALUES (?, '_menu_item_type', ?)")
        ->execute([$post_id, $item['type']]);
    $pdo->prepare("INSERT INTO {$new_db['prefix']}postmeta (post_id, meta_key, meta_value) VALUES (?, '_menu_item_object_id', ?)")
        ->execute([$post_id, $item['object_id']]);
    $pdo->prepare("INSERT INTO {$new_db['prefix']}postmeta (post_id, meta_key, meta_value) VALUES (?, '_menu_item_object', ?)")
        ->execute([$post_id, $item['type'] === 'page' ? 'page' : 'category']);
    $pdo->prepare("INSERT INTO {$new_db['prefix']}postmeta (post_id, meta_key, meta_value) VALUES (?, '_menu_item_url', ?)")
        ->execute([$post_id, $item['url']]);
    $pdo->prepare("INSERT INTO {$new_db['prefix']}postmeta (post_id, meta_key, meta_value) VALUES (?, '_menu_item_target', ?)")
        ->execute([$post_id, '']);
    $pdo->prepare("INSERT INTO {$new_db['prefix']}postmeta (post_id, meta_key, meta_value) VALUES (?, '_menu_item_classes', ?)")
        ->execute([$post_id, 'a:1:{i:0;s:0:\"\";}']);
    $pdo->prepare("INSERT INTO {$new_db['prefix']}postmeta (post_id, meta_key, meta_value) VALUES (?, '_menu_item_xfn', ?)")
        ->execute([$post_id, '']);

    echo "  Added menu item: {$item['title']}\n";
}

// Update menu location
$menu_locations = get_option($pdo, $new_db, 'theme_mods_twentytwentyfour');
// Get current nav_menu_locations or set default
$locations = [];
$stmt = $pdo->query("SELECT option_value FROM {$new_db['prefix']}options WHERE option_name = 'theme_mods_twentytwentyfour'");
$theme_mods = $stmt->fetchColumn();
if ($theme_mods) {
    $locations = @unserialize($theme_mods) ?: [];
}

$locations['nav_menu_locations'] = ['primary' => $menu_ttid];
$locations_json = serialize($locations);
$pdo->prepare("UPDATE {$new_db['prefix']}options SET option_value = ? WHERE option_name = 'theme_mods_twentytwentyfour'")
    ->execute([$locations_json]);

// Also try to set as theme location
$pdo->prepare("INSERT INTO {$new_db['prefix']}options (option_name, option_value) VALUES ('nav_menu_locations', ?) ON DUPLICATE KEY UPDATE option_value = ?")
    ->execute([json_encode(['primary' => $menu_ttid]), json_encode(['primary' => $menu_ttid])]);

// Update term_taxonomy count
$pdo->prepare("UPDATE {$new_db['prefix']}term_taxonomy SET count = (SELECT COUNT(*) FROM {$new_db['prefix']}term_relationships WHERE term_taxonomy_id = ?) WHERE term_taxonomy_id = ?")
    ->execute([$menu_ttid, $menu_ttid]);

echo "\n=== Menu Created Successfully ===\n";
echo "Check http://localhost:8081/wp-admin/nav-menus.php\n";

function sanitize_title($title) {
    $title = preg_replace('/[^a-z0-9\x{4e00}-\x{9fa5}]/u', '-', strtolower($title));
    $title = preg_replace('/-+/', '-', $title);
    $title = trim($title, '-');
    return $title;
}

function get_option($pdo, $new_db, $option_name) {
    $stmt = $pdo->prepare("SELECT option_value FROM {$new_db['prefix']}options WHERE option_name = ?");
    $stmt->execute([$option_name]);
    return $stmt->fetchColumn();
}