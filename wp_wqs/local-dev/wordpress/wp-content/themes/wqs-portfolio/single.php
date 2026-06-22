<?php
/**
 * The template for displaying single posts (works)
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main single-works">
    <div class="container">
        <?php while (have_posts()) : the_post(); ?>

            <header class="single-works-header" data-aos="fade-up">
                <h1><?php the_title(); ?></h1>
                <?php
                $work_year = wqs_get_creation_year(get_the_ID());
                ?>
                <span class="work-year"><?php echo esc_html($work_year); ?></span>
                <?php wqs_render_share_controls(get_the_ID()); ?>
            </header>

            <div class="single-works-content" data-aos="fade-up" data-aos-delay="200">
                <?php the_content(); ?>
            </div>

            <?php wqs_post_navigation(); ?>

        <?php endwhile; ?>
    </div>
</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS
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
