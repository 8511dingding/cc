<?php
/**
 * Template for Video category archive
 *
 * @package WQS_Portfolio
 */

get_header();
?>

<main id="main-content" class="site-main archive-with-sidebar">
    <div class="archive-layout">
        <aside class="archive-sidebar">
            <nav class="archive-submenu">
                <h3 class="submenu-title"><?php esc_html_e('Video', 'wqs-portfolio'); ?></h3>
                <ul class="submenu-list">
                    <li class="submenu-item">
                        <a href="#" class="submenu-link active" data-year="all">
                            <?php esc_html_e('All', 'wqs-portfolio'); ?>
                        </a>
                    </li>
                    <?php
                    global $wp_query;
                    $years = array();
                    $post_categories = array();

                    if (have_posts()) {
                        while (have_posts()) {
                            the_post();
                            $year = get_the_date('Y');
                            if (!in_array($year, $years)) {
                                $years[] = $year;
                            }
                            $cats = get_the_category();
                            if ($cats) {
                                foreach ($cats as $cat) {
                                    if (!isset($post_categories[$cat->term_id])) {
                                        $post_categories[$cat->term_id] = $cat;
                                    }
                                }
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

            <?php if (!empty($post_categories)) : ?>
            <nav class="archive-submenu archive-categories">
                <h3 class="submenu-title"><?php esc_html_e('Categories', 'wqs-portfolio'); ?></h3>
                <ul class="submenu-list">
                    <li class="submenu-item">
                        <a href="#" class="submenu-link active" data-category="all">
                            <?php esc_html_e('All', 'wqs-portfolio'); ?>
                        </a>
                    </li>
                    <?php foreach ($post_categories as $cat) : ?>
                    <li class="submenu-item">
                        <a href="#" class="submenu-link" data-category="<?php echo esc_attr($cat->slug); ?>">
                            <?php echo esc_html($cat->name); ?>
                        </a>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </nav>
            <?php endif; ?>
        </aside>

        <div class="archive-content">
            <header class="archive-header" data-aos="fade-up">
                <h1><?php esc_html_e('Video', 'wqs-portfolio'); ?></h1>
                <p class="archive-description">
                    <?php esc_html_e('Video works', 'wqs-portfolio'); ?>
                </p>
            </header>

            <?php if (have_posts()) : ?>
                <div class="works-grid archive-grid">
                    <?php
                    $i = 0;
                    while (have_posts()) : the_post();
                        $i++;
                        $post_year = get_the_date('Y');
                        $item_cats = get_the_category();
                        $cat_slugs = array();
                        if ($item_cats) {
                            foreach ($item_cats as $cat) {
                                $cat_slugs[] = $cat->slug;
                            }
                        }
                        $cat_data = implode(',', $cat_slugs);
                    ?>
                    <article id="post-<?php the_ID(); ?>" <?php post_class('works-item archive-item'); ?>
                             data-aos="fade-up"
                             data-aos-delay="<?php echo ($i % 4) * 100; ?>"
                             data-year="<?php echo esc_attr($post_year); ?>"
                             data-categories="<?php echo esc_attr($cat_data); ?>">
                        <div class="works-item-thumbnail">
                            <?php
                            if (has_post_thumbnail()) {
                                $thumb_id = get_post_thumbnail_id();
                                $thumb_data = wp_get_attachment_image_src($thumb_id, 'large');
                                $is_extreme = wqs_is_extreme_aspect_ratio($thumb_data[1], $thumb_data[2]);
                                ?>
                                <a href="<?php the_permalink(); ?>">
                                    <?php the_post_thumbnail('large', array('alt' => esc_attr(get_the_title()), 'class' => $is_extreme ? 'extreme-aspect' : '')); ?>
                                </a>
                            <?php } else {
                                $first_image = wqs_get_first_content_image(get_the_ID());
                                if ($first_image && $first_image['url']) {
                                    $is_extreme = wqs_is_extreme_aspect_ratio($first_image['width'], $first_image['height']);
                                    ?>
                                    <a href="<?php the_permalink(); ?>">
                                        <img src="<?php echo esc_url($first_image['url']); ?>"
                                             alt="<?php echo esc_attr(get_the_title()); ?>"
                                             class="<?php echo $is_extreme ? 'extreme-aspect' : ''; ?>">
                                    </a>
                                <?php } else { ?>
                                    <a href="<?php the_permalink(); ?>">
                                        <img src="https://picsum.photos/800/600?grayscale" alt="<?php echo esc_attr(get_the_title()); ?>">
                                    </a>
                                <?php }
                            } ?>
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
                echo '<p class="no-results">' . esc_html__('No videos found.', 'wqs-portfolio') . '</p>';
            endif; ?>
        </div>
    </div>
</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 800, easing: 'ease-out-cubic', once: true, offset: 50 });
    }

    var yearLinks = document.querySelectorAll('.archive-submenu:first-of-type .submenu-link');
    var categoryLinks = document.querySelectorAll('.archive-categories .submenu-link');
    var archiveItems = document.querySelectorAll('.archive-item');

    function filterItems() {
        var selectedYear = document.querySelector('.archive-submenu:first-of-type .submenu-link.active').getAttribute('data-year');
        var selectedCategory = document.querySelector('.archive-categories .submenu-link.active').getAttribute('data-category');

        archiveItems.forEach(function(item) {
            var itemYear = item.getAttribute('data-year');
            var itemCategories = item.getAttribute('data-categories');

            var yearMatch = (selectedYear === 'all' || itemYear === selectedYear);
            var categoryMatch = (selectedCategory === 'all' || (itemCategories && itemCategories.split(',').includes(selectedCategory)));

            if (yearMatch && categoryMatch) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });

        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
    }

    yearLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            yearLinks.forEach(function(l) { l.classList.remove('active'); });
            link.classList.add('active');
            filterItems();
        });
    });

    categoryLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            categoryLinks.forEach(function(l) { l.classList.remove('active'); });
            link.classList.add('active');
            filterItems();
        });
    });
});
</script>

<?php get_footer();