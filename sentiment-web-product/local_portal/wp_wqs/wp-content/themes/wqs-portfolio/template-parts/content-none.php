<?php
/**
 * Template part for displaying "nothing found" content
 *
 * @package WQS_Portfolio
 */

?>

<section class="no-results not-found">
    <header class="page-header">
        <h1 class="page-title"><?php esc_html_e('Nothing Found', 'wqs-portfolio'); ?></h1>
    </header>

    <div class="page-content">
        <?php if (is_home() && current_user_can('publish_posts')) : ?>
            <p><?php
                printf(
                    wp_kses_post(__('Ready to publish your first post? <a href="%1$s">Get started here</a>.', 'wqs-portfolio')),
                    esc_url(admin_url('post-new.php'))
                );
            ?></p>
        <?php elseif (is_search()) : ?>
            <p><?php esc_html_e('Sorry, but nothing matched your search terms. Please try again with some different keywords.', 'wqs-portfolio'); ?></p>
            <?php get_search_form(); ?>
        <?php else : ?>
            <p><?php esc_html_e('It seems we can\'t find what you\'re looking for. Perhaps searching can help.', 'wqs-portfolio'); ?></p>
            <?php get_search_form(); ?>
        <?php endif; ?>
    </div>
</section>