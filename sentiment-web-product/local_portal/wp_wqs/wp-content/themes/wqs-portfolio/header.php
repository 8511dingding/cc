<?php
/**
 * The header for our theme
 *
 * @package WQS_Portfolio
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
        <?php esc_html_e('Skip to content', 'wqs-portfolio'); ?>
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
                            <?php bloginfo('name'); ?>
                        </a>
                    </h1>
                <?php endif; ?>
            </div>

            <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
                <span class="screen-reader-text"><?php esc_html_e('Menu', 'wqs-portfolio'); ?></span>
                <span class="menu-icon"></span>
            </button>

            <nav id="site-navigation" class="main-navigation">
                <?php
                // Use primary menu location - Polylang handles translations automatically
                wp_nav_menu(array(
                    'theme_location' => 'primary',
                    'menu_id' => 'primary-menu',
                    'container' => false,
                    'fallback_cb' => function() {
                        echo '<ul id="primary-menu" class="nav-menu">';
                        echo '<li><a href="' . esc_url(home_url('/')) . '">Works</a></li>';
                        echo '<li><a href="#">Biography</a></li>';
                        echo '<li><a href="#">Contact</a></li>';
                        echo '</ul>';
                    },
                ));
                ?>

                <div class="header-right">
                    <?php echo wqs_language_switcher(); ?>
                </div>
            </nav>
        </div>
    </header>

    <div id="content" class="site-content">