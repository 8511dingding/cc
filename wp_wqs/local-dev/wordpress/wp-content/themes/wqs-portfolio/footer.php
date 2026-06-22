<?php
/**
 * The footer for our theme
 *
 * @package WQS_Portfolio
 * @since 1.0.0
 */

?>

    </div><!-- #content -->

    <footer id="colophon" class="site-footer">
        <div class="site-footer__inner">
            <div class="site-footer__brand">
                <a href="<?php echo esc_url(home_url('/')); ?>">Wang Qingsong</a>
                <span><?php echo wqs_get_current_language() === 'zh' ? '王庆松' : 'Beijing, China'; ?></span>
            </div>

            <nav class="site-footer__nav" aria-label="<?php esc_attr_e('Footer navigation', 'wqs-portfolio'); ?>">
                <?php
                if (has_nav_menu('footer')) {
                    wp_nav_menu(array(
                        'theme_location' => 'footer',
                        'container'      => false,
                        'menu_class'     => 'footer-menu',
                        'depth'          => 1,
                    ));
                } else {
                    $is_zh = wqs_get_current_language() === 'zh';
                    echo '<a href="' . esc_url(home_url($is_zh ? '/zh/biography/' : '/biography/')) . '">' . esc_html($is_zh ? '简历' : 'Biography') . '</a>';
                    echo '<a href="' . esc_url(home_url($is_zh ? '/zh/contact/' : '/contact/')) . '">' . esc_html($is_zh ? '联系' : 'Contact') . '</a>';
                }
                ?>
            </nav>

            <p class="site-footer__copyright">&copy; 1997-<?php echo esc_html(wp_date('Y')); ?>
                <?php
                if (function_exists('pll__')) {
                    echo pll__('Wang Qingsong. All rights reserved.');
                } else {
                    echo 'Wang Qingsong. All rights reserved.';
                }
                ?>
            </p>
        </div>
    </footer>

</div><!-- #page -->

<?php wp_footer(); ?>

</body>
</html>
