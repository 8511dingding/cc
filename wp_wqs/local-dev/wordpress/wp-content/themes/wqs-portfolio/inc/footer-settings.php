<?php
/**
 * Editable footer settings.
 *
 * @package WQS_Portfolio
 */

defined('ABSPATH') || exit;

function wqs_get_footer_default_settings()
{
    return array(
        'brand_en'       => 'Wang Qingsong',
        'brand_zh'       => '王庆松',
        'address_en'     => 'Beijing, China',
        'address_zh'     => '中国，北京',
        'address_layout' => 'under',
        'button_1_en'    => 'Biography',
        'button_1_zh'    => '简历',
        'button_1_url_en'=> home_url('/biography/'),
        'button_1_url_zh'=> home_url('/zh/biography/'),
        'button_2_en'    => 'Contact',
        'button_2_zh'    => '联系',
        'button_2_url_en'=> home_url('/contact/'),
        'button_2_url_zh'=> home_url('/zh/contact/'),
        'copyright_en'   => 'Wang Qingsong. All rights reserved.',
        'copyright_zh'   => '王庆松。保留所有权利。',
        'start_year'     => 1997,
    );
}

function wqs_get_footer_settings()
{
    $defaults = wqs_get_footer_default_settings();
    $stored = get_option('wqs_footer_settings', array());
    $settings = wp_parse_args(is_array($stored) ? $stored : array(), $defaults);
    $settings['address_layout'] = in_array($settings['address_layout'], array('under', 'beside', 'bottom'), true)
        ? $settings['address_layout']
        : 'under';
    $settings['start_year'] = min((int) wp_date('Y'), max(1900, absint($settings['start_year'])));

    return $settings;
}

function wqs_sanitize_footer_settings($input)
{
    $defaults = wqs_get_footer_default_settings();
    $input = is_array($input) ? $input : array();
    $settings = array();

    foreach (array('brand_en', 'brand_zh', 'address_en', 'address_zh', 'button_1_en', 'button_1_zh', 'button_2_en', 'button_2_zh', 'copyright_en', 'copyright_zh') as $field) {
        $settings[$field] = sanitize_text_field($input[$field] ?? $defaults[$field]);
    }

    foreach (array('button_1_url_en', 'button_1_url_zh', 'button_2_url_en', 'button_2_url_zh') as $field) {
        $settings[$field] = esc_url_raw($input[$field] ?? $defaults[$field]);
    }

    $layout = sanitize_key($input['address_layout'] ?? 'under');
    $settings['address_layout'] = in_array($layout, array('under', 'beside', 'bottom'), true) ? $layout : 'under';
    $settings['start_year'] = min((int) wp_date('Y'), max(1900, absint($input['start_year'] ?? 1997)));

    return $settings;
}

function wqs_register_footer_settings_page()
{
    add_submenu_page(
        'wqs-homepage-templates',
        __('Footer Settings', 'wqs-portfolio'),
        __('Footer Settings', 'wqs-portfolio'),
        'edit_theme_options',
        'wqs-footer-settings',
        'wqs_render_footer_settings_page'
    );
}
add_action('admin_menu', 'wqs_register_footer_settings_page');

function wqs_render_footer_settings_page()
{
    if (!current_user_can('edit_theme_options')) {
        return;
    }

    if (isset($_POST['wqs_footer_nonce'])
        && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['wqs_footer_nonce'])), 'wqs_save_footer_settings')) {
        $input = isset($_POST['wqs_footer_settings']) && is_array($_POST['wqs_footer_settings'])
            ? wp_unslash($_POST['wqs_footer_settings'])
            : array();
        update_option('wqs_footer_settings', wqs_sanitize_footer_settings($input));
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html__('Footer settings saved.', 'wqs-portfolio') . '</p></div>';
    }

    $settings = wqs_get_footer_settings();
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('Footer Settings', 'wqs-portfolio'); ?></h1>
        <p><?php esc_html_e('Edit footer identity, address placement, navigation buttons, and copyright text.', 'wqs-portfolio'); ?></p>
        <form method="post" style="max-width:1000px;">
            <?php wp_nonce_field('wqs_save_footer_settings', 'wqs_footer_nonce'); ?>
            <table class="form-table" role="presentation">
                <tbody>
                    <?php
                    $fields = array(
                        'brand_en' => 'Brand name (English)',
                        'brand_zh' => '品牌名称（中文）',
                        'address_en' => 'Address (English)',
                        'address_zh' => '地址（中文）',
                        'button_1_en' => 'Button 1 label (English)',
                        'button_1_zh' => '按钮一名称（中文）',
                        'button_1_url_en' => 'Button 1 URL (English)',
                        'button_1_url_zh' => '按钮一链接（中文）',
                        'button_2_en' => 'Button 2 label (English)',
                        'button_2_zh' => '按钮二名称（中文）',
                        'button_2_url_en' => 'Button 2 URL (English)',
                        'button_2_url_zh' => '按钮二链接（中文）',
                        'copyright_en' => 'Copyright text (English)',
                        'copyright_zh' => '版权文字（中文）',
                    );
                    foreach ($fields as $field => $label) :
                        $type = strpos($field, '_url_') !== false ? 'url' : 'text';
                        ?>
                        <tr>
                            <th scope="row"><label for="wqs-footer-<?php echo esc_attr($field); ?>"><?php echo esc_html($label); ?></label></th>
                            <td><input class="regular-text" id="wqs-footer-<?php echo esc_attr($field); ?>" type="<?php echo esc_attr($type); ?>" name="wqs_footer_settings[<?php echo esc_attr($field); ?>]" value="<?php echo esc_attr($settings[$field]); ?>"></td>
                        </tr>
                    <?php endforeach; ?>
                    <tr>
                        <th scope="row"><label for="wqs-footer-layout"><?php esc_html_e('Address position', 'wqs-portfolio'); ?></label></th>
                        <td>
                            <select id="wqs-footer-layout" name="wqs_footer_settings[address_layout]">
                                <option value="under" <?php selected($settings['address_layout'], 'under'); ?>><?php esc_html_e('Under the name', 'wqs-portfolio'); ?></option>
                                <option value="beside" <?php selected($settings['address_layout'], 'beside'); ?>><?php esc_html_e('Beside the name', 'wqs-portfolio'); ?></option>
                                <option value="bottom" <?php selected($settings['address_layout'], 'bottom'); ?>><?php esc_html_e('Beside the copyright', 'wqs-portfolio'); ?></option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="wqs-footer-year"><?php esc_html_e('Copyright start year', 'wqs-portfolio'); ?></label></th>
                        <td><input id="wqs-footer-year" type="number" min="1900" max="<?php echo esc_attr(wp_date('Y')); ?>" name="wqs_footer_settings[start_year]" value="<?php echo esc_attr($settings['start_year']); ?>"></td>
                    </tr>
                </tbody>
            </table>
            <?php submit_button(__('Save Footer Settings', 'wqs-portfolio')); ?>
        </form>
    </div>
    <?php
}
