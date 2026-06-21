<?php
/**
 * Homepage templates, data queries, and admin selector.
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Available homepage templates.
 */
function wqs_get_homepage_templates()
{
    return array(
        'museum-ribbon' => array(
            'label'       => __('Museum Ribbon', 'wqs-portfolio'),
            'description' => __('White museum layout with horizontal artwork rails.', 'wqs-portfolio'),
        ),
        'editorial-index' => array(
            'label'       => __('Editorial Index', 'wqs-portfolio'),
            'description' => __('Art-book typography, indexed sections, and a red footer.', 'wqs-portfolio'),
        ),
        'cinematic-archive' => array(
            'label'       => __('Cinematic Archive', 'wqs-portfolio'),
            'description' => __('Immersive hero, layered galleries, and a dark reviews section.', 'wqs-portfolio'),
        ),
    );
}

/**
 * Sanitize a homepage template key.
 */
function wqs_sanitize_homepage_template($value)
{
    $templates = wqs_get_homepage_templates();
    return isset($templates[$value]) ? $value : 'museum-ribbon';
}

/**
 * Current homepage template.
 */
function wqs_get_homepage_template()
{
    return wqs_sanitize_homepage_template(get_option('wqs_homepage_template', 'museum-ribbon'));
}

/**
 * Add the active homepage template to body classes.
 */
function wqs_homepage_body_class($classes)
{
    if (is_front_page()) {
        $classes[] = 'wqs-home';
        $classes[] = 'wqs-home--' . wqs_get_homepage_template();
    }
    return $classes;
}
add_filter('body_class', 'wqs_homepage_body_class');

/**
 * Homepage labels without depending on untranslated PO files.
 */
function wqs_home_label($key)
{
    $labels = array(
        'en' => array(
            'search_label' => 'Search the archive',
            'search'       => 'Search works, exhibitions and reviews',
            'view_all'     => 'View all',
            'explore'      => 'Explore',
            'read_all'     => 'Read all',
            'photography'  => 'Photography',
            'exhibitions'  => 'Exhibitions',
            'shooting'     => 'Shooting',
            'reviews'      => 'Reviews',
            'reviews_sub'  => 'Essays, interviews and critical writing',
            'biography'    => 'Biography',
            'contact'      => 'Contact',
            'no_content'   => 'No content is available yet.',
        ),
        'zh' => array(
            'search_label' => '搜索档案',
            'search'       => '搜索摄影、展览和评论',
            'view_all'     => '查看全部',
            'explore'      => '浏览全部',
            'read_all'     => '阅读全部',
            'photography'  => '摄影',
            'exhibitions'  => '展览',
            'shooting'     => '工作照',
            'reviews'      => '评论',
            'reviews_sub'  => '文章、访谈与评论',
            'biography'    => '简历',
            'contact'      => '联系',
            'no_content'   => '暂时没有可显示的内容。',
        ),
    );

    $lang = wqs_get_current_language() === 'zh' ? 'zh' : 'en';
    return isset($labels[$lang][$key]) ? $labels[$lang][$key] : $key;
}

/**
 * Get homepage posts for one archive group.
 */
function wqs_get_home_posts($group, $limit = 12)
{
    $term_ids = wqs_get_archive_content_term_ids($group);
    if (empty($term_ids)) {
        return new WP_Query(array('post__in' => array(0)));
    }

    $language_ids = wqs_get_archive_language_post_ids($term_ids, wqs_get_current_language());
    $excluded_ids = wqs_get_archive_landing_post_ids($term_ids);
    $included_ids = array_values(array_diff($language_ids, $excluded_ids));

    return new WP_Query(array(
        'post_type'           => 'post',
        'post_status'         => 'publish',
        'posts_per_page'      => max(1, (int) $limit),
        'ignore_sticky_posts' => true,
        'lang'                => '',
        'post__in'            => !empty($included_ids) ? $included_ids : array(0),
        'meta_key'            => '_wqs_creation_year',
        'orderby'             => array(
            'meta_value_num' => 'DESC',
            'date'           => 'DESC',
        ),
    ));
}

/**
 * URL for one archive group in the current language.
 */
function wqs_get_home_group_url($group)
{
    $term = wqs_get_archive_root_term($group);
    return $term && !is_wp_error($term) ? get_term_link($term) : home_url('/');
}

/**
 * Resolve a usable homepage image.
 */
function wqs_get_home_post_image($post_id)
{
    $image = wqs_get_archive_thumbnail($post_id, true);
    return !empty($image['url']) ? $image['url'] : wqs_get_placeholder_image_url();
}

/**
 * Render the configured slider, with a local post-image fallback.
 */
function wqs_render_home_hero($variant = 'museum')
{
    $slider = trim((string) do_shortcode(wqs_get_slider_shortcode()));
    ?>
    <section class="wqs-home-hero wqs-home-hero--<?php echo esc_attr($variant); ?>" aria-label="<?php esc_attr_e('Featured works', 'wqs-portfolio'); ?>">
        <?php if ($slider !== '') : ?>
            <?php echo $slider; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
        <?php else : ?>
            <?php
            $fallback = wqs_get_home_posts('photography', 1);
            if ($fallback->have_posts()) :
                $fallback->the_post();
                ?>
                <a class="wqs-home-hero__fallback" href="<?php the_permalink(); ?>">
                    <img src="<?php echo esc_url(wqs_get_home_post_image(get_the_ID())); ?>" alt="<?php the_title_attribute(); ?>">
                    <span class="wqs-home-hero__caption">
                        <strong><?php the_title(); ?></strong>
                        <small><?php echo esc_html(wqs_get_creation_year(get_the_ID())); ?></small>
                    </span>
                </a>
                <?php
                wp_reset_postdata();
            endif;
            ?>
        <?php endif; ?>
    </section>
    <?php
}

/**
 * Render homepage search.
 */
function wqs_render_home_search($dark = false)
{
    ?>
    <section class="wqs-home-search<?php echo $dark ? ' is-dark' : ''; ?>">
        <form role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>">
            <label for="wqs-home-search"><?php echo esc_html(wqs_home_label('search_label')); ?></label>
            <div class="wqs-home-search__field">
                <input id="wqs-home-search" type="search" name="s" placeholder="<?php echo esc_attr(wqs_home_label('search')); ?>">
                <button type="submit" aria-label="<?php echo esc_attr(wqs_home_label('search_label')); ?>">&#8594;</button>
            </div>
            <?php if (function_exists('pll_current_language')) : ?>
                <input type="hidden" name="lang" value="<?php echo esc_attr(wqs_get_current_language()); ?>">
            <?php endif; ?>
        </form>
    </section>
    <?php
}

/**
 * Render a horizontal artwork rail.
 */
function wqs_render_home_rail($group, $title, $limit = 12, $number = '')
{
    $query = wqs_get_home_posts($group, $limit);
    $rail_id = 'wqs-rail-' . sanitize_html_class($group) . '-' . wp_rand(100, 999);
    ?>
    <section class="wqs-home-section wqs-home-rail-section wqs-home-section--<?php echo esc_attr($group); ?>">
        <header class="wqs-home-section__header">
            <div>
                <?php if ($number !== '') : ?><span class="wqs-home-section__number"><?php echo esc_html($number); ?></span><?php endif; ?>
                <h2><?php echo esc_html($title); ?></h2>
            </div>
            <a href="<?php echo esc_url(wqs_get_home_group_url($group)); ?>"><?php echo esc_html(wqs_home_label('view_all')); ?> &#8594;</a>
        </header>

        <?php if ($query->have_posts()) : ?>
            <div class="wqs-home-rail__controls">
                <button type="button" data-rail-target="<?php echo esc_attr($rail_id); ?>" data-direction="-1" aria-label="<?php esc_attr_e('Previous items', 'wqs-portfolio'); ?>">&#8592;</button>
                <button type="button" data-rail-target="<?php echo esc_attr($rail_id); ?>" data-direction="1" aria-label="<?php esc_attr_e('Next items', 'wqs-portfolio'); ?>">&#8594;</button>
            </div>
            <div id="<?php echo esc_attr($rail_id); ?>" class="wqs-home-rail" tabindex="0">
                <?php while ($query->have_posts()) : $query->the_post(); ?>
                    <article class="wqs-home-card">
                        <a class="wqs-home-card__image" href="<?php the_permalink(); ?>">
                            <img src="<?php echo esc_url(wqs_get_home_post_image(get_the_ID())); ?>" alt="<?php the_title_attribute(); ?>" loading="lazy">
                        </a>
                        <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                        <span><?php echo esc_html(wqs_get_creation_year(get_the_ID())); ?></span>
                    </article>
                <?php endwhile; ?>
            </div>
            <div class="wqs-home-rail__progress"><span></span></div>
        <?php else : ?>
            <p><?php echo esc_html(wqs_home_label('no_content')); ?></p>
        <?php endif; ?>
        <?php wp_reset_postdata(); ?>
    </section>
    <?php
}

/**
 * Render six shooting posts.
 */
function wqs_render_home_shooting($number = '')
{
    $query = wqs_get_home_posts('shooting', 6);
    ?>
    <section class="wqs-home-section wqs-home-shooting">
        <header class="wqs-home-section__header">
            <div>
                <?php if ($number !== '') : ?><span class="wqs-home-section__number"><?php echo esc_html($number); ?></span><?php endif; ?>
                <h2><?php echo esc_html(wqs_home_label('shooting')); ?></h2>
            </div>
            <a href="<?php echo esc_url(wqs_get_home_group_url('shooting')); ?>"><?php echo esc_html(wqs_home_label('view_all')); ?> &#8594;</a>
        </header>
        <div class="wqs-home-shooting__grid">
            <?php while ($query->have_posts()) : $query->the_post(); ?>
                <article>
                    <a href="<?php the_permalink(); ?>">
                        <img src="<?php echo esc_url(wqs_get_home_post_image(get_the_ID())); ?>" alt="<?php the_title_attribute(); ?>" loading="lazy">
                    </a>
                    <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                    <span><?php echo esc_html(wqs_get_creation_year(get_the_ID())); ?></span>
                </article>
            <?php endwhile; ?>
        </div>
        <?php wp_reset_postdata(); ?>
    </section>
    <?php
}

/**
 * Render a compact reviews list.
 */
function wqs_render_home_reviews($number = '', $dark = false)
{
    $query = wqs_get_home_posts('reviews', 6);
    ?>
    <section class="wqs-home-section wqs-home-reviews<?php echo $dark ? ' is-dark' : ''; ?>">
        <header class="wqs-home-section__header">
            <div>
                <?php if ($number !== '') : ?><span class="wqs-home-section__number"><?php echo esc_html($number); ?></span><?php endif; ?>
                <h2><?php echo esc_html(wqs_home_label('reviews')); ?></h2>
                <p><?php echo esc_html(wqs_home_label('reviews_sub')); ?></p>
            </div>
            <a href="<?php echo esc_url(wqs_get_home_group_url('reviews')); ?>"><?php echo esc_html(wqs_home_label('read_all')); ?> &#8594;</a>
        </header>
        <div class="wqs-home-reviews__list">
            <?php while ($query->have_posts()) : $query->the_post(); ?>
                <article>
                    <span><?php echo esc_html(wqs_get_creation_year(get_the_ID())); ?></span>
                    <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                    <a class="wqs-home-reviews__arrow" href="<?php the_permalink(); ?>" aria-label="<?php the_title_attribute(); ?>">&#8594;</a>
                </article>
            <?php endwhile; ?>
        </div>
        <?php wp_reset_postdata(); ?>
    </section>
    <?php
}

/**
 * Register the Customizer selector.
 */
function wqs_register_homepage_design_customizer($wp_customize)
{
    $wp_customize->add_section('wqs_homepage_design', array(
        'title'    => __('Homepage Design', 'wqs-portfolio'),
        'priority' => 29,
    ));
    $wp_customize->add_setting('wqs_homepage_template', array(
        'type'              => 'option',
        'default'           => 'museum-ribbon',
        'sanitize_callback' => 'wqs_sanitize_homepage_template',
        'transport'         => 'refresh',
    ));
    $choices = array();
    foreach (wqs_get_homepage_templates() as $key => $template) {
        $choices[$key] = $template['label'];
    }
    $wp_customize->add_control('wqs_homepage_template', array(
        'label'       => __('Homepage Template', 'wqs-portfolio'),
        'description' => __('Choose one of the three WQS homepage designs.', 'wqs-portfolio'),
        'section'     => 'wqs_homepage_design',
        'type'        => 'radio',
        'choices'     => $choices,
    ));
}
add_action('customize_register', 'wqs_register_homepage_design_customizer');

/**
 * Add Appearance > Homepage Templates.
 */
function wqs_add_homepage_template_admin_page()
{
    add_theme_page(
        __('Homepage Templates', 'wqs-portfolio'),
        __('Homepage Templates', 'wqs-portfolio'),
        'edit_theme_options',
        'wqs-homepage-templates',
        'wqs_render_homepage_template_admin_page'
    );
}
add_action('admin_menu', 'wqs_add_homepage_template_admin_page');

/**
 * Save and render the homepage selector.
 */
function wqs_render_homepage_template_admin_page()
{
    if (!current_user_can('edit_theme_options')) {
        return;
    }

    if (isset($_POST['wqs_homepage_template_nonce'])
        && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['wqs_homepage_template_nonce'])), 'wqs_save_homepage_template')) {
        $template = isset($_POST['wqs_homepage_template'])
            ? wqs_sanitize_homepage_template(sanitize_key(wp_unslash($_POST['wqs_homepage_template'])))
            : 'museum-ribbon';
        update_option('wqs_homepage_template', $template);
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html__('Homepage template saved.', 'wqs-portfolio') . '</p></div>';
    }

    $current = wqs_get_homepage_template();
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('WQS Homepage Templates', 'wqs-portfolio'); ?></h1>
        <p><?php esc_html_e('Switching templates changes only the homepage presentation. All templates use the same posts, categories, slider, and media library.', 'wqs-portfolio'); ?></p>
        <form method="post">
            <?php wp_nonce_field('wqs_save_homepage_template', 'wqs_homepage_template_nonce'); ?>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;max-width:1100px;margin:24px 0;">
                <?php foreach (wqs_get_homepage_templates() as $key => $template) : ?>
                    <label style="display:block;background:#fff;border:<?php echo $current === $key ? '2px solid #2271b1' : '1px solid #c3c4c7'; ?>;padding:20px;cursor:pointer;">
                        <input type="radio" name="wqs_homepage_template" value="<?php echo esc_attr($key); ?>" <?php checked($current, $key); ?>>
                        <strong style="display:block;font-size:18px;margin:12px 0 6px;"><?php echo esc_html($template['label']); ?></strong>
                        <span><?php echo esc_html($template['description']); ?></span>
                    </label>
                <?php endforeach; ?>
            </div>
            <?php submit_button(__('Save Homepage Template', 'wqs-portfolio')); ?>
        </form>
    </div>
    <?php
}
