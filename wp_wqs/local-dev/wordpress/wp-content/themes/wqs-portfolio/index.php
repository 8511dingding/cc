<?php
/**
 * The main template file - serves as works archive
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main works-archive">
    <div class="container">
        <header class="works-archive-header" data-aos="fade-up">
            <h1><?php single_term_title('', true); ?></h1>
            <p class="works-archive-description">
                <?php esc_html_e('Photography works from 1997 to present', 'wqs-portfolio'); ?>
            </p>
        </header>

        <?php if (have_posts()) : ?>
            <div class="works-grid">
                <?php
                $i = 0;
                while (have_posts()) : the_post();
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
                ?>
            </div>

            <div class="posts-pagination">
                <?php
                echo paginate_links(array(
                    'mid_size' => 2,
                    'prev_text' => '&larr;',
                    'next_text' => '&rarr;',
                ));
                ?>
            </div>

        <?php else :
            echo '<p class="no-results">' . esc_html__('No works found.', 'wqs-portfolio') . '</p>';
        endif; ?>
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