<?php
/**
 * The template for displaying single works
 *
 * @package WQS_Portfolio
 * @since 1.0.0
 */

get_header();
?>

<main id="main-content" class="site-main single-works">
    <div class="container">
        <?php while (have_posts()) : the_post(); ?>

            <header class="single-works-header">
                <h1><?php the_title(); ?></h1>
                <?php
                $year_terms = get_the_terms(get_the_ID(), 'works_year');
                if ($year_terms && !is_wp_error($year_terms)) :
                ?>
                    <p class="single-works-year">
                        <?php
                        $years = array();
                        foreach ($year_terms as $term) {
                            $years[] = $term->name;
                        }
                        echo implode(', ', $years);
                        ?>
                    </p>
                <?php endif; ?>
            </header>

            <div class="single-works-content">
                <?php the_content(); ?>

                <?php
                // Get gallery images attached to this post
                $gallery_images = get_attached_media('image', get_the_ID());
                if ($gallery_images && count($gallery_images) > 0) :
                ?>
                    <div class="works-gallery pswp-gallery" id="works-gallery">
                        <?php foreach ($gallery_images as $image) : ?>
                            <?php
                            $full_url = wp_get_attachment_image_url($image->ID, 'large');
                            $thumb_url = wp_get_attachment_image_url($image->ID, 'medium');
                            $image_meta = wp_get_attachment_metadata($image->ID);
                            ?>
                            <div class="works-gallery-item" data-pswp-width="<?php echo esc_attr($image_meta['width'] ??1200); ?>" data-pswp-height="<?php echo esc_attr($image_meta['height'] ?? 800); ?>">
                                <img src="<?php echo esc_url($thumb_url); ?>" data-full-src="<?php echo esc_url($full_url); ?>" alt="<?php echo esc_attr($image->post_excerpt ?: get_the_title()); ?>">
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>

        <?php endwhile; ?>

        <nav class="single-works-nav">
            <?php
            $prev_post = get_previous_post();
            $next_post = get_next_post();
            ?>
            <?php if ($prev_post) : ?>
                <a href="<?php echo get_permalink($prev_post); ?>" class="nav-prev">&larr; <?php echo get_the_title($prev_post); ?></a>
            <?php endif; ?>
            <?php if ($next_post) : ?>
                <a href="<?php echo get_permalink($next_post); ?>" class="nav-next"><?php echo get_the_title($next_post); ?> &rarr;</a>
            <?php endif; ?>
        </nav>
    </div>
</main>

<style>
.single-works-year {
    font-size: 1rem;
    color: var(--wqs-text-light);
    margin-top: var(--wqs-spacing-xs);
}

.single-works-content {
    text-align: center;
}

.works-gallery {
    margin-top: var(--wqs-spacing-lg);
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: var(--wqs-spacing-sm);
}

.works-gallery-item {
    background: var(--wqs-gray-100);
    overflow: hidden;
}

.works-gallery-item img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.works-gallery-item:hover img {
    transform: scale(1.03);
}

.single-works-nav {
    display: flex;
    justify-content: space-between;
    margin-top: var(--wqs-spacing-lg);
    padding-top: var(--wqs-spacing-md);
    border-top: 1px solid var(--wqs-gray-200);
}

.single-works-nav a {
    color: var(--wqs-text);
    font-size: 0.95rem;
}

.single-works-nav a:hover {
    color: var(--wqs-red);
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const gallery = document.getElementById('works-gallery');
    if (gallery && typeof PhotoSwipeLightbox !== 'undefined') {
        const lightbox = new PhotoSwipeLightbox({
            gallery: '#works-gallery',
            children: '.works-gallery-item',
            pswpModule: () => import('https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/umd/photoswipe-lightbox.esm.js'),
            pswpCSS: 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe.css',
        });

        lightbox.addFilter('thumbBounds', (thumbBounds, data, index) => {
            const img = data.element?.querySelector('img');
            if (img) {
                const rect = img.getBoundingClientRect();
                thumbBounds.x = rect.left;
                thumbBounds.y = rect.top;
                thumbBounds.w = rect.width;
                thumbBounds.h = rect.height;
            }
            return thumbBounds;
        });

        lightbox.init();
    }
});
</script>

<?php
get_footer();