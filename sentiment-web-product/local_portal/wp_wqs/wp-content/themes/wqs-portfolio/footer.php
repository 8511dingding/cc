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
        <div class="container">
            <p>&copy; <?php echo date('Y'); ?>
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