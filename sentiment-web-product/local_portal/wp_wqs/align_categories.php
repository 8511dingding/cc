<?php
/**
 * Script to align English and Chinese categories
 * Creates Chinese category versions and fixes translation pairs
 */

$db_host = '127.0.0.1:3307';
$db_user = 'root';
$db_pass = 'GM3750-jm';
$db_name = 'wqs_wordpress';

$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$conn->set_charset('utf8mb4');

// Category name translations
$translations = [
    '14-18 Photography' => '14-18 摄影',
    '1996 Exhibitions' => '1996 展览',
    '1997-1999 Photography' => '1997-1999 摄影',
    '1997-1999 Shooting' => '1997-1999 工作照',
    '2000 Exhibitions' => '2000 展览',
    '2000 Photography' => '2000 摄影',
    '2000 Shooting' => '2000 工作照',
    '2001 Exhibitions' => '2001 展览',
    '2001 Photography' => '2001 摄影',
    '2001 Shooting' => '2001 工作照',
    '2002 Exhibitions' => '2002 展览',
    '2002 Photography' => '2002 摄影',
    '2002 Reviews' => '2002 评论',
    '2002 Shooting' => '2002 工作照',
    '2003 Exhibitions' => '2003 展览',
    '2003 Photography' => '2003 摄影',
    '2003 Reviews' => '2003 评论',
    '2003 Shooting' => '2003 工作照',
    '2004 Exhibitions' => '2004 展览',
    '2004 Photography' => '2004 摄影',
    '2004 Reviews' => '2004 评论',
    '2004 Shooting' => '2004 工作照',
    '2005 Exhibitions' => '2005 展览',
    '2005 Photography' => '2005 摄影',
    '2005 Reviews' => '2005 评论',
    '2005 Shooting' => '2005 工作照',
    '2006 Exhibitions' => '2006 展览',
    '2006 Reviews' => '2006 评论',
    '2006 Shooting' => '2006 工作照',
    '2007 Exhibitions' => '2007 展览',
    '2007 Photography' => '2007 摄影',
    '2007 Reviews' => '2007 评论',
    '2007 Shooting' => '2007 工作照',
    '2008 Exhibitions' => '2008 展览',
    '2008 Photography' => '2008 摄影',
    '2008 Reviews' => '2008 评论',
    '2008 Shooting' => '2008 工作照',
    '2009 Exhibitions' => '2009 展览',
    '2009 Photography' => '2009 摄影',
    '2009 Reviews' => '2009 评论',
    '2009 Shooting' => '2009 工作照',
    '2010 Exhibitions' => '2010 展览',
    '2010 Photography' => '2010 摄影',
    '2010 Reviews' => '2010 评论',
    '2010 Shooting' => '2010 工作照',
    '2011 Exhibitions' => '2011 展览',
    '2011 Photography' => '2011 摄影',
    '2011 Reviews' => '2011 评论',
    '2011 Shooting' => '2011 工作照',
    '2012 Exhibitions' => '2012 展览',
    '2012 Photography' => '2012 摄影',
    '2012 Reviews' => '2012 评论',
    '2012 Shooting' => '2012 工作照',
    '2013 Exhibitions' => '2013 展览',
    '2013 Photography' => '2013 摄影',
    '2013 Reviews' => '2013 评论',
    '2013 Shooting' => '2013 工作照',
    '2014 Exhibitions' => '2014 展览',
    '2014 Reviews' => '2014 评论',
    '2014 Shooting' => '2014 工作照',
    '2015 Exhibitions' => '2015 展览',
    '2015 Photography' => '2015 摄影',
    '2015 Reviews' => '2015 评论',
    '2015 Shooting' => '2015 工作照',
    '2016 Exhibitions' => '2016 展览',
    '2016 Photography' => '2016 摄影',
    '2016 Reviews' => '2016 评论',
    '2017 Exhibitions' => '2017 展览',
    '2017 Reviews' => '2017 评论',
    '2018 Photography' => '2018 摄影',
    '2018 Reviews' => '2018 评论',
    '2019 Photography' => '2019 摄影',
    '2019 Reviews' => '2019 评论',
    '2020 Exhibitions' => '2020 展览',
    '2020 Photography' => '2020 摄影',
    '2020 Reviews' => '2020 评论',
    '2021 Reviews' => '2021 评论',
    '2022 Reviews' => '2022 评论',
    '96-03 Exhibitions' => '96-03 展览',
    '98-01 Reviews' => '98-01 评论',
    'Biography' => 'Biography',
    'Contact' => 'Contact',
    'Exhibitions' => '展览',
    'Original Chinese' => 'Original Chinese',
    'Others' => '其他',
    'Photography' => '摄影',
    'Reviews' => '评论',
    'Shooting' => '工作照',
    'Video' => '视频',
    'X Exhibitions' => 'X 展览',
    'X Photography' => 'X 摄影',
];

echo "Starting category alignment...\n";

$created = 0;
$updated = 0;

// Get all category term_taxonomy_ids and their translation_ids
$sql = "SELECT plt.element_id AS en_ttid, plt.translation_id
        FROM wp_pll_translations plt
        JOIN wp_term_taxonomy tt ON tt.term_taxonomy_id = plt.element_id
        WHERE plt.language = 'en'
        AND tt.taxonomy = 'category'";

$result = $conn->query($sql);
$translation_map = []; // en_ttid => translation_id

while ($row = $result->fetch_assoc()) {
    $translation_map[$row['en_ttid']] = $row['translation_id'];
}

// Process each English category
foreach ($translation_map as $en_ttid => $translation_id) {
    // Get English category info
    $cat_info = $conn->query("
        SELECT t.term_id, t.name, t.slug, tt.count
        FROM wp_term_taxonomy tt
        JOIN wp_terms t ON t.term_id = tt.term_id
        WHERE tt.term_taxonomy_id = $en_ttid
    ")->fetch_assoc();

    if (!$cat_info) continue;

    $en_name = $cat_info['name'];
    $en_slug = $cat_info['slug'];
    $en_term_id = $cat_info['term_id'];

    // Get Chinese translation
    $zh_name = $translations[$en_name] ?? $en_name . ' (zh)';
    $zh_slug = $en_slug . '-zh';

    // Check if Chinese version already exists
    $existing_zh = $conn->query("SELECT term_id FROM wp_terms WHERE slug = '$zh_slug'")->fetch_assoc();

    if ($existing_zh) {
        $zh_term_id = $existing_zh['term_id'];
        echo "Chinese version already exists for '$en_name'\n";
    } else {
        // Create Chinese category
        $conn->query("INSERT INTO wp_terms (name, slug) VALUES ('" . $conn->real_escape_string($zh_name) . "', '$zh_slug')");
        $zh_term_id = $conn->insert_id;
        $created++;
        echo "Created Chinese category: $zh_name (term_id: $zh_term_id)\n";
    }

    // Create or update term_taxonomy for Chinese category if needed
    $zh_ttid_check = $conn->query("SELECT term_taxonomy_id FROM wp_term_taxonomy WHERE term_id = $zh_term_id AND taxonomy = 'category'")->fetch_assoc();

    if (!$zh_ttid_check) {
        $conn->query("INSERT INTO wp_term_taxonomy (term_id, taxonomy, description, parent, count) VALUES ($zh_term_id, 'category', '', 0, 0)");
        $zh_ttid = $conn->insert_id;
    } else {
        $zh_ttid = $zh_ttid_check['term_taxonomy_id'];
    }

    // Update Polylang translation - check if Chinese translation exists
    $zh_exists = $conn->query("SELECT id FROM wp_pll_translations WHERE translation_id = $translation_id AND language = 'zh'")->fetch_assoc();

    if ($zh_exists) {
        // Update existing
        $conn->query("UPDATE wp_pll_translations SET element_id = $zh_ttid WHERE translation_id = $translation_id AND language = 'zh'");
        $updated++;
        echo "Updated translation for '$en_name' (translation_id: $translation_id, zh_ttid: $zh_ttid)\n";
    } else {
        // Insert new
        $conn->query("INSERT INTO wp_pll_translations (translation_id, language, element_id) VALUES ($translation_id, 'zh', $zh_ttid)");
        $updated++;
        echo "Created translation for '$en_name' (translation_id: $translation_id, zh_ttid: $zh_ttid)\n";
    }
}

echo "\nDone! Created $created new Chinese categories, updated $updated translations.\n";

$conn->close();