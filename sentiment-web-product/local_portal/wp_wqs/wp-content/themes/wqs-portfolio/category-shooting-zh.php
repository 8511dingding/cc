<?php
/**
 * Template for Shooting (Behind the Scenes) category archive
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main archive-with-sidebar">
    <div class="archive-layout">
        <aside class="archive-sidebar">
            <nav class="archive-submenu">
                <h3 class="submenu-title"><?php esc_html_e('Shooting', 'wqs-portfolio'); ?></h3>
                <ul class="submenu-list">
                    <li class="submenu-item">
                        <a href="#" class="submenu-link active" data-year="all">
                            <?php esc_html_e('All', 'wqs-portfolio'); ?>
                        </a>
                    </li>
                    <?php
                    global $wp_query;
                    $years = array();

                    if (have_posts()) {
                        while (have_posts()) {
                            the_post();
                            $year = get_the_date('Y');
                            if (!in_array($year, $years)) {
                                $years[] = $year;
                            }
                        }
                        rewind_posts();
                    }

                    sort($years, SORT_NUMERIC);

                    foreach ($years as $year) :
                    ?>
                    <li class="submenu-item">
                        <a href="#" class="submenu-link" data-year="<?php echo esc_attr($year); ?>">
                            <?php echo esc_html($year); ?>
                        </a>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </nav>
        </aside>

        <div class="archive-content">
            <header class="archive-header" data-aos="fade-up">
                <h1><?php esc_html_e('Shooting', 'wqs-portfolio'); ?></h1>
                <p class="archive-description">
                    <?php esc_html_e('Behind the scenes', 'wqs-portfolio'); ?>
                </p>
            </header>

            <?php if (have_posts()) : ?>
                <div class="works-grid archive-grid">
                    <?php
                    $i = 0;
                    while (have_posts()) : the_post();
                        $i++;
                        $post_year = get_the_date('Y');
                    ?>
                    <article id="post-<?php the_ID(); ?>" <?php post_class('works-item archive-item'); ?>
                             data-aos="fade-up"
                             data-aos-delay="<?php echo ($i % 4) * 100; ?>"
                             data-year="<?php echo esc_attr($post_year); ?>">
                        <div class="works-item-thumbnail">
                            <?php if (has_post_thumbnail()) : ?>
                                <a href="<?php the_permalink(); ?>">
                                    <?php the_post_thumbnail('large', array('alt' => esc_attr(get_the_title()))); ?>
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
                            <span class="works-item-year"><?php echo esc_html($post_year); ?></span>
                        </div>
                    </article>
                    <?php endwhile; ?>
                </div>

                <div class="posts-pagination">
                    <?php echo paginate_links(array('mid_size' => 2, 'prev_text' => '&larr;', 'next_text' => '&rarr;')); ?>
                </div>
            <?php else :
                echo '<p class="no-results">' . esc_html__('No works found.', 'wqs-portfolio') . '</p>';
            endif; ?>
        </div>
    </div>
</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 800, easing: 'ease-out-cubic', once: true, offset: 50 });
    }
    var submenuLinks = document.querySelectorAll('.submenu-link');
    var archiveItems = document.querySelectorAll('.archive-item');
    submenuLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            submenuLinks.forEach(function(l) { l.classList.remove('active'); });
            link.classList.add('active');
            var selectedYear = link.getAttribute('data-year');
            archiveItems.forEach(function(item) {
                item.style.display = (selectedYear === 'all' || item.getAttribute('data-year') === selectedYear) ? '' : 'none';
            });
        });
    });
});
</script>

<?php get_footer();