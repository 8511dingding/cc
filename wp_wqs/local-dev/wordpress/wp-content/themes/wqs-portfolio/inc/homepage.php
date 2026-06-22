<?php
/**
 * Site templates, homepage data queries, and admin selector.
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Available site templates.
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
 * Sanitize a site template key.
 */
function wqs_sanitize_homepage_template($value)
{
    $templates = wqs_get_homepage_templates();
    return isset($templates[$value]) ? $value : 'museum-ribbon';
}

/**
 * Current site template.
 */
function wqs_get_homepage_template()
{
    return wqs_sanitize_homepage_template(get_option('wqs_homepage_template', 'museum-ribbon'));
}

/**
 * Default visual settings for each complete site template.
 */
function wqs_get_site_template_default_settings($template)
{
    $defaults = array(
        'museum-ribbon' => array(
            'background'    => '#f7f7f4',
            'panel'         => '#ffffff',
            'text'          => '#151515',
            'muted'         => '#6d6d68',
            'border'        => '#d2d2cc',
            'accent'        => '#8f2018',
            'body_font'     => 'inter',
            'heading_font'  => 'playfair',
            'base_size'     => 17,
            'nav_size'      => 16,
            'heading_scale' => 100,
        ),
        'editorial-index' => array(
            'background'    => '#f2f0eb',
            'panel'         => '#ffffff',
            'text'          => '#111111',
            'muted'         => '#66645f',
            'border'        => '#aaa7a0',
            'accent'        => '#a52318',
            'body_font'     => 'inter',
            'heading_font'  => 'playfair',
            'base_size'     => 17,
            'nav_size'      => 16,
            'heading_scale' => 108,
        ),
        'cinematic-archive' => array(
            'background'    => '#f3f3ef',
            'panel'         => '#ffffff',
            'text'          => '#111111',
            'muted'         => '#6a6a66',
            'border'        => '#cacac4',
            'accent'        => '#98251b',
            'body_font'     => 'inter',
            'heading_font'  => 'playfair',
            'base_size'     => 17,
            'nav_size'      => 16,
            'heading_scale' => 104,
        ),
    );

    $template = wqs_sanitize_homepage_template($template);
    return $defaults[$template];
}

/**
 * Available font stacks for template settings.
 */
function wqs_get_site_template_font_choices()
{
    return array(
        'inter' => array(
            'label' => 'Inter',
            'stack' => "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        ),
        'system' => array(
            'label' => __('System Sans', 'wqs-portfolio'),
            'stack' => "-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif",
        ),
        'helvetica' => array(
            'label' => 'Helvetica / Arial',
            'stack' => "'Helvetica Neue', Helvetica, Arial, sans-serif",
        ),
        'playfair' => array(
            'label' => 'Playfair Display',
            'stack' => "'Playfair Display', Georgia, 'Times New Roman', serif",
        ),
        'georgia' => array(
            'label' => 'Georgia',
            'stack' => "Georgia, 'Times New Roman', serif",
        ),
        'noto-serif' => array(
            'label' => 'Noto Serif / Songti',
            'stack' => "'Noto Serif SC', 'Songti SC', SimSun, Georgia, serif",
        ),
    );
}

/**
 * Return sanitized per-template visual settings.
 */
function wqs_get_site_template_settings($template)
{
    $template = wqs_sanitize_homepage_template($template);
    $defaults = wqs_get_site_template_default_settings($template);
    $stored = get_option('wqs_site_template_settings_' . $template, array());
    $settings = wp_parse_args(is_array($stored) ? $stored : array(), $defaults);

    foreach (array('background', 'panel', 'text', 'muted', 'border', 'accent') as $field) {
        $settings[$field] = sanitize_hex_color($settings[$field]) ?: $defaults[$field];
    }

    $fonts = wqs_get_site_template_font_choices();
    foreach (array('body_font', 'heading_font') as $field) {
        if (!isset($fonts[$settings[$field]])) {
            $settings[$field] = $defaults[$field];
        }
    }

    $settings['base_size'] = min(22, max(14, absint($settings['base_size'])));
    $settings['nav_size'] = min(20, max(12, absint($settings['nav_size'])));
    $settings['heading_scale'] = min(130, max(80, absint($settings['heading_scale'])));

    return $settings;
}

/**
 * Build frontend CSS variables for the selected complete template.
 */
function wqs_get_site_template_custom_css($template)
{
    $template = wqs_sanitize_homepage_template($template);
    $settings = wqs_get_site_template_settings($template);
    $fonts = wqs_get_site_template_font_choices();
    $selector = 'body.wqs-design--' . sanitize_html_class($template);

    $heading_ratio = $settings['heading_scale'] / 100;

    return sprintf(
        '%1$s{--wqs-template-bg:%2$s;--wqs-template-panel:%3$s;--wqs-template-text:%4$s;--wqs-template-muted:%5$s;--wqs-template-border:%6$s;--wqs-template-accent:%7$s;--wqs-font-primary:%8$s;--wqs-font-serif:%9$s;font-family:%8$s;font-size:%10$dpx;}'
        . '%1$s .main-navigation a{font-size:%11$dpx;}'
        . '%1$s :where(.page-body,.single-works-content,.works-item-content,.review-item) h1{font-size:%12$srem;}'
        . '%1$s :where(.page-body,.single-works-content,.works-item-content,.review-item) h2{font-size:%13$srem;}'
        . '%1$s :where(.page-body,.single-works-content,.works-item-content,.review-item) h3{font-size:%14$srem;}',
        $selector,
        $settings['background'],
        $settings['panel'],
        $settings['text'],
        $settings['muted'],
        $settings['border'],
        $settings['accent'],
        $fonts[$settings['body_font']]['stack'],
        $fonts[$settings['heading_font']]['stack'],
        $settings['base_size'],
        $settings['nav_size'],
        number_format(3 * $heading_ratio, 2, '.', ''),
        number_format(1.8 * $heading_ratio, 2, '.', ''),
        number_format(1.4 * $heading_ratio, 2, '.', '')
    );
}

/**
 * Add the active site template to body classes.
 */
function wqs_homepage_body_class($classes)
{
    $classes[] = 'wqs-design';
    $classes[] = 'wqs-design--' . wqs_get_homepage_template();

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
    $caption_map = array();
    if ($slider !== '' && preg_match_all('/<a[^>]+href=["\']([^"\']+)["\']/i', $slider, $matches)) {
        foreach (array_unique($matches[1]) as $slide_url) {
            $post_id = url_to_postid(html_entity_decode($slide_url));
            if ($post_id) {
                $caption_map[untrailingslashit(html_entity_decode($slide_url))] = array(
                    'title' => get_the_title($post_id),
                    'year'  => wqs_get_creation_year($post_id),
                );
            }
        }
    }
    ?>
    <section class="wqs-home-hero wqs-home-hero--<?php echo esc_attr($variant); ?>"
             data-slide-captions="<?php echo esc_attr(wp_json_encode($caption_map, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)); ?>"
             aria-label="<?php esc_attr_e('Featured works', 'wqs-portfolio'); ?>">
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
            <div class="wqs-home-rail__progress" data-rail-target="<?php echo esc_attr($rail_id); ?>" role="scrollbar" aria-controls="<?php echo esc_attr($rail_id); ?>" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" tabindex="0"><span></span></div>
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
        'title'    => __('WQS Site Design', 'wqs-portfolio'),
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
        'label'       => __('Site Template', 'wqs-portfolio'),
        'description' => __('Choose one of the three complete WQS frontend designs.', 'wqs-portfolio'),
        'section'     => 'wqs_homepage_design',
        'type'        => 'radio',
        'choices'     => $choices,
    ));
}
add_action('customize_register', 'wqs_register_homepage_design_customizer');

/**
 * Add Appearance > WQS Site Templates.
 */
function wqs_add_homepage_template_admin_page()
{
    add_menu_page(
        __('WQS Site Templates', 'wqs-portfolio'),
        __('WQS Site Templates', 'wqs-portfolio'),
        'edit_theme_options',
        'wqs-homepage-templates',
        'wqs_render_homepage_template_admin_page',
        'dashicons-layout',
        61
    );

    add_submenu_page(
        'wqs-homepage-templates',
        __('Template Selection', 'wqs-portfolio'),
        __('Template Selection', 'wqs-portfolio'),
        'edit_theme_options',
        'wqs-homepage-templates',
        'wqs_render_homepage_template_admin_page'
    );

    foreach (wqs_get_homepage_templates() as $template_key => $template) {
        add_submenu_page(
            'wqs-homepage-templates',
            sprintf(__('%s Settings', 'wqs-portfolio'), $template['label']),
            sprintf(__('%s Settings', 'wqs-portfolio'), $template['label']),
            'edit_theme_options',
            'wqs-template-settings-' . $template_key,
            function () use ($template_key) {
                wqs_render_site_template_settings_page($template_key);
            }
        );
    }
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
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html__('Site template saved.', 'wqs-portfolio') . '</p></div>';
    }

    $current = wqs_get_homepage_template();
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('WQS Site Templates', 'wqs-portfolio'); ?></h1>
        <p><?php esc_html_e('Switching templates changes the complete frontend presentation, including the homepage, archives, posts, pages, header, footer, and mobile layout. All templates use the same content and settings.', 'wqs-portfolio'); ?></p>
        <form method="post">
            <?php wp_nonce_field('wqs_save_homepage_template', 'wqs_homepage_template_nonce'); ?>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;max-width:1100px;margin:24px 0;">
                <?php foreach (wqs_get_homepage_templates() as $key => $template) : ?>
                    <div style="display:block;background:#fff;border:<?php echo $current === $key ? '2px solid #2271b1' : '1px solid #c3c4c7'; ?>;padding:20px;">
                        <label style="display:block;cursor:pointer;">
                            <input type="radio" name="wqs_homepage_template" value="<?php echo esc_attr($key); ?>" <?php checked($current, $key); ?>>
                            <strong style="display:block;font-size:18px;margin:12px 0 6px;"><?php echo esc_html($template['label']); ?></strong>
                            <span><?php echo esc_html($template['description']); ?></span>
                        </label>
                        <a href="<?php echo esc_url(admin_url('admin.php?page=wqs-template-settings-' . $key)); ?>" style="display:block;margin-top:14px;">
                            <?php esc_html_e('Edit colors, fonts, and sizes', 'wqs-portfolio'); ?> &rarr;
                        </a>
                    </div>
                <?php endforeach; ?>
            </div>
            <?php submit_button(__('Save Site Template', 'wqs-portfolio')); ?>
        </form>
    </div>
    <?php
}

/**
 * Render and save one complete template's visual settings.
 */
function wqs_render_site_template_settings_page($template)
{
    if (!current_user_can('edit_theme_options')) {
        return;
    }

    $template = wqs_sanitize_homepage_template($template);
    $templates = wqs_get_homepage_templates();
    $defaults = wqs_get_site_template_default_settings($template);
    $fonts = wqs_get_site_template_font_choices();

    if (isset($_POST['wqs_template_settings_nonce'])
        && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['wqs_template_settings_nonce'])), 'wqs_save_template_settings_' . $template)) {
        $input = isset($_POST['wqs_template_settings']) && is_array($_POST['wqs_template_settings'])
            ? wp_unslash($_POST['wqs_template_settings'])
            : array();
        $settings = array();

        foreach (array('background', 'panel', 'text', 'muted', 'border', 'accent') as $field) {
            $settings[$field] = sanitize_hex_color($input[$field] ?? '') ?: $defaults[$field];
        }

        foreach (array('body_font', 'heading_font') as $field) {
            $value = sanitize_key($input[$field] ?? '');
            $settings[$field] = isset($fonts[$value]) ? $value : $defaults[$field];
        }

        $settings['base_size'] = min(22, max(14, absint($input['base_size'] ?? $defaults['base_size'])));
        $settings['nav_size'] = min(20, max(12, absint($input['nav_size'] ?? $defaults['nav_size'])));
        $settings['heading_scale'] = min(130, max(80, absint($input['heading_scale'] ?? $defaults['heading_scale'])));

        update_option('wqs_site_template_settings_' . $template, $settings);
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html__('Template settings saved.', 'wqs-portfolio') . '</p></div>';
    }

    if (isset($_POST['wqs_template_reset_nonce'])
        && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['wqs_template_reset_nonce'])), 'wqs_reset_template_settings_' . $template)) {
        delete_option('wqs_site_template_settings_' . $template);
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html__('Template settings reset.', 'wqs-portfolio') . '</p></div>';
    }

    $settings = wqs_get_site_template_settings($template);
    ?>
    <div class="wrap">
        <h1><?php echo esc_html($templates[$template]['label']); ?> <?php esc_html_e('Settings', 'wqs-portfolio'); ?></h1>
        <p><?php echo esc_html($templates[$template]['description']); ?></p>
        <p>
            <a href="<?php echo esc_url(admin_url('admin.php?page=wqs-homepage-templates')); ?>">
                &larr; <?php esc_html_e('Back to WQS Site Templates', 'wqs-portfolio'); ?>
            </a>
        </p>

        <form method="post" style="max-width:960px;margin-top:24px;">
            <?php wp_nonce_field('wqs_save_template_settings_' . $template, 'wqs_template_settings_nonce'); ?>

            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;">
                <?php
                $color_fields = array(
                    'background' => __('Page Background', 'wqs-portfolio'),
                    'panel'      => __('Panel Background', 'wqs-portfolio'),
                    'text'       => __('Primary Text', 'wqs-portfolio'),
                    'muted'      => __('Secondary Text', 'wqs-portfolio'),
                    'border'     => __('Borders', 'wqs-portfolio'),
                    'accent'     => __('Accent Color', 'wqs-portfolio'),
                );
                foreach ($color_fields as $field => $label) :
                    ?>
                    <label style="display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px;background:#fff;border:1px solid #c3c4c7;">
                        <span><?php echo esc_html($label); ?></span>
                        <input type="color" name="wqs_template_settings[<?php echo esc_attr($field); ?>]" value="<?php echo esc_attr($settings[$field]); ?>" style="width:64px;height:38px;">
                    </label>
                <?php endforeach; ?>
            </div>

            <table class="form-table" role="presentation" style="margin-top:24px;background:#fff;border:1px solid #c3c4c7;">
                <tbody>
                    <tr>
                        <th scope="row"><label for="wqs-body-font"><?php esc_html_e('Body Font', 'wqs-portfolio'); ?></label></th>
                        <td>
                            <select id="wqs-body-font" name="wqs_template_settings[body_font]">
                                <?php foreach ($fonts as $key => $font) : ?>
                                    <option value="<?php echo esc_attr($key); ?>" <?php selected($settings['body_font'], $key); ?>><?php echo esc_html($font['label']); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="wqs-heading-font"><?php esc_html_e('Heading Font', 'wqs-portfolio'); ?></label></th>
                        <td>
                            <select id="wqs-heading-font" name="wqs_template_settings[heading_font]">
                                <?php foreach ($fonts as $key => $font) : ?>
                                    <option value="<?php echo esc_attr($key); ?>" <?php selected($settings['heading_font'], $key); ?>><?php echo esc_html($font['label']); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="wqs-base-size"><?php esc_html_e('Body Font Size', 'wqs-portfolio'); ?></label></th>
                        <td><input id="wqs-base-size" type="number" min="14" max="22" name="wqs_template_settings[base_size]" value="<?php echo esc_attr($settings['base_size']); ?>"> px</td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="wqs-nav-size"><?php esc_html_e('Navigation Font Size', 'wqs-portfolio'); ?></label></th>
                        <td><input id="wqs-nav-size" type="number" min="12" max="20" name="wqs_template_settings[nav_size]" value="<?php echo esc_attr($settings['nav_size']); ?>"> px</td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="wqs-heading-scale"><?php esc_html_e('Content Heading Size Scale', 'wqs-portfolio'); ?></label></th>
                        <td>
                            <input id="wqs-heading-scale" type="range" min="80" max="130" step="1" name="wqs_template_settings[heading_scale]" value="<?php echo esc_attr($settings['heading_scale']); ?>" oninput="this.nextElementSibling.value=this.value">
                            <output><?php echo esc_html($settings['heading_scale']); ?></output>%
                        </td>
                    </tr>
                </tbody>
            </table>

            <?php submit_button(__('Save Template Settings', 'wqs-portfolio')); ?>
        </form>

        <form method="post" onsubmit="return confirm('<?php echo esc_js(__('Reset this template to its original design settings?', 'wqs-portfolio')); ?>');">
            <?php wp_nonce_field('wqs_reset_template_settings_' . $template, 'wqs_template_reset_nonce'); ?>
            <?php submit_button(__('Reset This Template', 'wqs-portfolio'), 'secondary', 'submit', false); ?>
        </form>
    </div>
    <?php
}
