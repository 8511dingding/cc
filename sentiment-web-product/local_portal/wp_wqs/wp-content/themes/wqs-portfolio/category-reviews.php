<?php
/**
 * Template for Reviews category archive - simple list
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main reviews-archive">
    <div class="container">
        <header class="reviews-archive-header" data-aos="fade-up">
            <h1><?php esc_html_e('Reviews', 'wqs-portfolio'); ?></h1>
            <p class="works-archive-description">
                <?php esc_html_e('Press and media coverage', 'wqs-portfolio'); ?>
            </p>
        </header>

        <?php if (have_posts()) : ?>
            <div class="reviews-list" data-aos="fade-up" data-aos-delay="200">
                <?php
                while (have_posts()) : the_post();
                ?>
                <article id="post-<?php the_ID(); ?>" <?php post_class('review-item'); ?>>
                    <div class="review-date"><?php echo get_the_date('Y.m.d'); ?></div>
                    <h2 class="review-title">
                        <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                    </h2>
                </article>
                <?php
                endwhile;
                ?>
            </div>

            <div class="posts-pagination">
                <?php echo paginate_links(array('mid_size' => 2, 'prev_text' => '&larr;', 'next_text' => '&rarr;')); ?>
            </div>
        <?php else :
            echo '<p class="no-results">' . esc_html__('No reviews found.', 'wqs-portfolio') . '</p>';
        endif; ?>
    </div>
</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 800, easing: 'ease-out-cubic', once: true, offset: 50 });
    }
});
</script>

<?php get_footer();