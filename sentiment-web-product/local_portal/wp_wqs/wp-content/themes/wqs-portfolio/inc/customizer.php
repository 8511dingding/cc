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