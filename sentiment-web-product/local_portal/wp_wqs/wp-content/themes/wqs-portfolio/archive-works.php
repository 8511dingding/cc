<?php
/**
 * The template for displaying works archive page
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main works-archive">
    <div class="container">
        <header class="works-archive-header">
            <h1><?php single_term_title('', true); ?></h1>
            <p class="works-archive-description">
                <?php esc_html_e('Photography works from 1997 to present', 'wqs-portfolio'); ?>
            </p>
        </header>

        <?php if (have_posts()) : ?>
            <div class="works-grid">
                <?php
                while (have_posts()) : the_post();
                    get_template_part('template-parts/content', 'works');
                endwhile;
                ?>
            </div>

            <?php the_posts_pagination(array(
                'mid_size' => 2,
                'prev_text' => '&larr;',
                'next_text' => '&rarr;',
            )); ?>

        <?php else :
            get_template_part('template-parts/content', 'none');
        endif; ?>
    </div>
</main>

<?php
get_footer();