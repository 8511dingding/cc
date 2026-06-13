<?php
/**
 * The front page template file
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main front-page">

    <?php $slider_height = wqs_get_slider_height(); ?>
    <section class="home-slider" style="height: <?php echo esc_attr($slider_height); ?>;">
        <?php echo do_shortcode(wqs_get_slider_shortcode()); ?>
    </section>

    <section class="works-section">
        <div class="container">
            <header class="works-section-header" data-aos="fade-up">
                <h2><?php esc_html_e('Works', 'wqs-portfolio'); ?></h2>
                <p><?php esc_html_e('Photography works from 1997 to present', 'wqs-portfolio'); ?></p>
            </header>

            <div class="works-grid">
                <?php
                $works_args = array(
                    'post_type' => 'post',
                    'posts_per_page' => 8,
                    'post_status' => 'publish',
                    'orderby' => 'date',
                    'order' => 'DESC',
                    'lang' => wqs_get_current_language(),
                );

                $works_query = new WP_Query($works_args);

                if ($works_query->have_posts()) :
                    $i = 0;
                    while ($works_query->have_posts()) : $works_query->the_post();
                        $i++;
                        ?>
                        <article id="post-<?php the_ID(); ?>" <?php post_class('works-item'); ?> data-aos="fade-up" data-aos-delay="<?php echo ($i % 4) * 100; ?>">
                            <div class="works-item-thumbnail">
                                <?php if (has_post_thumbnail()) : ?>
                                    <a href="<?php the_permalink(); ?>">
                                        <?php the_post_thumbnail('large', array('alt' => get_the_title())); ?>
                                    </a>
                                <?php else : ?>
                                    <a href="<?php the_permalink(); ?>">
                                        <img src="https://picsum.photos/800/600?grayscale" alt="<?php echo esc_attr(get_the_title()); ?>">
                                    </a>
                                <?php endif; ?>
                            </div>
                            <div class="works-item-content">
                                <h3 class="works-item-title">
                                    <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                                </h3>
                                <span class="works-item-year"><?php echo get_the_date('Y'); ?></span>
                            </div>
                        </article>
                        <?php
                    endwhile;
                    wp_reset_postdata();
                else :
                    echo '<p class="no-works">' . esc_html__('No works found.', 'wqs-portfolio') . '</p>';
                endif;
                ?>
            </div>

            <div class="section-footer">
                <a href="<?php echo get_post_type_archive_link('post'); ?>" class="btn-view-all">
                    <?php esc_html_e('View All Works', 'wqs-portfolio'); ?> &rarr;
                </a>
            </div>
        </div>
    </section>

</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS if available
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