<?php
$pdo = new PDO('mysql:host=127.0.0.1;port=3307;dbname=wqs_wordpress;charset=utf8mb4', 'root', 'GM3750-jm');

// Populate wp_languages table with EN and ZH language data
$stmt = $pdo->query('
    SELECT t.term_id, t.name, t.slug
    FROM wp_terms t
    JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id
    WHERE tt.taxonomy = "language"
');
$lang_terms = $stmt->fetchAll();
echo "Language terms found: " . count($lang_terms) . "\n";

foreach ($lang_terms as $lang) {
    echo "Processing: " . $lang['name'] . " (slug: " . $lang['slug'] . ")\n";

    if ($lang['slug'] == 'en') {
        $locale = 'en_GB';
        $name = 'English';
        $lang_id = 1;
    } else {
        $locale = 'zh_CN';
        $name = 'Chinese';
        $lang_id = 2;
    }

    // Insert into wp_languages
    $pdo->prepare('INSERT INTO wp_languages (term_id, lang_id, slug, name, locale, flag_url) VALUES (?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE name=VALUES(name), locale=VALUES(locale)')->execute([$lang['term_id'], $lang_id, $lang['slug'], $name, $locale, '']);
    echo "  Inserted/updated: term_id=" . $lang['term_id'] . ", lang_id=" . $lang_id . "\n";
}

echo "\nwp_languages now has " . $pdo->query('SELECT COUNT(*) FROM wp_languages')->fetchColumn() . " entries\n";

// Verify
$stmt2 = $pdo->query('SELECT * FROM wp_languages');
echo "\nwp_languages content:\n";
while ($row = $stmt2->fetch()) {
    print_r($row);
}