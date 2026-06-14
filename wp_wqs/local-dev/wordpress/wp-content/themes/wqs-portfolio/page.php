<?php
/**
 * The template for displaying static pages (Biography, Contact, etc.)
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main page-content">
    <div class="container">
        <?php while (have_posts()) : the_post(); ?>

            <header class="page-header" data-aos="fade-up">
                <h1><?php the_title(); ?></h1>
            </header>

            <div class="page-body" data-aos="fade-up" data-aos-delay="200">
                <?php the_content(); ?>
            </div>

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
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 50
        });
    }

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