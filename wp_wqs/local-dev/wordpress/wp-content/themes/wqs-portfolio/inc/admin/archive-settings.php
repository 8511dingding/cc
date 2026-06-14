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
    register_setting('wqs_archive_settings', 'wqs_photography_categories');
    register_setting('wqs_archive_settings', 'wqs_exhibition_categories');
    register_setting('wqs_archive_settings', 'wqs_shooting_categories');
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
        'wqs_show_all_categories',
        __('Show "All" Option', 'wqs-portfolio'),
        'wqs_show_all_categories_callback',
        'wqs-archive-settings',
        'wqs_archive_sidebar_section'
    );
}
add_action('admin_init', 'wqs_archive_settings_init');

/**
 * Section callback
 */
function wqs_archive_sidebar_section_callback()
{
    echo '<p>' . __('Configure which categories to display in each archive sidebar. Leave empty to show all categories of that type.', 'wqs-portfolio') . '</p>';
    echo '<p>' . __('Enter category slugs separated by commas. Examples:', 'wqs-portfolio') . '</p>';
    echo '<ul style="list-style-type: disc; margin-left: 20px;">';
    echo '<li>Photography: <code>2000-photography, 2001-photography, 2002-photography</code></li>';
    echo '<li>Exhibition: <code>2000-exhibitions, 2001-exhibitions</code></li>';
    echo '<li>Shooting: <code>2000-shooting, 2001-shooting</code></li>';
    echo '</ul>';
}

/**
 * Photography categories field callback
 */
function wqs_photography_categories_callback()
{
    $value = get_option('wqs_photography_categories', '');
    echo '<textarea id="wqs_photography_categories" name="wqs_photography_categories" rows="3" cols="60" class="regular-text code" placeholder="2000-photography, 2001-photography, ...">' . esc_textarea($value) . '</textarea>';
    echo '<p class="description">Enter slugs like: <code>2000-photography,2001-photography,2002-photography</code></p>';
}

/**
 * Exhibition categories field callback
 */
function wqs_exhibition_categories_callback()
{
    $value = get_option('wqs_exhibition_categories', '');
    echo '<textarea id="wqs_exhibition_categories" name="wqs_exhibition_categories" rows="3" cols="60" class="regular-text code" placeholder="2000-exhibitions, 2001-exhibitions, ...">' . esc_textarea($value) . '</textarea>';
    echo '<p class="description">Enter slugs like: <code>2000-exhibitions,2001-exhibitions,2002-exhibitions</code></p>';
}

/**
 * Shooting categories field callback
 */
function wqs_shooting_categories_callback()
{
    $value = get_option('wqs_shooting_categories', '');
    echo '<textarea id="wqs_shooting_categories" name="wqs_shooting_categories" rows="3" cols="60" class="regular-text code" placeholder="2000-shooting, 2001-shooting, ...">' . esc_textarea($value) . '</textarea>';
    echo '<p class="description">Enter slugs like: <code>2000-shooting,2001-shooting,2002-shooting</code></p>';
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

    foreach ($all_cats as $cat) {
        if (preg_match('/Photography/i', $cat->name) || preg_match('/^\d{2,4}\s+Photography/i', $cat->name)) {
            $photography_cats[$cat->slug] = $cat->name;
        }
        if (preg_match('/Exhibition/i', $cat->name) || preg_match('/^\d{2,4}\s+Exhibition/i', $cat->name)) {
            $exhibition_cats[$cat->slug] = $cat->name;
        }
        if (preg_match('/Shooting/i', $cat->name) || preg_match('/^\d{2,4}\s+Shooting/i', $cat->name)) {
            $shooting_cats[$cat->slug] = $cat->name;
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

