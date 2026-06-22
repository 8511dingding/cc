<?php
/**
 * The template for displaying static pages (Biography, Contact, etc.)
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main page-content">
    <div class="container">
        <?php while (have_posts()) : the_post(); ?>

            <header class="page-header" data-aos="fade-up">
                <h1><?php the_title(); ?></h1>
                <?php wqs_render_share_controls(get_the_ID()); ?>
            </header>

            <div class="page-body" data-aos="fade-up" data-aos-delay="200">
                <?php the_content(); ?>
            </div>

        <?php endwhile; ?>
    </div>
</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 50
        });
    }

});
</script>

<?php
get_footer();
