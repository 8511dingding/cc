<?php
/**
 * Template for Photography category archive
 *
 * @package WQS_Portfolio
 */

get_header();

$current_lang = function_exists('pll_get_current_language') ? pll_get_current_language() : 'zh';

// Get configured categories from Customizer
$configured_cats = wqs_get_configured_photography_categories();
$show_all = wqs_show_all_categories();
?>

<main id="main-content" class="site-main archive-with-sidebar">
    <div class="archive-layout">
        <aside class="archive-sidebar">
            <nav class="archive-submenu">
                <h3 class="submenu-title"><?php esc_html_e('Photography', 'wqs-portfolio'); ?></h3>
                <ul class="submenu-list">
                    <?php if ($show_all) : ?>
                    <li class="submenu-item">
                        <a href="#" class="submenu-link active" data-year="all" data-category="all">
                            <?php esc_html_e('All', 'wqs-portfolio'); ?>
                        </a>
                    </li>
                    <?php endif; ?>

                    <?php
                    // Get all categories
                    $all_cats = get_categories(array('hide_empty' => true, 'orderby' => 'name'));
                    $photo_categories = array();

                    foreach ($all_cats as $cat) {
                        // If configured, only show those; otherwise show Photography-related
                        if (!empty($configured_cats)) {
                            if (in_array($cat->slug, $configured_cats)) {
                                $photo_categories[$cat->term_id] = $cat;
                            }
                        } else {
                            // Default: Photography categories and year-based
                            if (preg_match('/Photography/i', $cat->name) ||
                                preg_match('/^\d{2,4}\s+Photography/i', $cat->name)) {
                                $photo_categories[$cat->term_id] = $cat;
                            }
                        }
                    }

                    // Sort by year extracted from name (descending)
                    usort($photo_categories, function($a, $b) {
                        preg_match('/(\d{2,4})/', $a->name, $ma);
                        preg_match('/(\d{2,4})/', $b->name, $mb);
                        $ya = isset($ma[1]) ? (strlen($ma[1]) == 2 ? '20' . $ma[1] : $ma[1]) : '9999';
                        $yb = isset($mb[1]) ? (strlen($mb[1]) == 2 ? '20' . $mb[1] : $mb[1]) : '9999';
                        return strcmp($yb, $ya);
                    });

                    foreach ($photo_categories as $cat) :
                        preg_match('/(\d{2,4})/', $cat->name, $matches);
                        $year = isset($matches[1]) ? (strlen($matches[1]) == 2 ? '20' . $matches[1] : $matches[1]) : '';
                    ?>
                    <li class="submenu-item">
                        <a href="#" class="submenu-link" data-year="<?php echo esc_attr($year); ?>" data-category="<?php echo esc_attr($cat->slug); ?>">
                            <?php echo esc_html($cat->name); ?>
                        </a>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </nav>
        </aside>

        <div class="archive-content">
            <header class="archive-header" data-aos="fade-up">
                <h1><?php esc_html_e('Photography', 'wqs-portfolio'); ?></h1>
                <p class="archive-description">
                    <?php esc_html_e('Photography works from 1997 to present', 'wqs-portfolio'); ?>
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
                        $cat_names = array();
                        if ($item_cats) {
                            foreach ($item_cats as $cat) {
                                $cat_slugs[] = $cat->slug;
                                $cat_names[] = $cat->name;
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
                            $thumb_id = get_post_thumbnail_id();
                            $thumb_url = '';
                            $thumb_width = 0;
                            $thumb_height = 0;
                            $is_extreme = false;

                            if ($thumb_id) {
                                $thumb_data = wp_get_attachment_image_src($thumb_id, 'large');
                                if ($thumb_data) {
                                    $thumb_url = $thumb_data[0];
                                    $thumb_width = $thumb_data[1];
                                    $thumb_height = $thumb_data[2];
                                    $is_extreme = wqs_is_extreme_aspect_ratio($thumb_width, $thumb_height);
                                }
                            }

                            // Try to get first image from content if no featured image
                            if (empty($thumb_url)) {
                                $first_image = wqs_get_first_content_image(get_the_ID());
                                if ($first_image && $first_image['url']) {
                                    $thumb_url = $first_image['url'];
                                    $thumb_width = $first_image['width'];
                                    $thumb_height = $first_image['height'];
                                    $is_extreme = wqs_is_extreme_aspect_ratio($thumb_width, $thumb_height);
                                }
                            }

                            if ($thumb_url) {
                                ?>
                                <a href="<?php the_permalink(); ?>">
                                    <img src="<?php echo esc_url($thumb_url); ?>"
                                         alt="<?php echo esc_attr(get_the_title()); ?>"
                                         class="<?php echo $is_extreme ? 'extreme-aspect' : ''; ?>"
                                         loading="lazy">
                                </a>
                            <?php } else { ?>
                                <a href="<?php the_permalink(); ?>">
                                    <img src="https://picsum.photos/800/600?grayscale"
                                         alt="<?php echo esc_attr(get_the_title()); ?>">
                                </a>
                            <?php } ?>
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
                    <?php
                    echo paginate_links(array(
                        'mid_size' => 2,
                        'prev_text' => '&larr;',
                        'next_text' => '&rarr;',
                    ));
                    ?>
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

    var sidebarLinks = document.querySelectorAll('.archive-submenu .submenu-link');
    var archiveItems = document.querySelectorAll('.archive-item');

    function filterItems() {
        var selectedYear = document.querySelector('.archive-submenu .submenu-link.active').getAttribute('data-year');
        var selectedCategory = document.querySelector('.archive-submenu .submenu-link.active').getAttribute('data-category');

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

    sidebarLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            sidebarLinks.forEach(function(l) { l.classList.remove('active'); });
            link.classList.add('active');
            filterItems();
        });
    });
});
</script>

<?php get_footer();