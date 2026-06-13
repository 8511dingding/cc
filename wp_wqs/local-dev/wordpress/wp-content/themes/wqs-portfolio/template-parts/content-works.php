<?php
/**
 * Template part for displaying works content
 *
 * @package WQS_Portfolio
 */

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
        <header class="works-item-header">
            <h3 class="works-item-title">
                <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
            </h3>
        </header>
        <?php wqs_post_years(); ?>
        <?php if (has_excerpt()) : ?>
            <div class="works-item-excerpt">
                <?php the_excerpt(); ?>
            </div>
        <?php endif; ?>
    </div>
</article>