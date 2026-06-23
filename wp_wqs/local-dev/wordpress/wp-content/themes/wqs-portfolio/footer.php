<?php
/**
 * The footer for our theme
 *
 * @package WQS_Portfolio
 * @since 1.0.0
 */

?>

    </div><!-- #content -->

    <?php
    $footer_settings = function_exists('wqs_get_footer_settings') ? wqs_get_footer_settings() : array();
    $footer_is_zh = wqs_get_current_language() === 'zh';
    $footer_brand = $footer_settings[$footer_is_zh ? 'brand_zh' : 'brand_en'] ?? ($footer_is_zh ? '王庆松' : 'Wang Qingsong');
    $footer_address = $footer_settings[$footer_is_zh ? 'address_zh' : 'address_en'] ?? ($footer_is_zh ? '中国，北京' : 'Beijing, China');
    $footer_layout = $footer_settings['address_layout'] ?? 'under';
    $footer_style = sprintf(
        '--wqs-footer-button-size:%dpx;--wqs-footer-copyright-size:%dpx;',
        (int) ($footer_settings['button_font_size'] ?? 16),
        (int) ($footer_settings['copyright_font_size'] ?? 15)
    );
    ?>
    <footer id="colophon" class="site-footer site-footer--address-<?php echo esc_attr($footer_layout); ?>" style="<?php echo esc_attr($footer_style); ?>">
        <div class="site-footer__inner">
            <div class="site-footer__brand">
                <a href="<?php echo esc_url(home_url('/')); ?>"><?php echo esc_html($footer_brand); ?></a>
                <?php if ($footer_layout !== 'bottom') : ?>
                    <span><?php echo esc_html($footer_address); ?></span>
                <?php endif; ?>
            </div>

            <nav class="site-footer__nav" aria-label="<?php esc_attr_e('Footer navigation', 'wqs-portfolio'); ?>">
                <?php
                foreach (array(1, 2) as $button_index) {
                    $label_key = 'button_' . $button_index . '_' . ($footer_is_zh ? 'zh' : 'en');
                    $url_key = 'button_' . $button_index . '_url_' . ($footer_is_zh ? 'zh' : 'en');
                    if (!empty($footer_settings[$label_key]) && !empty($footer_settings[$url_key])) {
                        echo '<a href="' . esc_url($footer_settings[$url_key]) . '">' . esc_html($footer_settings[$label_key]) . '</a>';
                    }
                }
                ?>
            </nav>

            <p class="site-footer__copyright">
                <?php if ($footer_layout === 'bottom') : ?><span class="site-footer__address"><?php echo esc_html($footer_address); ?></span><?php endif; ?>
                &copy; <?php echo esc_html($footer_settings['start_year'] ?? 1997); ?>-<?php echo esc_html(wp_date('Y')); ?>
                <?php echo esc_html($footer_settings[$footer_is_zh ? 'copyright_zh' : 'copyright_en'] ?? 'Wang Qingsong. All rights reserved.'); ?>
            </p>
        </div>
    </footer>

    <?php
    $active_template = function_exists('wqs_get_homepage_template') ? wqs_get_homepage_template() : 'museum-ribbon';
    $active_template_settings = function_exists('wqs_get_site_template_settings')
        ? wqs_get_site_template_settings($active_template)
        : array('scroll_top_enabled' => 1);
    if (!empty($active_template_settings['scroll_top_enabled'])) :
        ?>
        <button class="wqs-back-to-top" type="button" aria-label="<?php echo esc_attr($footer_is_zh ? '返回页面顶部' : 'Back to top'); ?>">
            <span aria-hidden="true">&#8593;</span>
        </button>
    <?php endif; ?>

</div><!-- #page -->

<?php wp_footer(); ?>

</body>
</html>
