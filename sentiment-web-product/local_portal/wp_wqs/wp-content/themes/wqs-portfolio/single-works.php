<?php
/**
 * The template for displaying single works
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main single-works">
    <div class="container">
        <?php while (have_posts()) : the_post(); ?>

            <header class="single-works-header">
                <h1><?php the_title(); ?></h1>
                <?php wqs_post_years(); ?>
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
                            <div class="works-gallery-item"
                                 data-pswp-width="<?php echo esc_attr($image_meta['width'] ?? 1200); ?>"
                                 data-pswp-height="<?php echo esc_attr($image_meta['height'] ?? 800); ?>">
                                <img src="<?php echo esc_url($thumb_url); ?>"
                                     data-full-src="<?php echo esc_url($full_url); ?>"
                                     alt="<?php echo esc_attr($image->post_excerpt ?: get_the_title()); ?>"
                                     loading="lazy">
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>

        <?php endwhile; ?>

        <?php wqs_post_navigation(); ?>
    </div>
</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const gallery = document.getElementById('works-gallery');
    if (gallery && typeof PhotoSwipeLightbox !== 'undefined') {
        const lightbox = new PhotoSwipeLightbox({
            gallery: '#works-gallery',
            children: '.works-gallery-item',
            pswpModule: () => import('https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/umd/photoswipe-lightbox.esm.js'),
            pswpCSS: 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe.css',
            padding: { top: 20, bottom: 20, left: 20, right: 20 },
            zoom: true,
            bgOpacity: 0.9,
            maxWidth: 2000,
            maxHeight: 2000,
        });

        lightbox.on('change', (instance) => {
            const img = instance.currSlide.data.element?.querySelector('img');
            if (img && img.dataset.fullSrc) {
                instance.currSlide.data.src = img.dataset.fullSrc;
            }
        });

        lightbox.init();
    }
});
</script>

<?php
get_footer();