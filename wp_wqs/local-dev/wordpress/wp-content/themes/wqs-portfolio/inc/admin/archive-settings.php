<?php
/**
 * Archive Sidebar Settings Admin Page
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Register the admin menu page
 */
function wqs_add_archive_settings_page()
{
    add_submenu_page(
        'themes.php',                    // Parent slug (Appearance menu)
        __('Archive Sidebar', 'wqs-portfolio'),
        __('Archive Sidebar', 'wqs-portfolio'),
        'manage_options',
        'wqs-archive-settings',
        'wqs_render_archive_settings_page'
    );
}
add_action('admin_menu', 'wqs_add_archive_settings_page');

/**
 * Register settings
 */
function wqs_archive_settings_init()
{
    // Register settings
    register_setting('wqs_archive_settings', 'wqs_photography_categories', array('sanitize_callback' => 'wqs_sanitize_archive_category_slugs'));
    register_setting('wqs_archive_settings', 'wqs_exhibition_categories', array('sanitize_callback' => 'wqs_sanitize_archive_category_slugs'));
    register_setting('wqs_archive_settings', 'wqs_shooting_categories', array('sanitize_callback' => 'wqs_sanitize_archive_category_slugs'));
    register_setting('wqs_archive_settings', 'wqs_review_categories', array('sanitize_callback' => 'wqs_sanitize_archive_category_slugs'));
    register_setting('wqs_archive_settings', 'wqs_show_all_categories');

    // Add settings section
    add_settings_section(
        'wqs_archive_sidebar_section',
        __('Archive Sidebar Categories', 'wqs-portfolio'),
        'wqs_archive_sidebar_section_callback',
        'wqs-archive-settings'
    );

    // Add settings fields
    add_settings_field(
        'wqs_photography_categories',
        __('Photography Categories', 'wqs-portfolio'),
        'wqs_photography_categories_callback',
        'wqs-archive-settings',
        'wqs_archive_sidebar_section'
    );

    add_settings_field(
        'wqs_exhibition_categories',
        __('Exhibition Categories', 'wqs-portfolio'),
        'wqs_exhibition_categories_callback',
        'wqs-archive-settings',
        'wqs_archive_sidebar_section'
    );

    add_settings_field(
        'wqs_shooting_categories',
        __('Shooting Categories', 'wqs-portfolio'),
        'wqs_shooting_categories_callback',
        'wqs-archive-settings',
        'wqs_archive_sidebar_section'
    );

    add_settings_field(
        'wqs_review_categories',
        __('Review Categories', 'wqs-portfolio'),
        'wqs_review_categories_callback',
        'wqs-archive-settings',
        'wqs_archive_sidebar_section'
    );

    add_settings_field(
        'wqs_show_all_categories',
        __('Show "All" Option', 'wqs-portfolio'),
        'wqs_show_all_categories_callback',
        'wqs-archive-settings',
        'wqs_archive_sidebar_section'
    );
}
add_action('admin_init', 'wqs_archive_settings_init');

/**
 * Sanitize comma-separated category slugs.
 */
function wqs_sanitize_archive_category_slugs($value)
{
    if (!is_string($value)) {
        return '';
    }

    $slugs = preg_split('/[\s,]+/', $value);
    $slugs = array_filter(array_map('sanitize_title', $slugs));
    $slugs = array_unique($slugs);

    return implode(', ', $slugs);
}

/**
 * Section callback
 */
function wqs_archive_sidebar_section_callback()
{
    echo '<p>' . __('Configure which categories to display in each archive sidebar. Leave empty to show all categories of that type.', 'wqs-portfolio') . '</p>';
    echo '<p>' . __('Enter category slugs separated by commas. Use the exact slugs from the list below; either language can be used and the frontend will show the current language version when available. Examples:', 'wqs-portfolio') . '</p>';
    echo '<ul style="list-style-type: disc; margin-left: 20px;">';
    echo '<li>Photography: <code>2000-photography-en, 2001-photography-en, 2002-photography-en</code></li>';
    echo '<li>Exhibition: <code>2000-exhibitions-en, 2001-exhibitions-en</code></li>';
    echo '<li>Shooting: <code>2000-shooting-en, 2001-shooting-en</code></li>';
    echo '<li>Reviews: <code>2002-reviews-en, 2003-reviews-en, 2004-reviews-en</code></li>';
    echo '</ul>';
}

/**
 * Photography categories field callback
 */
function wqs_photography_categories_callback()
{
    $value = get_option('wqs_photography_categories', '');
    echo '<textarea id="wqs_photography_categories" name="wqs_photography_categories" rows="3" cols="60" class="regular-text code" placeholder="2000-photography-en, 2001-photography-en, ...">' . esc_textarea($value) . '</textarea>';
    echo '<p class="description">Enter slugs like: <code>2000-photography-en,2001-photography-en,2002-photography-en</code></p>';
}

/**
 * Exhibition categories field callback
 */
function wqs_exhibition_categories_callback()
{
    $value = get_option('wqs_exhibition_categories', '');
    echo '<textarea id="wqs_exhibition_categories" name="wqs_exhibition_categories" rows="3" cols="60" class="regular-text code" placeholder="2000-exhibitions-en, 2001-exhibitions-en, ...">' . esc_textarea($value) . '</textarea>';
    echo '<p class="description">Enter slugs like: <code>2000-exhibitions-en,2001-exhibitions-en,2002-exhibitions-en</code></p>';
}

/**
 * Shooting categories field callback
 */
function wqs_shooting_categories_callback()
{
    $value = get_option('wqs_shooting_categories', '');
    echo '<textarea id="wqs_shooting_categories" name="wqs_shooting_categories" rows="3" cols="60" class="regular-text code" placeholder="2000-shooting-en, 2001-shooting-en, ...">' . esc_textarea($value) . '</textarea>';
    echo '<p class="description">Enter slugs like: <code>2000-shooting-en,2001-shooting-en,2002-shooting-en</code></p>';
}

/**
 * Review categories field callback
 */
function wqs_review_categories_callback()
{
    $value = get_option('wqs_review_categories', '');
    echo '<textarea id="wqs_review_categories" name="wqs_review_categories" rows="3" cols="60" class="regular-text code" placeholder="2002-reviews-en, 2003-reviews-en, ...">' . esc_textarea($value) . '</textarea>';
    echo '<p class="description">Enter slugs like: <code>2002-reviews-en,2003-reviews-en,2004-reviews-en</code></p>';
}

/**
 * Show all categories checkbox callback
 */
function wqs_show_all_categories_callback()
{
    $value = get_option('wqs_show_all_categories', '1');
    echo '<input type="checkbox" id="wqs_show_all_categories" name="wqs_show_all_categories" value="1"' . checked('1', $value, false) . '>';
    echo '<label for="wqs_show_all_categories">' . __('Show "All" option at the top of each sidebar section', 'wqs-portfolio') . '</label>';
}

/**
 * Render the settings page
 */
function wqs_render_archive_settings_page()
{
    // Get all categories for reference
    $all_cats = get_categories(array('hide_empty' => false, 'orderby' => 'name'));
    $photography_cats = array();
    $exhibition_cats = array();
    $shooting_cats = array();
    $review_cats = array();

    foreach ($all_cats as $cat) {
        if (preg_match('/Photography|摄影/i', $cat->name) || preg_match('/photography/i', $cat->slug)) {
            $photography_cats[$cat->slug] = $cat->name;
        }
        if (preg_match('/Exhibition|展览/i', $cat->name) || preg_match('/exhibition/i', $cat->slug)) {
            $exhibition_cats[$cat->slug] = $cat->name;
        }
        if (preg_match('/Shooting|工作照/i', $cat->name) || preg_match('/shooting/i', $cat->slug)) {
            $shooting_cats[$cat->slug] = $cat->name;
        }
        if (preg_match('/Review|评论/i', $cat->name) || preg_match('/review/i', $cat->slug)) {
            $review_cats[$cat->slug] = $cat->name;
        }
    }
    ?>
    <div class="wrap">
        <h1><?php echo esc_html(get_admin_page_title()); ?></h1>

        <form method="post" action="options.php">
            <?php settings_fields('wqs_archive_settings'); ?>
            <?php do_settings_sections('wqs-archive-settings'); ?>
            <?php submit_button(); ?>
        </form>

        <hr style="margin: 40px 0;">

        <h2><?php _e('Available Category Slugs', 'wqs-portfolio'); ?></h2>
        <p><?php _e('Copy these slugs into the fields above to include specific categories.', 'wqs-portfolio'); ?></p>

        <h3><?php _e('Photography Categories', 'wqs-portfolio'); ?></h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
            <?php foreach ($photography_cats as $slug => $name) : ?>
                <code style="background: #f0f0f0; padding: 4px 8px; border-radius: 3px; cursor: pointer;" title="<?php echo esc_attr($name); ?>" onclick="copyToClipboard('<?php echo esc_js($slug); ?>')"><?php echo esc_html($slug); ?></code>
            <?php endforeach; ?>
        </div>

        <h3><?php _e('Exhibition Categories', 'wqs-portfolio'); ?></h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
            <?php foreach ($exhibition_cats as $slug => $name) : ?>
                <code style="background: #f0f0f0; padding: 4px 8px; border-radius: 3px; cursor: pointer;" title="<?php echo esc_attr($name); ?>" onclick="copyToClipboard('<?php echo esc_js($slug); ?>')"><?php echo esc_html($slug); ?></code>
            <?php endforeach; ?>
        </div>

        <h3><?php _e('Shooting Categories', 'wqs-portfolio'); ?></h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
            <?php foreach ($shooting_cats as $slug => $name) : ?>
                <code style="background: #f0f0f0; padding: 4px 8px; border-radius: 3px; cursor: pointer;" title="<?php echo esc_attr($name); ?>" onclick="copyToClipboard('<?php echo esc_js($slug); ?>')"><?php echo esc_html($slug); ?></code>
            <?php endforeach; ?>
        </div>

        <h3><?php _e('Review Categories', 'wqs-portfolio'); ?></h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
            <?php foreach ($review_cats as $slug => $name) : ?>
                <code style="background: #f0f0f0; padding: 4px 8px; border-radius: 3px; cursor: pointer;" title="<?php echo esc_attr($name); ?>" onclick="copyToClipboard('<?php echo esc_js($slug); ?>')"><?php echo esc_html($slug); ?></code>
            <?php endforeach; ?>
        </div>

        <p><?php _e('Tip: Click on any slug to copy it to clipboard.', 'wqs-portfolio'); ?></p>
    </div>

    <script>
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(function() {
            alert('Copied: ' + text);
        }, function(err) {
            console.error('Could not copy text: ', err);
        });
    }
    </script>

    <style>
    .wrap code:hover {
        background: #e0e0e0;
        cursor: pointer;
    }
    </style>
    <?php
}
