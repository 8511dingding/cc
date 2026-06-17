<?php
/**
 * Generic category archive template.
 *
 * Keeps configured archive sidebars on child category pages.
 *
 * @package WQS_Portfolio
 */

get_header();

$current_term = get_queried_object();
$archive_group = wqs_get_archive_group_for_term($current_term);

if ($archive_group) {
    wqs_render_category_archive($archive_group);
} else {
    ?>
    <main id="main-content" class="site-main works-archive">
        <div class="container">
            <header class="works-archive-header" data-aos="fade-up">
                <h1><?php single_term_title('', true); ?></h1>
                <?php if (term_description()) : ?>
                    <div class="works-archive-description">
                        <?php echo wp_kses_post(term_description()); ?>
                    </div>
                <?php endif; ?>
            </header>

            <?php if (have_posts()) : ?>
                <div class="works-grid">
                    <?php
                    $i = 0;
                    while (have_posts()) :
                        the_post();
                        $i++;
                        wqs_render_archive_grid_item($i);
                    endwhile;
                    ?>
                </div>

                <div class="posts-pagination">
                    <?php echo paginate_links(array('mid_size' => 2, 'prev_text' => '&larr;', 'next_text' => '&rarr;')); ?>
                </div>
            <?php else : ?>
                <p class="no-results"><?php esc_html_e('No works found.', 'wqs-portfolio'); ?></p>
            <?php endif; ?>
        </div>
    </main>
    <?php
    wqs_render_archive_aos_script();
}

get_footer();
