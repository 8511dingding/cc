<?php
/**
 * Custom Post Types and Taxonomies
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Register Custom Post Types
 *
 * CPTs are disabled - all content uses standard 'post' type with Polylang for translations
 * Kept here for reference in case needed in the future
 */
// function wqs_register_post_types()
// {
// // Works Post Type
//     register_post_type('works', array(
// 'labels' => array(
//             'name' => __('作品', 'wqs-portfolio'),
//             'singular_name' => __('作品', 'wqs-portfolio'),
//             'menu_name' => __('作品', 'wqs-portfolio'),
//             'name_admin_bar' => __('作品', 'wqs-portfolio'),
//             'add_new' => __('添加新作品', 'wqs-portfolio'),
//             'add_new_item' => __('添加新作品', 'wqs-portfolio'),
//             'edit_item' => __('编辑作品', 'wqs-portfolio'),
//             'new_item' => __('新作品', 'wqs-portfolio'),
//             'view_item' => __('查看作品', 'wqs-portfolio'),
//             'search_items' => __('搜索作品', 'wqs-portfolio'),
//             'not_found' => __('未找到作品', 'wqs-portfolio'),
//             'not_found_in_trash' => __('回收站中未找到作品', 'wqs-portfolio'),
//         ),
//         'description' => __('王庆松的摄影作品', 'wqs-portfolio'),
//         'public' => true,
//         'show_ui' => true,
//         'show_in_menu' => true,
//         'show_in_nav_menus' => true,
//         'show_in_rest' => true,
//         'has_archive' => true,
//         'hierarchical' => false,
//         'supports' => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
//         'rewrite' => array('slug' => 'works'),
//         'menu_position' => 5,
//     ));
//
// // Exhibition Post Type
//     register_post_type('exhibition', array(
//         'labels' => array(
//             'name' => __('展览', 'wqs-portfolio'),
//             'singular_name' => __('展览', 'wqs-portfolio'),
//             'menu_name' => __('展览', 'wqs-portfolio'),
//             'add_new' => __('添加新展览', 'wqs-portfolio'),
//             'add_new_item' => __('添加新展览', 'wqs-portfolio'),
//             'edit_item' => __('编辑展览', 'wqs-portfolio'),
//             'view_item' => __('查看展览', 'wqs-portfolio'),
//             'search_items' => __('搜索展览', 'wqs-portfolio'),
//             'not_found' => __('未找到展览', 'wqs-portfolio'),
//         ),
//         'description' => __('王庆松的展览', 'wqs-portfolio'),
//         'public' => true,
//         'show_ui' => true,
//         'show_in_menu' => true,
//         'show_in_nav_menus' => true,
//         'show_in_rest' => true,
//         'has_archive' => true,
//         'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
//         'rewrite' => array('slug' => 'exhibitions'),
//         'menu_position' => 6,
//     ));
//
//     // Review Post Type
//     register_post_type('review', array(
//         'labels' => array(
//             'name' => __('评论', 'wqs-portfolio'),
//             'singular_name' => __('评论', 'wqs-portfolio'),
//             'menu_name' => __('评论', 'wqs-portfolio'),
//             'add_new' => __('添加新评论', 'wqs-portfolio'),
//             'add_new_item' => __('添加新评论', 'wqs-portfolio'),
//             'edit_item' => __('编辑评论', 'wqs-portfolio'),
//             'view_item' => __('查看评论', 'wqs-portfolio'),
//             'search_items' => __('搜索评论', 'wqs-portfolio'),
//             'not_found' => __('未找到评论', 'wqs-portfolio'),
//         ),
//         'description' => __('期刊和媒体报道', 'wqs-portfolio'),
//         'public' => true,
//         'show_ui' => true,
//         'show_in_menu' => true,
//         'show_in_nav_menus' => true,
//         'show_in_rest' => true,
//         'has_archive' => true,
//         'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
//         'rewrite' => array('slug' => 'reviews'),
//         'menu_position' => 7,
//     ));
//
//     // Behind the Scenes Post Type
//     register_post_type('behind_the_scenes', array(
//         'labels' => array(
//             'name' => __('工作照', 'wqs-portfolio'),
//             'singular_name' => __('工作照', 'wqs-portfolio'),
//             'menu_name' => __('工作照', 'wqs-portfolio'),
//             'add_new' => __('添加新工作照', 'wqs-portfolio'),
//             'add_new_item' => __('添加新工作照', 'wqs-portfolio'),
//             'edit_item' => __('编辑工作照', 'wqs-portfolio'),
//             'view_item' => __('查看工作照', 'wqs-portfolio'),
//             'search_items' => __('搜索工作照', 'wqs-portfolio'),
//             'not_found' => __('未找到工作照', 'wqs-portfolio'),
//         ),
//         'description' => __('作品拍摄背后的故事', 'wqs-portfolio'),
//         'public' => true,
//         'show_ui' => true,
//         'show_in_menu' => true,
//         'show_in_nav_menus' => true,
//         'show_in_rest' => true,
//         'has_archive' => true,
//         'supports' => array('title', 'editor', 'thumbnail', 'excerpt'),
//         'rewrite' => array('slug' => 'behind-the-scenes'),
//         'menu_position' => 8,
//     ));
// }
// add_action('init', 'wqs_register_post_types');

/**
 * Register Custom Taxonomies for Works
 *
 * Taxonomies are disabled since they depend on disabled CPTs
 * Kept here for reference in case needed in the future
 */
// function wqs_register_taxonomies()
// {
//     // Year taxonomy
//     register_taxonomy('works_year', 'works', array(
//         'labels' => array(
//             'name' => __('年份', 'wqs-portfolio'),
//             'singular_name' => __('年份', 'wqs-portfolio'),
//             'search_items' => __('搜索年份', 'wqs-portfolio'),
//             'all_items' => __('所有年份', 'wqs-portfolio'),
//             'edit_item' => __('编辑年份', 'wqs-portfolio'),
//             'update_item' => __('更新年份', 'wqs-portfolio'),
//             'add_new_item' => __('添加新年份', 'wqs-portfolio'),
//             'new_item_name' => __('新年份名称', 'wqs-portfolio'),
//             'not_found' => __('未找到年份', 'wqs-portfolio'),
//         ),
//         'hierarchical' => true,
//         'show_ui' => true,
//         'show_admin_column' => true,
//         'query_var' => true,
//         'show_in_rest' => true,
//         'rewrite' => array('slug' => 'works-year'),
//     ));
//
//     // Category taxonomy for works
//     register_taxonomy('works_category', 'works', array(
//         'labels' => array(
//             'name' => __('作品分类', 'wqs-portfolio'),
//             'singular_name' => __('作品分类', 'wqs-portfolio'),
//             'search_items' => __('搜索分类', 'wqs-portfolio'),
//             'all_items' => __('所有分类', 'wqs-portfolio'),
//             'edit_item' => __('编辑分类', 'wqs-portfolio'),
//             'update_item' => __('更新分类', 'wqs-portfolio'),
//             'add_new_item' => __('添加新分类', 'wqs-portfolio'),
//             'new_item_name' => __('新分类名称', 'wqs-portfolio'),
//             'not_found' => __('未找到分类', 'wqs-portfolio'),
//         ),
//         'hierarchical' => true,
//         'show_ui' => true,
//         'show_admin_column' => true,
//         'query_var' => true,
//         'show_in_rest' => true,
//         'rewrite' => array('slug' => 'works-category'),
//     ));
// }
// add_action('init', 'wqs_register_taxonomies');

/**
 * Flush rewrite rules on theme activation (only once)
 *
 * CPTs are disabled, but we still flush to clean up any old rewrite rules
 */
function wqs_rewrite_flush()
{
    flush_rewrite_rules();
}
add_action('after_switch_theme', 'wqs_rewrite_flush');