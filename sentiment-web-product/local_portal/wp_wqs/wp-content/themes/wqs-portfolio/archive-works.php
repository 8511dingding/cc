<?php
/**
 * The template for displaying works archive page
 *
 * @package WQS_Portfolio
 * @since 1.0.0
 */

get_header();
?>

<main id="main-content" class="site-main works-archive">
    <div class="container">
        <header class="works-archive-header">
            <h1><?php single_term_title('', true); ?></h1>
            <p class="works-archive-description">
                <?php
                if (function_exists('pll__')) {
                    echo pll__('Photography works from 1997 to present');
                } else {
                    echo 'Photography works from 1997 to present';
                }
                ?>
            </p>
        </header>

        <?php if (have_posts()) : ?>
            <div class="works-grid">
                <?php while (have_posts()) : the_post(); ?>
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
                            <?php
                            $year_terms = get_the_terms(get_the_ID(), 'works_year');
                            if ($year_terms && !is_wp_error($year_terms)) :
                            ?>
                                <p class="works-item-year">
                                    <?php
                                    $years = array();
                                    foreach ($year_terms as $term) {
                                        $years[] = $term->name;
                                    }
                                    echo implode(', ', $years);
                                    ?>
                                </p>
                            <?php endif; ?>
                            <?php if (has_excerpt()) : ?>
                                <p class="works-item-excerpt"><?php the_excerpt(); ?></p>
                            <?php endif; ?>
                        </div>
                    </article>
                <?php endwhile; ?>
            </div>

            <?php
            the_posts_pagination(array(
                'mid_size'  => 2,
                'prev_text' => '&larr;',
                'next_text' => '&rarr;',
            ));
            ?>

        <?php else : ?>
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
</main>

<style>
.works-item-year {
    font-size: 0.85rem;
    color: var(--wqs-text-light);
    margin-bottom: var(--wqs-spacing-xs);
}

.works-archive-description {
    font-size: 1.1rem;
    color: var(--wqs-text-light);
}

.site-main.works-archive {
    padding: var(--wqs-spacing-xl) 0;
}

.site-main.works-archive .works-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}
</style>

<?php
get_footer();