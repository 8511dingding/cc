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
                <span class="work-year"><?php echo get_the_date('Y'); ?></span>
            </header>

            <div class="single-works-content" data-aos="fade-up" data-aos-delay="200">
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

            <?php wqs_post_navigation(); ?>

            <?php
            // Bilingual content section
            $current_lang = wqs_get_current_language();
            $chinese_content = get_post_meta(get_the_ID(), 'chinese_content', true);
            $chinese_title = get_post_meta(get_the_ID(), 'chinese_title', true);
            ?>

            <?php if ($chinese_content && $current_lang === 'en') : ?>
            <div class="bilingual-toggle" data-aos="fade-up">
                <button type="button" id="toggle-chinese" class="btn-toggle-chinese">
                    <?php esc_html_e('Show Chinese Version', 'wqs-portfolio'); ?>
                </button>
            </div>
            <div class="chinese-version" id="chinese-version" style="display: none;">
                <h2 class="chinese-title"><?php echo esc_html($chinese_title ?: __('Chinese Version', 'wqs-portfolio')); ?></h2>
                <div class="chinese-content">
                    <?php echo apply_filters('the_content', wp_kses_post($chinese_content)); ?>
                </div>
            </div>
            <?php endif; ?>

            <?php if ($current_lang === 'zh' && $chinese_content) : ?>
            <div class="chinese-version" data-aos="fade-up">
                <h2 class="chinese-title"><?php echo esc_html($chinese_title ?: __('Chinese Version', 'wqs-portfolio')); ?></h2>
                <div class="chinese-content">
                    <?php echo apply_filters('the_content', wp_kses_post($chinese_content)); ?>
                </div>
            </div>
            <?php endif; ?>

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

    // Initialize PhotoSwipe Lightbox
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

    // Bilingual toggle
    var toggleBtn = document.getElementById('toggle-chinese');
    var chineseVersion = document.getElementById('chinese-version');

    if (toggleBtn && chineseVersion) {
        toggleBtn.addEventListener('click', function() {
            if (chineseVersion.style.display === 'none') {
                chineseVersion.style.display = 'block';
                toggleBtn.textContent = '<?php esc_html_e('Hide Chinese Version', 'wqs-portfolio'); ?>';
            } else {
                chineseVersion.style.display = 'none';
                toggleBtn.textContent = '<?php esc_html_e('Show Chinese Version', 'wqs-portfolio'); ?>';
            }
        });
    }
});
</script>

<?php
get_footer();