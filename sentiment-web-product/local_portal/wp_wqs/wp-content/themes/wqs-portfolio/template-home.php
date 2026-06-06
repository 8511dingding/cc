<?php
/**
 * Template Name: Home Page with Slider
 *
 * @package WQS_Portfolio
 * @since 1.0.0
 */

get_header();
?>

<main id="main-content" class="site-main front-page">

    <!-- Homepage Slider -->
    <section class="home-slider">
        <?php echo do_shortcode('[metaslider id="1639"]'); ?>
    </section>

    <!-- Works Section -->
    <section class="section-works">
        <div class="container">
            <header class="section-header">
                <h2 class="section-title">
                    <?php
                    if (function_exists('pll__')) {
                        echo pll__('作品');
                    } else {
                        echo '作品';
                    }
                    ?>
                </h2>
                <p class="section-subtitle">
                    <?php
                    if (function_exists('pll__')) {
                        echo pll__('Photography works from 1997 to present');
                    } else {
                        echo 'Photography works from 1997 to present';
                    }
                    ?>
                </p>
            </header>

            <div class="works-grid">
                <?php
                $works_args = array(
                    'post_type' => 'works',
                    'posts_per_page' => 6,
                    'post_status' => 'publish',
                    'orderby' => 'date',
                    'order' => 'DESC',
                );

                $works_query = new WP_Query($works_args);

                if ($works_query->have_posts()) :
                    while ($works_query->have_posts()) : $works_query->the_post();
                ?>
                        <article id="post-<?php the_ID(); ?>" <?php post_class('works-item'); ?>>
                            <div class="works-item-thumbnail">
                                <?php if (has_post_thumbnail()) : ?>
                                   <a href="<?php the_permalink(); ?>">
                                        <?php the_post_thumbnail('works-thumb'); ?>
                                    </a>
                                <?php else : ?>
                                    <a href="<?php the_permalink(); ?>">
                                        <img src="https://via.placeholder.com/600x450/dbd6aa/333333?text=No+Image" alt="<?php the_title_attribute(); ?>">
                                    </a>
                                <?php endif; ?>
                            </div>
                            <div class="works-item-content">
                                <h3 class="works-item-title">
                                    <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                                </h3>
                                <?php if (has_excerpt()) : ?>
                                    <p class="works-item-excerpt"><?php the_excerpt(); ?></p>
                                <?php endif; ?>
                            </div>
                        </article>
                <?php
                    endwhile;
                    wp_reset_postdata();
                else :
                ?>
                    <p class="no-works">
                        <?php
                        if (function_exists('pll__')) {
                            echo pll__('No works found.');
                        } else {
                            echo 'No works found.';
                        }
                        ?>
                    </p>
                <?php endif; ?>
            </div>

            <div class="section-footer">
                <a href="<?php echo get_post_type_archive_link('works'); ?>" class="btn-view-all">
                    <?php
                    if (function_exists('pll__')) {
                        echo pll__('View All Works');
                    } else {
                        echo 'View All Works';
                    }
                    ?>
                    &rarr;
                </a>
            </div>
        </div>
    </section>

</main>

<style>
.front-page {
    text-align: center;
}

.section-works {
    padding: var(--wqs-spacing-xl) 0;
    background-color: var(--wqs-gray-100);
}

.section-header {
    margin-bottom: var(--wqs-spacing-lg);
}

.section-title {
    font-size: 2.5rem;
    font-family: var(--wqs-font-serif);
    color: var(--wqs-text);
    margin-bottom: var(--wqs-spacing-xs);
}

.section-subtitle {
    font-size: 1.1rem;
    color: var(--wqs-text-light);
    margin-bottom: 0;
}

.section-footer {
    margin-top: var(--wqs-spacing-lg);
}

.btn-view-all {
    display: inline-block;
    padding: 0.75rem 2rem;
    background-color: var(--wqs-red);
    color: var(--wqs-white);
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-radius: 3px;
    transition: background-color 0.2s ease;
}

.btn-view-all:hover {
    background-color: var(--wqs-red-dark);
    color: var(--wqs-white);
    text-decoration: none;
}

.no-works {
    grid-column: 1 / -1;
    text-align: center;
    padding: var(--wqs-spacing-lg);
    color: var(--wqs-text-light);
}
</style>

<?php
get_footer();