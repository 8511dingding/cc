<?php
/**
 * Social accounts and article sharing.
 *
 * @package WQS_Portfolio
 */

defined('ABSPATH') || exit;

/**
 * Supported social platforms in their default display order.
 */
function wqs_get_social_platforms()
{
    return array(
        'facebook' => array(
            'label'       => 'Facebook',
            'short_label' => 'Facebook',
            'icon'        => 'fa-facebook-f',
            'share_mode'  => 'direct',
        ),
        'xiaohongshu' => array(
            'label'       => 'Xiaohongshu',
            'short_label' => '小红书',
            'icon'        => '',
            'share_mode'  => 'qr',
        ),
        'weibo' => array(
            'label'       => 'Weibo',
            'short_label' => '微博',
            'icon'        => 'fa-weibo',
            'share_mode'  => 'direct',
        ),
        'tiktok' => array(
            'label'       => 'TikTok',
            'short_label' => 'TikTok',
            'icon'        => 'fa-tiktok',
            'share_mode'  => 'qr',
        ),
        'douyin' => array(
            'label'       => 'Douyin',
            'short_label' => '抖音',
            'icon'        => 'fa-tiktok',
            'share_mode'  => 'qr',
        ),
        'instagram' => array(
            'label'       => 'Instagram',
            'short_label' => 'Instagram',
            'icon'        => 'fa-instagram',
            'share_mode'  => 'qr',
        ),
    );
}

/**
 * Default social settings.
 */
function wqs_get_social_default_settings()
{
    $settings = array(
        'home_enabled'     => 1,
        'share_posts'      => 1,
        'share_pages'      => 1,
        'share_works'      => 1,
        'native_share'     => 1,
        'qr_fallback'      => 1,
        'home_heading_en'  => 'Follow Wang Qingsong',
        'home_heading_zh'  => '关注王庆松',
        'platforms'        => array(),
    );

    $order = 10;
    foreach (wqs_get_social_platforms() as $key => $platform) {
        $settings['platforms'][$key] = array(
            'account_enabled' => 0,
            'share_enabled'   => 1,
            'quick_enabled'   => in_array($key, array('facebook', 'xiaohongshu'), true) ? 1 : 0,
            'account_url'     => '',
            'handle'          => '',
            'order'           => $order,
        );
        $order += 10;
    }

    return $settings;
}

/**
 * Return sanitized social settings.
 */
function wqs_get_social_settings()
{
    $defaults = wqs_get_social_default_settings();
    $stored = get_option('wqs_social_settings', array());
    $stored = is_array($stored) ? $stored : array();
    $settings = wp_parse_args($stored, $defaults);
    $settings['platforms'] = isset($stored['platforms']) && is_array($stored['platforms'])
        ? $stored['platforms']
        : array();

    foreach (array('home_enabled', 'share_posts', 'share_pages', 'share_works', 'native_share', 'qr_fallback') as $field) {
        $settings[$field] = empty($settings[$field]) ? 0 : 1;
    }

    $settings['home_heading_en'] = sanitize_text_field($settings['home_heading_en'] ?? $defaults['home_heading_en']);
    $settings['home_heading_zh'] = sanitize_text_field($settings['home_heading_zh'] ?? $defaults['home_heading_zh']);

    foreach (wqs_get_social_platforms() as $key => $platform) {
        $value = isset($settings['platforms'][$key]) && is_array($settings['platforms'][$key])
            ? $settings['platforms'][$key]
            : array();
        $settings['platforms'][$key] = wp_parse_args($value, $defaults['platforms'][$key]);
        $settings['platforms'][$key]['account_enabled'] = empty($settings['platforms'][$key]['account_enabled']) ? 0 : 1;
        $settings['platforms'][$key]['share_enabled'] = empty($settings['platforms'][$key]['share_enabled']) ? 0 : 1;
        $settings['platforms'][$key]['quick_enabled'] = empty($settings['platforms'][$key]['quick_enabled']) ? 0 : 1;
        $settings['platforms'][$key]['account_url'] = esc_url_raw($settings['platforms'][$key]['account_url']);
        $settings['platforms'][$key]['handle'] = sanitize_text_field($settings['platforms'][$key]['handle']);
        $settings['platforms'][$key]['order'] = max(0, absint($settings['platforms'][$key]['order']));
    }

    return $settings;
}

/**
 * Sort platform definitions using the saved order.
 */
function wqs_get_ordered_social_platforms($context = 'all')
{
    $settings = wqs_get_social_settings();
    $platforms = wqs_get_social_platforms();
    $keys = array_keys($platforms);

    usort($keys, static function ($left, $right) use ($settings) {
        return ($settings['platforms'][$left]['order'] ?? 0) <=> ($settings['platforms'][$right]['order'] ?? 0);
    });

    $ordered = array();
    foreach ($keys as $key) {
        $ordered[$key] = $platforms[$key];
    }
    $platforms = $ordered;

    if ($context === 'account') {
        $platforms = array_filter($platforms, static function ($platform, $key) use ($settings) {
            return !empty($settings['platforms'][$key]['account_enabled'])
                && !empty($settings['platforms'][$key]['account_url']);
        }, ARRAY_FILTER_USE_BOTH);
    } elseif ($context === 'share') {
        $platforms = array_filter($platforms, static function ($platform, $key) use ($settings) {
            return !empty($settings['platforms'][$key]['share_enabled']);
        }, ARRAY_FILTER_USE_BOTH);
    }

    return $platforms;
}

/**
 * Whether frontend social assets are needed.
 */
function wqs_should_load_social_assets()
{
    $settings = wqs_get_social_settings();

    if (is_front_page()) {
        return !empty($settings['home_enabled']) && (bool) wqs_get_ordered_social_platforms('account');
    }

    if (!is_singular()) {
        return false;
    }

    $post_type = get_post_type();
    return ($post_type === 'post' && !empty($settings['share_posts']))
        || ($post_type === 'page' && !empty($settings['share_pages']))
        || ($post_type === 'works' && !empty($settings['share_works']));
}

/**
 * Platform icon or compact brand mark.
 */
function wqs_social_platform_icon($key, $platform)
{
    if (!empty($platform['icon'])) {
        return '<i class="fa-brands ' . esc_attr($platform['icon']) . '" aria-hidden="true"></i>';
    }

    return '<span class="wqs-social-brand-mark" aria-hidden="true">RED</span>';
}

/**
 * Render homepage account links.
 */
function wqs_render_home_social_accounts()
{
    $settings = wqs_get_social_settings();
    $platforms = wqs_get_ordered_social_platforms('account');
    if (empty($settings['home_enabled']) || empty($platforms)) {
        return;
    }

    $heading = wqs_get_current_language() === 'zh'
        ? $settings['home_heading_zh']
        : $settings['home_heading_en'];
    ?>
    <section class="wqs-home-social" aria-labelledby="wqs-home-social-title">
        <header>
            <h2 id="wqs-home-social-title"><?php echo esc_html($heading); ?></h2>
        </header>
        <div class="wqs-home-social__list">
            <?php foreach ($platforms as $key => $platform) : ?>
                <?php $account = $settings['platforms'][$key]; ?>
                <a href="<?php echo esc_url($account['account_url']); ?>" target="_blank" rel="noopener noreferrer me">
                    <span class="wqs-home-social__icon"><?php echo wqs_social_platform_icon($key, $platform); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></span>
                    <span class="wqs-home-social__name"><?php echo esc_html($platform['short_label']); ?></span>
                    <span class="wqs-home-social__handle"><?php echo esc_html($account['handle']); ?></span>
                    <span class="wqs-home-social__arrow" aria-hidden="true">&#8599;</span>
                </a>
            <?php endforeach; ?>
        </div>
    </section>
    <?php
}

/**
 * Build a direct share URL for supported web platforms.
 */
function wqs_get_direct_share_url($platform, $url, $title, $image = '')
{
    if ($platform === 'facebook') {
        return 'https://www.facebook.com/sharer/sharer.php?' . http_build_query(array('u' => $url));
    }

    if ($platform === 'weibo') {
        return 'https://service.weibo.com/share/share.php?' . http_build_query(array(
            'url'   => $url,
            'title' => $title,
            'pic'   => $image,
        ));
    }

    return '';
}

/**
 * Whether sharing is enabled for a post type.
 */
function wqs_is_sharing_enabled_for_post($post_id)
{
    $settings = wqs_get_social_settings();
    $post_type = get_post_type($post_id);

    return ($post_type === 'post' && !empty($settings['share_posts']))
        || ($post_type === 'page' && !empty($settings['share_pages']))
        || ($post_type === 'works' && !empty($settings['share_works']));
}

/**
 * Render default article/page share actions.
 */
function wqs_render_share_controls($post_id = 0)
{
    $post_id = $post_id ?: get_the_ID();
    if (!$post_id || !wqs_is_sharing_enabled_for_post($post_id)) {
        return;
    }

    $settings = wqs_get_social_settings();
    $platforms = wqs_get_ordered_social_platforms('share');
    if (!$platforms) {
        return;
    }

    $url = get_permalink($post_id);
    $title = get_the_title($post_id);
    $thumbnail = wqs_get_archive_thumbnail($post_id, false);
    $image = !empty($thumbnail['url']) ? $thumbnail['url'] : '';
    $quick = array();

    foreach ($platforms as $key => $platform) {
        if (!empty($settings['platforms'][$key]['quick_enabled'])) {
            $quick[$key] = $platform;
        }
        if (count($quick) >= 2) {
            break;
        }
    }
    ?>
    <div class="wqs-share-actions" aria-label="<?php echo esc_attr(wqs_get_current_language() === 'zh' ? '分享' : 'Share'); ?>">
        <?php foreach ($quick as $key => $platform) : ?>
            <?php
            $share_url = wqs_get_direct_share_url($key, $url, $title, $image);
            if ($share_url) :
                ?>
                <a class="wqs-share-action"
                   href="<?php echo esc_url($share_url); ?>"
                   target="_blank"
                   rel="noopener noreferrer"
                   data-wqs-direct-share="<?php echo esc_attr($key); ?>">
                    <?php echo wqs_social_platform_icon($key, $platform); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
                    <span><?php echo esc_html($platform['short_label']); ?></span>
                </a>
            <?php else : ?>
                <button class="wqs-share-action wqs-share-open" type="button" data-platform="<?php echo esc_attr($key); ?>" aria-haspopup="dialog">
                    <?php echo wqs_social_platform_icon($key, $platform); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
                    <span><?php echo esc_html($platform['short_label']); ?></span>
                </button>
            <?php endif; ?>
        <?php endforeach; ?>

        <button class="wqs-share-action wqs-share-open wqs-share-more" type="button" aria-haspopup="dialog">
            <span><?php echo esc_html(wqs_get_current_language() === 'zh' ? '更多' : 'More'); ?></span>
            <span class="wqs-share-more__arrow" aria-hidden="true">&#8599;</span>
        </button>
    </div>
    <?php
}

/**
 * Render one reusable sharing dialog on singular pages.
 */
function wqs_render_share_dialog()
{
    if (!is_singular() || is_front_page()) {
        return;
    }

    $post_id = get_queried_object_id();
    if (!$post_id || !wqs_is_sharing_enabled_for_post($post_id)) {
        return;
    }

    $settings = wqs_get_social_settings();
    $platforms = wqs_get_ordered_social_platforms('share');
    if (!$platforms) {
        return;
    }

    $url = get_permalink($post_id);
    $title = get_the_title($post_id);
    $thumbnail = wqs_get_archive_thumbnail($post_id, true);
    $image = !empty($thumbnail['url']) ? $thumbnail['url'] : '';
    $is_zh = wqs_get_current_language() === 'zh';
    ?>
    <dialog id="wqs-share-dialog" class="wqs-share-dialog"
            data-share-url="<?php echo esc_url($url); ?>"
            data-share-title="<?php echo esc_attr($title); ?>"
            data-qr-enabled="<?php echo empty($settings['qr_fallback']) ? '0' : '1'; ?>"
            aria-labelledby="wqs-share-dialog-title">
        <div class="wqs-share-dialog__surface">
            <header class="wqs-share-dialog__header">
                <div>
                    <span><?php echo esc_html($is_zh ? '分享' : 'Share'); ?></span>
                    <h2 id="wqs-share-dialog-title"><?php echo esc_html($is_zh ? '分享这篇内容' : 'Share this work'); ?></h2>
                </div>
                <button class="wqs-share-dialog__close" type="button" aria-label="<?php echo esc_attr($is_zh ? '关闭' : 'Close'); ?>">&times;</button>
            </header>

            <div class="wqs-share-dialog__preview">
                <img src="<?php echo esc_url($image); ?>" alt="">
                <div>
                    <strong><?php echo esc_html($title); ?></strong>
                    <span><?php echo esc_html(wp_parse_url($url, PHP_URL_HOST)); ?></span>
                </div>
            </div>

            <?php if (!empty($settings['native_share'])) : ?>
                <button type="button" class="wqs-share-native">
                    <span><?php echo esc_html($is_zh ? '使用系统分享' : 'Share…'); ?></span>
                    <span aria-hidden="true">&#8599;</span>
                </button>
            <?php endif; ?>

            <div class="wqs-share-platforms">
                <?php foreach ($platforms as $key => $platform) : ?>
                    <?php $share_url = wqs_get_direct_share_url($key, $url, $title, $image); ?>
                    <button type="button"
                            class="wqs-share-platform"
                            data-platform="<?php echo esc_attr($key); ?>"
                            data-mode="<?php echo esc_attr($share_url ? 'direct' : 'qr'); ?>"
                            data-share-href="<?php echo esc_url($share_url); ?>">
                        <span class="wqs-share-platform__icon"><?php echo wqs_social_platform_icon($key, $platform); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></span>
                        <span><?php echo esc_html($platform['short_label']); ?></span>
                    </button>
                <?php endforeach; ?>
            </div>

            <div class="wqs-share-utilities">
                <button type="button" class="wqs-share-copy">
                    <span aria-hidden="true">&#10697;</span>
                    <span><?php echo esc_html($is_zh ? '复制链接' : 'Copy link'); ?></span>
                </button>
                <?php if (!empty($settings['qr_fallback'])) : ?>
                    <button type="button" class="wqs-share-show-qr">
                        <span class="wqs-qr-mini" aria-hidden="true"></span>
                        <span><?php echo esc_html($is_zh ? '显示二维码' : 'Show QR code'); ?></span>
                    </button>
                <?php endif; ?>
            </div>

            <section class="wqs-share-qr" hidden>
                <button type="button" class="wqs-share-qr__back">&#8592; <?php echo esc_html($is_zh ? '返回' : 'Back'); ?></button>
                <div class="wqs-share-qr__code" aria-hidden="true"></div>
                <h3><?php echo esc_html($is_zh ? '扫码分享' : 'Scan to share'); ?></h3>
                <p><?php echo esc_html($is_zh ? '使用小红书、抖音、微博或其他手机应用扫描。' : 'Scan with Xiaohongshu, Douyin, Weibo, or another mobile app.'); ?></p>
                <button type="button" class="wqs-share-copy wqs-share-copy--wide"><?php echo esc_html($is_zh ? '复制链接' : 'Copy link'); ?></button>
            </section>

            <p class="wqs-share-toast" role="status" aria-live="polite"></p>
        </div>
    </dialog>
    <?php
}
add_action('wp_footer', 'wqs_render_share_dialog', 5);

/**
 * Register the flexible social settings page.
 */
function wqs_register_social_settings_page()
{
    add_submenu_page(
        'wqs-homepage-templates',
        __('Social Media & Sharing', 'wqs-portfolio'),
        __('Social Media & Sharing', 'wqs-portfolio'),
        'edit_theme_options',
        'wqs-social-sharing',
        'wqs_render_social_settings_page'
    );
}
add_action('admin_menu', 'wqs_register_social_settings_page');

/**
 * Load sortable behavior on the social settings screen.
 */
function wqs_social_admin_assets($hook_suffix)
{
    if (strpos((string) $hook_suffix, 'wqs-social-sharing') === false) {
        return;
    }

    wp_enqueue_script('jquery-ui-sortable');
    $script = <<<'JS'
jQuery(function($) {
    var list = $('.wqs-social-admin-platforms');
    list.sortable({
        handle: '.wqs-social-admin-handle',
        axis: 'y',
        update: function() {
            list.children('.wqs-social-admin-row').each(function(index) {
                $(this).find('.wqs-social-order').val((index + 1) * 10);
            });
        }
    });
});
JS;
    wp_add_inline_script('jquery-ui-sortable', $script);
}
add_action('admin_enqueue_scripts', 'wqs_social_admin_assets');

/**
 * Sanitize posted social settings.
 */
function wqs_sanitize_social_settings_input($input)
{
    $defaults = wqs_get_social_default_settings();
    $input = is_array($input) ? $input : array();
    $settings = array();

    foreach (array('home_enabled', 'share_posts', 'share_pages', 'share_works', 'native_share', 'qr_fallback') as $field) {
        $settings[$field] = empty($input[$field]) ? 0 : 1;
    }

    $settings['home_heading_en'] = sanitize_text_field($input['home_heading_en'] ?? $defaults['home_heading_en']);
    $settings['home_heading_zh'] = sanitize_text_field($input['home_heading_zh'] ?? $defaults['home_heading_zh']);
    $settings['platforms'] = array();
    $quick_count = 0;

    foreach (wqs_get_social_platforms() as $key => $platform) {
        $value = isset($input['platforms'][$key]) && is_array($input['platforms'][$key])
            ? $input['platforms'][$key]
            : array();
        $quick_enabled = !empty($value['quick_enabled']) && $quick_count < 2 ? 1 : 0;
        if ($quick_enabled) {
            $quick_count++;
        }

        $settings['platforms'][$key] = array(
            'account_enabled' => empty($value['account_enabled']) ? 0 : 1,
            'share_enabled'   => empty($value['share_enabled']) ? 0 : 1,
            'quick_enabled'   => $quick_enabled,
            'account_url'     => esc_url_raw($value['account_url'] ?? ''),
            'handle'          => sanitize_text_field($value['handle'] ?? ''),
            'order'           => max(0, absint($value['order'] ?? $defaults['platforms'][$key]['order'])),
        );
    }

    return $settings;
}

/**
 * Save and render social settings.
 */
function wqs_render_social_settings_page()
{
    if (!current_user_can('edit_theme_options')) {
        return;
    }

    if (isset($_POST['wqs_social_nonce'])
        && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['wqs_social_nonce'])), 'wqs_save_social_settings')) {
        $input = isset($_POST['wqs_social_settings']) && is_array($_POST['wqs_social_settings'])
            ? wp_unslash($_POST['wqs_social_settings'])
            : array();
        update_option('wqs_social_settings', wqs_sanitize_social_settings_input($input));
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html__('Social media settings saved.', 'wqs-portfolio') . '</p></div>';
    }

    $settings = wqs_get_social_settings();
    $platforms = wqs_get_ordered_social_platforms();
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('Social Media & Sharing', 'wqs-portfolio'); ?></h1>
        <p><?php esc_html_e('Manage artist account links, homepage visibility, article sharing, quick actions, and platform order.', 'wqs-portfolio'); ?></p>

        <form method="post">
            <?php wp_nonce_field('wqs_save_social_settings', 'wqs_social_nonce'); ?>

            <h2><?php esc_html_e('General Display', 'wqs-portfolio'); ?></h2>
            <table class="form-table" role="presentation">
                <tbody>
                    <tr>
                        <th scope="row"><?php esc_html_e('Homepage Accounts', 'wqs-portfolio'); ?></th>
                        <td><label><input type="checkbox" name="wqs_social_settings[home_enabled]" value="1" <?php checked($settings['home_enabled']); ?>> <?php esc_html_e('Show enabled artist accounts on the homepage', 'wqs-portfolio'); ?></label></td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('Homepage Heading', 'wqs-portfolio'); ?></th>
                        <td>
                            <input class="regular-text" type="text" name="wqs_social_settings[home_heading_en]" value="<?php echo esc_attr($settings['home_heading_en']); ?>" placeholder="Follow Wang Qingsong">
                            <input class="regular-text" type="text" name="wqs_social_settings[home_heading_zh]" value="<?php echo esc_attr($settings['home_heading_zh']); ?>" placeholder="关注王庆松">
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('Sharing Locations', 'wqs-portfolio'); ?></th>
                        <td>
                            <label><input type="checkbox" name="wqs_social_settings[share_posts]" value="1" <?php checked($settings['share_posts']); ?>> <?php esc_html_e('Posts', 'wqs-portfolio'); ?></label>&nbsp;&nbsp;
                            <label><input type="checkbox" name="wqs_social_settings[share_pages]" value="1" <?php checked($settings['share_pages']); ?>> <?php esc_html_e('Pages', 'wqs-portfolio'); ?></label>&nbsp;&nbsp;
                            <label><input type="checkbox" name="wqs_social_settings[share_works]" value="1" <?php checked($settings['share_works']); ?>> <?php esc_html_e('Works', 'wqs-portfolio'); ?></label>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php esc_html_e('Share Experience', 'wqs-portfolio'); ?></th>
                        <td>
                            <label><input type="checkbox" name="wqs_social_settings[native_share]" value="1" <?php checked($settings['native_share']); ?>> <?php esc_html_e('Use native mobile share when supported', 'wqs-portfolio'); ?></label><br>
                            <label><input type="checkbox" name="wqs_social_settings[qr_fallback]" value="1" <?php checked($settings['qr_fallback']); ?>> <?php esc_html_e('Enable QR code fallback', 'wqs-portfolio'); ?></label>
                        </td>
                    </tr>
                </tbody>
            </table>

            <h2><?php esc_html_e('Platforms', 'wqs-portfolio'); ?></h2>
            <p><?php esc_html_e('Drag rows to reorder. At most two platforms can be shown as quick actions; all remaining enabled platforms appear under More.', 'wqs-portfolio'); ?></p>

            <div class="wqs-social-admin-platforms" style="max-width:1180px;">
                <?php foreach ($platforms as $key => $platform) : ?>
                    <?php $account = $settings['platforms'][$key]; ?>
                    <div class="wqs-social-admin-row" style="display:grid;grid-template-columns:36px 150px 1fr 180px;gap:16px;align-items:center;padding:16px;margin-bottom:8px;background:#fff;border:1px solid #c3c4c7;">
                        <button type="button" class="wqs-social-admin-handle button" aria-label="<?php esc_attr_e('Drag to reorder', 'wqs-portfolio'); ?>" style="cursor:grab;">&#8597;</button>
                        <strong><?php echo esc_html($platform['short_label']); ?></strong>
                        <div>
                            <input type="url" class="regular-text" name="wqs_social_settings[platforms][<?php echo esc_attr($key); ?>][account_url]" value="<?php echo esc_attr($account['account_url']); ?>" placeholder="https://">
                            <input type="text" name="wqs_social_settings[platforms][<?php echo esc_attr($key); ?>][handle]" value="<?php echo esc_attr($account['handle']); ?>" placeholder="@account">
                        </div>
                        <div>
                            <label><input type="checkbox" name="wqs_social_settings[platforms][<?php echo esc_attr($key); ?>][account_enabled]" value="1" <?php checked($account['account_enabled']); ?>> <?php esc_html_e('Homepage', 'wqs-portfolio'); ?></label><br>
                            <label><input type="checkbox" name="wqs_social_settings[platforms][<?php echo esc_attr($key); ?>][share_enabled]" value="1" <?php checked($account['share_enabled']); ?>> <?php esc_html_e('Share panel', 'wqs-portfolio'); ?></label><br>
                            <label><input type="checkbox" name="wqs_social_settings[platforms][<?php echo esc_attr($key); ?>][quick_enabled]" value="1" <?php checked($account['quick_enabled']); ?>> <?php esc_html_e('Quick action', 'wqs-portfolio'); ?></label>
                            <input class="wqs-social-order" type="hidden" name="wqs_social_settings[platforms][<?php echo esc_attr($key); ?>][order]" value="<?php echo esc_attr($account['order']); ?>">
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>

            <?php submit_button(__('Save Social Settings', 'wqs-portfolio')); ?>
        </form>
    </div>
    <?php
}
