<?php
/**
 * Debug Polylang Settings
 *访问: /wp-content/themes/wqs-portfolio/debug-pll.php
 */

require_once dirname(__FILE__) . '/../../../wp-load.php';

header('Content-Type: text/plain; charset=utf-8');

echo "=== Polylang Settings Debug ===\n\n";

// Get Polylang options
$pll_options = get_option('polylang');

if ($pll_options === false) {
    echo "Polylang options not found in database!\n";
} else {
    echo "Polylang Options:\n";
    print_r($pll_options);

    echo "\n\nKey values:\n";
    echo "force_lang: " . ($pll_options['force_lang'] ?? 'not set') . "\n";
    echo "hide_default: " . ($pll_options['hide_default'] ?? 'not set') . "\n";
    echo "redirect_lang: " . ($pll_options['redirect_lang'] ?? 'not set') . "\n";
}

// Get all languages
if (function_exists('pll_languages_list')) {
    echo "\n\nLanguages configured:\n";
    $languages = pll_languages_list();
    print_r($languages);
}

// Get current language
if (function_exists('pll_current_language')) {
    echo "\n\nCurrent language: " . pll_current_language('slug') . "\n";
}

// Get menu items with language info
echo "\n\n=== Menu Items ===\n";
$menus = wp_get_nav_menus();
foreach ($menus as $menu) {
    echo "\nMenu: {$menu->name} (ID: {$menu->term_id})\n";
    $items = wp_get_nav_menu_items($menu->term_id);
    foreach ($items as $item) {
        $lang = get_post_meta($item->ID, '_pll_menu_item_language', true);
        echo "  - {$item->title} (ID: {$item->ID}) lang: {$lang}\n";
    }
}