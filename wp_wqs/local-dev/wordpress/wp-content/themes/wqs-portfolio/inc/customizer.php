<?php
/**
 * Customizer settings
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Add Customizer settings for Archive Sidebar
 */
function wqs_customize_register_archive($wp_customize)
{
    // Archive Sidebar Section
    $wp_customize->add_section('wqs_archive_sidebar', array(
        'title'    => __('Archive Sidebar', 'wqs-portfolio'),
        'priority' => 35,
        'panel'    => 'wqs_archive_panel',
    ));

    // Photography Categories
    $wp_customize->add_setting('wqs_photography_categories', array(
        'default'           => '',
        'sanitize_callback' => 'sanitize_text_field',
        'transport'         => 'refresh',
    ));

    $wp_customize->add_control('wqs_photography_categories', array(
        'label'    => __('Photography Categories', 'wqs-portfolio'),
        'section'  => 'wqs_archive_sidebar',
        'type'     => 'text',
        'description' => __('Enter category slugs separated by commas (e.g., 2000-photography,2001-photography). Leave empty to show all Photography subcategories.', 'wqs-portfolio'),
    ));

    // Exhibition Categories
    $wp_customize->add_setting('wqs_exhibition_categories', array(
        'default'           => '',
        'sanitize_callback' => 'sanitize_text_field',
        'transport'         => 'refresh',
    ));

    $wp_customize->add_control('wqs_exhibition_categories', array(
        'label'    => __('Exhibition Categories', 'wqs-portfolio'),
        'section'  => 'wqs_archive_sidebar',
        'type'     => 'text',
        'description' => __('Enter category slugs separated by commas. Leave empty to show all.', 'wqs-portfolio'),
    ));

    // Shooting Categories
    $wp_customize->add_setting('wqs_shooting_categories', array(
        'default'           => '',
        'sanitize_callback' => 'sanitize_text_field',
        'transport'         => 'refresh',
    ));

    $wp_customize->add_control('wqs_shooting_categories', array(
        'label'    => __('Shooting Categories', 'wqs-portfolio'),
        'section'  => 'wqs_archive_sidebar',
        'type'     => 'text',
        'description' => __('Enter category slugs separated by commas. Leave empty to show all.', 'wqs-portfolio'),
    ));

    // Show All option
    $wp_customize->add_setting('wqs_show_all_categories', array(
        'default'           => '1',
        'sanitize_callback' => 'sanitize_text_field',
        'transport'         => 'refresh',
    ));

    $wp_customize->add_control('wqs_show_all_categories', array(
        'label'    => __('Show "All" Option', 'wqs-portfolio'),
        'section'  => 'wqs_archive_sidebar',
        'type'     => 'checkbox',
        'description' => __('Show "All" option at the top of each sidebar section.', 'wqs-portfolio'),
    ));
}
add_action('customize_register', 'wqs_customize_register_archive');

/**
 * Get configured Photography categories
 */
function wqs_get_configured_photography_categories()
{
    $setting = get_option('wqs_photography_categories', '');
    if (empty($setting)) {
        return array();
    }
    return array_map('trim', explode(',', $setting));
}

/**
 * Get configured Exhibition categories
 */
function wqs_get_configured_exhibition_categories()
{
    $setting = get_option('wqs_exhibition_categories', '');
    if (empty($setting)) {
        return array();
    }
    return array_map('trim', explode(',', $setting));
}

/**
 * Get configured Shooting categories
 */
function wqs_get_configured_shooting_categories()
{
    $setting = get_option('wqs_shooting_categories', '');
    if (empty($setting)) {
        return array();
    }
    return array_map('trim', explode(',', $setting));
}

/**
 * Whether to show "All" option
 */
function wqs_show_all_categories()
{
    return get_option('wqs_show_all_categories', '1') === '1';
}

/**
 * Add Customizer settings for homepage slider
 */
function wqs_customize_register($wp_customize)
{
    // Homepage Slider Section
    $wp_customize->add_section('wqs_home_slider', array(
        'title'    => __('Homepage Slider', 'wqs-portfolio'),
        'priority' => 30,
    ));

    // Slider Shortcode Setting
    $wp_customize->add_setting('wqs_slider_shortcode', array(
        'default'           => '[metaslider id="1639"]',
        'sanitize_callback' => 'wp_kses_post',
        'transport'         => 'refresh',
    ));

    $wp_customize->add_control('wqs_slider_shortcode', array(
        'label'    => __('Slider Shortcode', 'wqs-portfolio'),
        'section'  => 'wqs_home_slider',
        'type'     => 'text',
        'description' => __('Enter the MetaSlider shortcode (e.g., [metaslider id="1639"])', 'wqs-portfolio'),
    ));

    // Slider Height Setting
    $wp_customize->add_setting('wqs_slider_height', array(
        'default'           => '70vh',
        'sanitize_callback' => 'sanitize_text_field',
        'transport'         => 'refresh',
    ));

    $wp_customize->add_control('wqs_slider_height', array(
        'label'    => __('Slider Height', 'wqs-portfolio'),
        'section'  => 'wqs_home_slider',
        'type'     => 'text',
        'description' => __('e.g., 70vh, 500px, 100%', 'wqs-portfolio'),
    ));
}
add_action('customize_register', 'wqs_customize_register');

/**
 * Get slider shortcode from customizer or return default
 */
function wqs_get_slider_shortcode()
{
    return get_theme_mod('wqs_slider_shortcode', '[metaslider id="1639"]');
}

/**
 * Get slider height from customizer or return default
 */
function wqs_get_slider_height()
{
    return get_theme_mod('wqs_slider_height', '70vh');
}