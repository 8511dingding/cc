<?php
/**
 * The header for our theme
 *
 * @package WQS_Portfolio
 * @since 1.0.0
 */

?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">
    <a class="skip-link screen-reader-text" href="#main-content">
        <?php
        if (function_exists('pll__')) {
            echo pll__('Skip to content');
        } else {
            echo 'Skip to content';
        }
        ?>
    </a>

    <header id="masthead" class="site-header">
        <div class="header-inner">
            <div class="site-branding">
                <?php
                if (has_custom_logo()) :
                    the_custom_logo();
                else :
                ?>
                    <h1 class="site-logo">
                        <a href="<?php echo esc_url(home_url('/')); ?>" rel="home">
                            <?php
                            if (function_exists('pll__')) {
                                echo pll__('Wang Qingsong');
                            } else {
                                bloginfo('name');
                            }
                            ?>
                        </a>
                    </h1>
                <?php endif; ?>
            </div>

            <nav id="site-navigation" class="main-navigation">
                <?php
                // Get current language and select appropriate menu
                $current_lang = function_exists('pll_current_language') ? pll_current_language() : 'en';
                $menu_name = ($current_lang === 'zh') ? 'Main Navigation ZH' : 'Main Navigation EN';

                wp_nav_menu(array(
                    'menu' => $menu_name,
                    'menu_id'        => 'primary-menu',
                    'container'      => false,
                    'fallback_cb'    => false,
                ));
                ?>

                <?php echo wqs_get_language_switcher(); ?>
            </nav>
        </div>
    </header>

    <div id="content" class="site-content">