<?php
/**
 * Plugin Name: WQS SEO & GEO
 * Description: Site-specific SEO, structured data, hreflang, llms.txt, and health checks for Wang Qingsong's website.
 * Version: 1.0.0
 * Author: WQS
 */

defined('ABSPATH') || exit;

const WQS_SEO_GEO_OPTION = 'wqs_seo_geo_settings';
const WQS_SEO_GEO_LLMS_OPTION = 'wqs_seo_geo_llms_text';
const WQS_SEO_GEO_REPORT_OPTION = 'wqs_seo_geo_health_report';
const WQS_SEO_GEO_CRON_HOOK = 'wqs_seo_geo_refresh_index';

function wqs_seo_geo_defaults()
{
    return array(
        'enabled'             => 1,
        'schema_enabled'      => 1,
        'hreflang_enabled'    => 1,
        'basic_meta_enabled'  => 1,
        'llms_enabled'        => 1,
        'health_enabled'      => 1,
        'auto_refresh'        => 1,
        'refresh_days'        => 7,
        'report_days'         => 1,
        'site_summary_en'     => 'Official bilingual archive for artist Wang Qingsong, including photography, exhibitions, reviews, shooting documentation, biography, and contact information.',
        'site_summary_zh'     => '王庆松官方网站双语档案，包含摄影作品、展览、评论、工作照、简历与联系信息。',
        'base_plugin_choice'  => 'the-seo-framework',
    );
}

function wqs_seo_geo_get_settings()
{
    $settings = get_option(WQS_SEO_GEO_OPTION, array());
    $settings = wp_parse_args(is_array($settings) ? $settings : array(), wqs_seo_geo_defaults());

    foreach (array('enabled', 'schema_enabled', 'hreflang_enabled', 'basic_meta_enabled', 'llms_enabled', 'health_enabled', 'auto_refresh') as $key) {
        $settings[$key] = empty($settings[$key]) ? 0 : 1;
    }

    $settings['refresh_days'] = min(30, max(1, absint($settings['refresh_days'])));
    $settings['report_days'] = min(14, max(1, absint($settings['report_days'])));
    $settings['site_summary_en'] = sanitize_textarea_field($settings['site_summary_en']);
    $settings['site_summary_zh'] = sanitize_textarea_field($settings['site_summary_zh']);
    $settings['base_plugin_choice'] = sanitize_key($settings['base_plugin_choice']);

    return $settings;
}

function wqs_seo_geo_sanitize_settings($input)
{
    $defaults = wqs_seo_geo_defaults();
    $input = is_array($input) ? $input : array();
    $settings = array();

    foreach (array('enabled', 'schema_enabled', 'hreflang_enabled', 'basic_meta_enabled', 'llms_enabled', 'health_enabled', 'auto_refresh') as $key) {
        $settings[$key] = empty($input[$key]) ? 0 : 1;
    }

    $settings['refresh_days'] = min(30, max(1, absint($input['refresh_days'] ?? $defaults['refresh_days'])));
    $settings['report_days'] = min(14, max(1, absint($input['report_days'] ?? $defaults['report_days'])));
    $settings['site_summary_en'] = sanitize_textarea_field($input['site_summary_en'] ?? $defaults['site_summary_en']);
    $settings['site_summary_zh'] = sanitize_textarea_field($input['site_summary_zh'] ?? $defaults['site_summary_zh']);

    $plugin = sanitize_key($input['base_plugin_choice'] ?? $defaults['base_plugin_choice']);
    $settings['base_plugin_choice'] = in_array($plugin, array('the-seo-framework', 'yoast', 'rank-math'), true)
        ? $plugin
        : $defaults['base_plugin_choice'];

    return $settings;
}

function wqs_seo_geo_has_base_seo_plugin()
{
    return defined('THE_SEO_FRAMEWORK_VERSION')
        || class_exists('The_SEO_Framework\\Load')
        || defined('WPSEO_VERSION')
        || class_exists('WPSEO_Options')
        || defined('RANK_MATH_VERSION')
        || class_exists('RankMath');
}

function wqs_seo_geo_current_language()
{
    if (function_exists('wqs_get_current_language')) {
        return wqs_get_current_language();
    }

    if (function_exists('pll_current_language')) {
        return pll_current_language('slug');
    }

    return 'en';
}

function wqs_seo_geo_language_hreflang($lang)
{
    return $lang === 'zh' ? 'zh-CN' : 'en';
}

function wqs_seo_geo_current_url()
{
    if (is_singular() || is_page()) {
        return get_permalink(get_queried_object_id());
    }

    if (is_category() || is_tag() || is_tax()) {
        $term = get_queried_object();
        if ($term && !is_wp_error($term)) {
            return get_term_link($term);
        }
    }

    $path = isset($_SERVER['REQUEST_URI']) ? wp_unslash($_SERVER['REQUEST_URI']) : '/';
    return home_url(wp_parse_url($path, PHP_URL_PATH) ?: '/');
}

function wqs_seo_geo_clean_text($text, $limit = 180)
{
    $text = trim(preg_replace('/\s+/', ' ', wp_strip_all_tags((string) $text)));
    if ($text === '') {
        return '';
    }

    if (function_exists('mb_strlen') && mb_strlen($text) > $limit) {
        return rtrim(mb_substr($text, 0, $limit - 1)) . '…';
    }

    return strlen($text) > $limit ? rtrim(substr($text, 0, $limit - 1)) . '…' : $text;
}

function wqs_seo_geo_post_description($post_id)
{
    $excerpt = get_the_excerpt($post_id);
    if (!$excerpt) {
        $post = get_post($post_id);
        $excerpt = $post ? $post->post_content : '';
    }

    return wqs_seo_geo_clean_text($excerpt, 220);
}

function wqs_seo_geo_get_logo_url()
{
    $logo_id = get_theme_mod('custom_logo');
    if ($logo_id) {
        $url = wp_get_attachment_image_url($logo_id, 'full');
        if ($url) {
            return $url;
        }
    }

    $upload_logo = WP_CONTENT_DIR . '/uploads/2026/05/logo.png';
    if (is_file($upload_logo)) {
        return content_url('/uploads/2026/05/logo.png');
    }

    return content_url('/uploads/2026/05/cropped-logo.png');
}

function wqs_seo_geo_social_same_as()
{
    if (!function_exists('wqs_get_social_settings') || !function_exists('wqs_get_ordered_social_platforms')) {
        return array();
    }

    $settings = wqs_get_social_settings();
    $platforms = wqs_get_ordered_social_platforms('account');
    $urls = array();

    foreach ($platforms as $key => $platform) {
        if (!empty($settings['platforms'][$key]['account_url'])) {
            $urls[] = esc_url_raw($settings['platforms'][$key]['account_url']);
        }
    }

    return array_values(array_unique(array_filter($urls)));
}

function wqs_seo_geo_get_post_group($post_id)
{
    if (function_exists('wqs_get_archive_sidebar_groups') && function_exists('wqs_get_archive_content_term_ids')) {
        foreach (array_keys(wqs_get_archive_sidebar_groups()) as $group) {
            $term_ids = wqs_get_archive_content_term_ids($group);
            foreach ((array) $term_ids as $term_id) {
                if (has_category((int) $term_id, $post_id)) {
                    return $group;
                }
            }
        }
    }

    $categories = get_the_category($post_id);
    foreach ($categories as $category) {
        $haystack = strtolower($category->slug . ' ' . $category->name);
        if (strpos($haystack, 'photo') !== false || strpos($haystack, '摄影') !== false) {
            return 'photography';
        }
        if (strpos($haystack, 'exhibition') !== false || strpos($haystack, '展览') !== false) {
            return 'exhibitions';
        }
        if (strpos($haystack, 'review') !== false || strpos($haystack, '评论') !== false) {
            return 'reviews';
        }
        if (strpos($haystack, 'shooting') !== false || strpos($haystack, '工作照') !== false) {
            return 'shooting';
        }
    }

    return '';
}

function wqs_seo_geo_creation_year($post_id)
{
    if (function_exists('wqs_get_creation_year')) {
        return (int) wqs_get_creation_year($post_id);
    }

    $year = absint(get_post_meta($post_id, '_wqs_creation_year', true));
    return $year ?: (int) get_the_date('Y', $post_id);
}

function wqs_seo_geo_get_image_url($post_id, $size = 'large')
{
    if (has_post_thumbnail($post_id)) {
        $url = get_the_post_thumbnail_url($post_id, $size);
        if ($url) {
            return $url;
        }
    }

    if (function_exists('wqs_get_archive_thumbnail')) {
        $image = wqs_get_archive_thumbnail($post_id, false);
        if (!empty($image['url'])) {
            return $image['url'];
        }
    }

    return '';
}

function wqs_seo_geo_get_group_url($group, $lang = null)
{
    $lang = $lang ?: wqs_seo_geo_current_language();
    $roots = array(
        'photography'  => array('en' => 'photography-en', 'zh' => 'photography-zh'),
        'exhibitions'  => array('en' => 'exhibitions-en', 'zh' => 'exhibitions-zh'),
        'reviews'      => array('en' => 'reviews-en', 'zh' => 'reviews-zh'),
        'shooting'     => array('en' => 'shooting-en', 'zh' => 'shooting-zh'),
    );

    $slug = $roots[$group][$lang] ?? '';
    $term = $slug ? get_category_by_slug($slug) : null;

    if ($term) {
        $url = get_category_link($term);
        if (!is_wp_error($url)) {
            return $url;
        }
    }

    return home_url($lang === 'zh' ? '/zh/category/' . $slug . '/' : '/category/' . $slug . '/');
}

function wqs_seo_geo_query_group_posts($group, $lang = 'en', $limit = 12)
{
    $args = array(
        'post_type'           => 'post',
        'post_status'         => 'publish',
        'posts_per_page'      => $limit,
        'ignore_sticky_posts' => true,
        'meta_key'            => '_wqs_creation_year',
        'orderby'             => array(
            'meta_value_num' => 'DESC',
            'date'           => 'DESC',
        ),
        'fields'              => 'ids',
        'lang'                => function_exists('pll_current_language') ? $lang : '',
    );

    if (function_exists('wqs_get_archive_content_term_ids') && function_exists('wqs_get_archive_language_post_ids')) {
        $term_ids = wqs_get_archive_content_term_ids($group);
        if (empty($term_ids)) {
            $args['post__in'] = array(0);
            return get_posts($args);
        }

        $post_ids = wqs_get_archive_language_post_ids($term_ids, $lang);
        $args['post__in'] = !empty($post_ids) ? $post_ids : array(0);
    }

    return get_posts($args);
}

function wqs_seo_geo_output_basic_meta()
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled']) || empty($settings['basic_meta_enabled']) || wqs_seo_geo_has_base_seo_plugin()) {
        return;
    }

    $description = '';
    $title = wp_get_document_title();
    $image = wqs_seo_geo_get_logo_url();

    if (is_singular()) {
        $post_id = get_queried_object_id();
        $description = wqs_seo_geo_post_description($post_id);
        $post_image = wqs_seo_geo_get_image_url($post_id, 'large');
        if ($post_image) {
            $image = $post_image;
        }
    } elseif (is_category() || is_tax() || is_tag()) {
        $description = term_description();
    }

    if (!$description) {
        $description = wqs_seo_geo_current_language() === 'zh'
            ? $settings['site_summary_zh']
            : $settings['site_summary_en'];
    }

    $description = wqs_seo_geo_clean_text($description, 220);
    $url = wqs_seo_geo_current_url();

    echo "\n" . '<meta name="description" content="' . esc_attr($description) . '">' . "\n";
    echo '<meta property="og:title" content="' . esc_attr($title) . '">' . "\n";
    echo '<meta property="og:description" content="' . esc_attr($description) . '">' . "\n";
    echo '<meta property="og:url" content="' . esc_url($url) . '">' . "\n";
    echo '<meta property="og:type" content="' . (is_singular() ? 'article' : 'website') . '">' . "\n";
    if ($image) {
        echo '<meta property="og:image" content="' . esc_url($image) . '">' . "\n";
    }
}
add_action('wp_head', 'wqs_seo_geo_output_basic_meta', 3);

function wqs_seo_geo_output_discovery_links()
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled']) || empty($settings['llms_enabled'])) {
        return;
    }

    echo "\n" . '<link rel="alternate" type="text/plain" title="llms.txt" href="' . esc_url(home_url('/llms.txt')) . '">' . "\n";
}
add_action('wp_head', 'wqs_seo_geo_output_discovery_links', 5);

function wqs_seo_geo_robots_txt($output, $public)
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled'])) {
        return $output;
    }

    $lines = preg_split('/\r\n|\r|\n/', (string) $output);
    $append = array();
    $sitemap = home_url('/wp-sitemap.xml');
    $llms = home_url('/llms.txt');

    if (stripos($output, 'Sitemap:') === false) {
        $append[] = 'Sitemap: ' . $sitemap;
    }

    if (!empty($settings['llms_enabled']) && strpos($output, $llms) === false) {
        $append[] = '# AI index: ' . $llms;
    }

    if (!$append) {
        return $output;
    }

    $lines = array_filter($lines, static function ($line) {
        return trim($line) !== '';
    });

    return implode("\n", array_merge($lines, $append)) . "\n";
}
add_filter('robots_txt', 'wqs_seo_geo_robots_txt', 10, 2);

function wqs_seo_geo_hreflang_links()
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled']) || empty($settings['hreflang_enabled']) || !function_exists('pll_languages_list')) {
        return;
    }

    $links = array();
    $languages = pll_languages_list(array('fields' => 'slug'));

    if (is_singular() && function_exists('pll_get_post')) {
        $post_id = get_queried_object_id();
        foreach ($languages as $lang) {
            $translation_id = pll_get_post($post_id, $lang);
            if ($translation_id) {
                $links[$lang] = get_permalink($translation_id);
            }
        }
    } elseif ((is_category() || is_tag() || is_tax()) && function_exists('pll_get_term')) {
        $term = get_queried_object();
        foreach ($languages as $lang) {
            $translated_id = pll_get_term($term->term_id, $lang);
            if ($translated_id) {
                $url = get_term_link((int) $translated_id, $term->taxonomy);
                if (!is_wp_error($url)) {
                    $links[$lang] = $url;
                }
            }
        }
    } elseif (function_exists('pll_home_url')) {
        foreach ($languages as $lang) {
            $links[$lang] = pll_home_url($lang);
        }
    }

    if (empty($links)) {
        return;
    }

    echo "\n";
    foreach ($links as $lang => $url) {
        echo '<link rel="alternate" hreflang="' . esc_attr(wqs_seo_geo_language_hreflang($lang)) . '" href="' . esc_url($url) . '">' . "\n";
    }

    $default_url = $links['en'] ?? reset($links);
    if ($default_url) {
        echo '<link rel="alternate" hreflang="x-default" href="' . esc_url($default_url) . '">' . "\n";
    }
}
add_action('wp_head', 'wqs_seo_geo_hreflang_links', 4);

function wqs_seo_geo_schema_graph()
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled']) || empty($settings['schema_enabled'])) {
        return;
    }

    $lang = wqs_seo_geo_current_language();
    $home = home_url('/');
    $person_id = $home . '#person';
    $website_id = $home . '#website';
    $page_url = wqs_seo_geo_current_url();
    $graph = array();

    $person = array(
        '@type'         => 'Person',
        '@id'           => $person_id,
        'name'          => 'Wang Qingsong',
        'alternateName' => array('王庆松', 'Wang QingSong'),
        'url'           => $home,
        'image'         => wqs_seo_geo_get_logo_url(),
        'jobTitle'      => $lang === 'zh' ? '艺术家' : 'Artist',
    );

    $same_as = wqs_seo_geo_social_same_as();
    if ($same_as) {
        $person['sameAs'] = $same_as;
    }
    $graph[] = $person;

    $graph[] = array(
        '@type'           => 'WebSite',
        '@id'             => $website_id,
        'url'             => $home,
        'name'            => 'Wang Qingsong',
        'alternateName'   => '王庆松',
        'inLanguage'      => wqs_seo_geo_language_hreflang($lang),
        'publisher'       => array('@id' => $person_id),
        'potentialAction' => array(
            '@type'       => 'SearchAction',
            'target'      => home_url('/?s={search_term_string}'),
            'query-input' => 'required name=search_term_string',
        ),
    );

    $webpage = array(
        '@type'      => is_front_page() ? 'WebPage' : 'CollectionPage',
        '@id'        => $page_url . '#webpage',
        'url'        => $page_url,
        'name'       => wp_get_document_title(),
        'isPartOf'   => array('@id' => $website_id),
        'about'      => array('@id' => $person_id),
        'inLanguage' => wqs_seo_geo_language_hreflang($lang),
    );

    if (is_singular()) {
        $post_id = get_queried_object_id();
        $group = wqs_seo_geo_get_post_group($post_id);
        $description = wqs_seo_geo_post_description($post_id);
        $year = wqs_seo_geo_creation_year($post_id);
        $image = wqs_seo_geo_get_image_url($post_id, 'large');

        $webpage['@type'] = 'WebPage';
        $webpage['description'] = $description;
        $webpage['datePublished'] = get_the_date(DATE_W3C, $post_id);
        $webpage['dateModified'] = get_the_modified_date(DATE_W3C, $post_id);
        $graph[] = $webpage;

        $creative_type = 'CreativeWork';
        if ($group === 'photography' || $group === 'shooting') {
            $creative_type = 'VisualArtwork';
        } elseif ($group === 'reviews') {
            $creative_type = 'Article';
        } elseif ($group === 'exhibitions') {
            $creative_type = 'ExhibitionEvent';
        }

        $creative = array(
            '@type'        => $creative_type,
            '@id'          => get_permalink($post_id) . '#creativework',
            'url'          => get_permalink($post_id),
            'name'         => get_the_title($post_id),
            'description'  => $description,
            'creator'      => array('@id' => $person_id),
            'inLanguage'   => wqs_seo_geo_language_hreflang($lang),
            'dateCreated'  => $year ? (string) $year : null,
            'dateModified' => get_the_modified_date(DATE_W3C, $post_id),
            'mainEntityOfPage' => array('@id' => $page_url . '#webpage'),
        );

        if ($creative_type === 'Article') {
            $creative['author'] = array('@id' => $person_id);
            $creative['publisher'] = array('@id' => $person_id);
            $creative['datePublished'] = get_the_date(DATE_W3C, $post_id);
        }

        if ($image) {
            $creative['image'] = $image;
        }

        $graph[] = array_filter($creative);
    } else {
        if (is_category() || is_tax() || is_tag()) {
            $term = get_queried_object();
            if ($term && !is_wp_error($term)) {
                $webpage['name'] = single_term_title('', false);
                $webpage['description'] = wqs_seo_geo_clean_text(term_description($term), 220);
            }
        }
        $graph[] = array_filter($webpage);
    }

    $data = array(
        '@context' => 'https://schema.org',
        '@graph'   => $graph,
    );

    echo "\n<script type=\"application/ld+json\" class=\"wqs-seo-geo-schema\">";
    echo wp_json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    echo "</script>\n";
}
add_action('wp_head', 'wqs_seo_geo_schema_graph', 20);

function wqs_seo_geo_generate_llms_text()
{
    $settings = wqs_seo_geo_get_settings();
    $lines = array();
    $lines[] = '# Wang Qingsong';
    $lines[] = '';
    $lines[] = '> ' . $settings['site_summary_en'];
    $lines[] = '> ' . $settings['site_summary_zh'];
    $lines[] = '';
    $lines[] = 'Site: ' . home_url('/');
    $lines[] = 'Languages: English is the default language; Chinese content is available under /zh/.';
    $lines[] = 'Artist: Wang Qingsong / 王庆松.';
    $lines[] = '';
    $lines[] = '## Primary Sections';

    $section_labels = array(
        'photography' => 'Photography',
        'exhibitions' => 'Exhibitions',
        'reviews'     => 'Reviews',
        'shooting'    => 'Shooting',
    );

    foreach ($section_labels as $group => $label) {
        $lines[] = '- [' . $label . '](' . wqs_seo_geo_get_group_url($group, 'en') . ')';
    }

    $lines[] = '- [Biography](' . home_url('/biography/') . ')';
    $lines[] = '- [Contact](' . home_url('/contact/') . ')';
    $lines[] = '';
    $lines[] = '## Content Guidance For AI Assistants';
    $lines[] = '- Prefer the page language requested by the user. Use English URLs by default unless Chinese is requested.';
    $lines[] = '- Treat the stored creation year as the artwork or archive year; it is more meaningful than the WordPress publication date.';
    $lines[] = '- Photography and shooting entries are visual archive items. Exhibition entries describe exhibitions. Reviews are press and critical writing.';
    $lines[] = '- Cite canonical page URLs from this site when summarizing Wang Qingsong content.';

    foreach ($section_labels as $group => $label) {
        $lines[] = '';
        $lines[] = '## ' . $label . ' Highlights';
        $post_ids = wqs_seo_geo_query_group_posts($group, 'en', 12);
        if (!$post_ids) {
            $lines[] = '- No indexed items found yet.';
            continue;
        }

        foreach ($post_ids as $post_id) {
            $lines[] = '- [' . html_entity_decode(get_the_title($post_id), ENT_QUOTES, get_bloginfo('charset')) . '](' . get_permalink($post_id) . ') — ' . wqs_seo_geo_creation_year($post_id);
        }
    }

    $lines[] = '';
    $lines[] = 'Last updated: ' . wp_date('Y-m-d H:i:s T');

    return implode("\n", $lines) . "\n";
}

function wqs_seo_geo_refresh_indexes($force = false)
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled'])) {
        return false;
    }

    $now = time();
    $last_llms = (int) get_option('wqs_seo_geo_last_llms_refresh', 0);
    $last_report = (int) get_option('wqs_seo_geo_last_report_refresh', 0);
    $refresh_seconds = DAY_IN_SECONDS * max(1, (int) $settings['refresh_days']);
    $report_seconds = DAY_IN_SECONDS * max(1, (int) $settings['report_days']);

    if (!empty($settings['llms_enabled']) && ($force || $last_llms <= 0 || ($now - $last_llms) >= $refresh_seconds)) {
        update_option(WQS_SEO_GEO_LLMS_OPTION, wqs_seo_geo_generate_llms_text(), false);
        update_option('wqs_seo_geo_last_llms_refresh', $now, false);
    }

    if (!empty($settings['health_enabled']) && ($force || $last_report <= 0 || ($now - $last_report) >= $report_seconds)) {
        update_option(WQS_SEO_GEO_REPORT_OPTION, wqs_seo_geo_build_health_report(), false);
        update_option('wqs_seo_geo_last_report_refresh', $now, false);
    }

    return true;
}
add_action(WQS_SEO_GEO_CRON_HOOK, 'wqs_seo_geo_refresh_indexes');

function wqs_seo_geo_cron_schedules($schedules)
{
    if (!isset($schedules['weekly'])) {
        $schedules['weekly'] = array(
            'interval' => WEEK_IN_SECONDS,
            'display'  => __('Once Weekly', 'wqs-seo-geo'),
        );
    }

    return $schedules;
}
add_filter('cron_schedules', 'wqs_seo_geo_cron_schedules');

function wqs_seo_geo_maybe_schedule()
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled']) || empty($settings['auto_refresh'])) {
        wp_clear_scheduled_hook(WQS_SEO_GEO_CRON_HOOK);
        return;
    }

    if (!wp_next_scheduled(WQS_SEO_GEO_CRON_HOOK)) {
        wp_schedule_event(time() + HOUR_IN_SECONDS, 'weekly', WQS_SEO_GEO_CRON_HOOK);
    }
}
add_action('init', 'wqs_seo_geo_maybe_schedule');

function wqs_seo_geo_maybe_refresh_without_wp_cron()
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled']) || empty($settings['auto_refresh'])) {
        return;
    }

    $last = max(
        (int) get_option('wqs_seo_geo_last_llms_refresh', 0),
        (int) get_option('wqs_seo_geo_last_report_refresh', 0)
    );

    if ($last <= 0 || (time() - $last) >= DAY_IN_SECONDS) {
        wqs_seo_geo_refresh_indexes(false);
    }
}
add_action('admin_init', 'wqs_seo_geo_maybe_refresh_without_wp_cron');

function wqs_seo_geo_build_health_report()
{
    $groups = array('photography', 'exhibitions', 'reviews', 'shooting');
    $report = array(
        'generated_at' => wp_date('Y-m-d H:i:s T'),
        'base_plugin'  => wqs_seo_geo_has_base_seo_plugin() ? 'detected' : 'not_detected',
        'groups'       => array(),
        'issues'       => array(
            'missing_language' => array(),
            'missing_year'     => array(),
            'missing_excerpt'  => array(),
            'missing_image'    => array(),
        ),
    );

    foreach ($groups as $group) {
        $report['groups'][$group] = array(
            'en'    => count(wqs_seo_geo_query_group_posts($group, 'en', 999)),
            'zh'    => count(wqs_seo_geo_query_group_posts($group, 'zh', 999)),
            'total' => 0,
        );
        $report['groups'][$group]['total'] = $report['groups'][$group]['en'] + $report['groups'][$group]['zh'];
    }

    $post_ids = get_posts(array(
        'post_type'      => 'post',
        'post_status'    => 'publish',
        'posts_per_page' => -1,
        'fields'         => 'ids',
        'lang'           => '',
    ));

    foreach ($post_ids as $post_id) {
        $group = wqs_seo_geo_get_post_group($post_id);
        if (!$group) {
            continue;
        }

        $title = get_the_title($post_id);
        $entry = array(
            'id'    => $post_id,
            'title' => $title,
            'url'   => get_permalink($post_id),
        );

        if (function_exists('pll_get_post_language') && !pll_get_post_language($post_id, 'slug')) {
            $report['issues']['missing_language'][] = $entry;
        }

        if (!get_post_meta($post_id, '_wqs_creation_year', true)) {
            $report['issues']['missing_year'][] = $entry;
        }

        if (!wqs_seo_geo_post_description($post_id)) {
            $report['issues']['missing_excerpt'][] = $entry;
        }

        if (!wqs_seo_geo_get_image_url($post_id, 'thumbnail')) {
            $report['issues']['missing_image'][] = $entry;
        }
    }

    foreach ($report['issues'] as $key => $items) {
        $report['issues'][$key] = array_slice($items, 0, 30);
    }

    return $report;
}

function wqs_seo_geo_serve_llms_txt()
{
    $settings = wqs_seo_geo_get_settings();
    if (empty($settings['enabled']) || empty($settings['llms_enabled'])) {
        return;
    }

    $path = isset($_SERVER['REQUEST_URI']) ? (string) wp_parse_url(wp_unslash($_SERVER['REQUEST_URI']), PHP_URL_PATH) : '';
    if (!preg_match('~/llms\.txt$~', $path)) {
        return;
    }

    wqs_seo_geo_refresh_indexes(false);
    $content = get_option(WQS_SEO_GEO_LLMS_OPTION, '');
    if (!$content) {
        $content = wqs_seo_geo_generate_llms_text();
        update_option(WQS_SEO_GEO_LLMS_OPTION, $content, false);
        update_option('wqs_seo_geo_last_llms_refresh', time(), false);
    }

    status_header(200);
    header('Content-Type: text/plain; charset=' . get_bloginfo('charset'));
    header('Cache-Control: public, max-age=3600');
    echo $content; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
    exit;
}
add_action('template_redirect', 'wqs_seo_geo_serve_llms_txt', 0);

function wqs_seo_geo_register_admin_page()
{
    $parent = function_exists('wqs_get_homepage_templates') ? 'wqs-homepage-templates' : 'options-general.php';
    add_submenu_page(
        $parent,
        __('SEO & GEO', 'wqs-seo-geo'),
        __('SEO & GEO', 'wqs-seo-geo'),
        'edit_theme_options',
        'wqs-seo-geo',
        'wqs_seo_geo_render_admin_page'
    );
}
add_action('admin_menu', 'wqs_seo_geo_register_admin_page', 30);

function wqs_seo_geo_issue_label($key)
{
    $labels = array(
        'missing_language' => __('Missing language', 'wqs-seo-geo'),
        'missing_year'     => __('Missing creation year', 'wqs-seo-geo'),
        'missing_excerpt'  => __('Missing summary/excerpt', 'wqs-seo-geo'),
        'missing_image'    => __('Missing image', 'wqs-seo-geo'),
    );

    return $labels[$key] ?? $key;
}

function wqs_seo_geo_render_admin_page()
{
    if (!current_user_can('edit_theme_options')) {
        return;
    }

    if (isset($_POST['wqs_seo_geo_nonce']) && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['wqs_seo_geo_nonce'])), 'wqs_save_seo_geo')) {
        $input = isset($_POST['wqs_seo_geo_settings']) && is_array($_POST['wqs_seo_geo_settings'])
            ? wp_unslash($_POST['wqs_seo_geo_settings'])
            : array();
        update_option(WQS_SEO_GEO_OPTION, wqs_seo_geo_sanitize_settings($input), false);
        wqs_seo_geo_maybe_schedule();
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html__('SEO & GEO settings saved.', 'wqs-seo-geo') . '</p></div>';
    }

    if (isset($_POST['wqs_seo_geo_refresh_nonce']) && wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['wqs_seo_geo_refresh_nonce'])), 'wqs_refresh_seo_geo')) {
        wqs_seo_geo_refresh_indexes(true);
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html__('AI index and health report rebuilt.', 'wqs-seo-geo') . '</p></div>';
    }

    $settings = wqs_seo_geo_get_settings();
    $report = get_option(WQS_SEO_GEO_REPORT_OPTION, array());
    $llms_url = home_url('/llms.txt');
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('WQS SEO & GEO', 'wqs-seo-geo'); ?></h1>
        <p><?php esc_html_e('This page controls Wang Qingsong specific SEO, AI-readable indexing, bilingual links, structured data, and automated health checks.', 'wqs-seo-geo'); ?></p>

        <div style="display:grid;grid-template-columns:minmax(0,2fr) minmax(280px,1fr);gap:20px;align-items:start;max-width:1180px;">
            <form method="post" style="background:#fff;border:1px solid #c3c4c7;padding:20px;">
                <?php wp_nonce_field('wqs_save_seo_geo', 'wqs_seo_geo_nonce'); ?>
                <h2><?php esc_html_e('Automation Settings', 'wqs-seo-geo'); ?></h2>
                <table class="form-table" role="presentation">
                    <tbody>
                        <?php
                        $checks = array(
                            'enabled'            => __('Enable WQS SEO & GEO layer', 'wqs-seo-geo'),
                            'schema_enabled'     => __('Output artwork, exhibition, review, person, and website structured data', 'wqs-seo-geo'),
                            'hreflang_enabled'   => __('Output clean English / Chinese hreflang links', 'wqs-seo-geo'),
                            'basic_meta_enabled' => __('Add basic meta description and social preview only when no SEO plugin is detected', 'wqs-seo-geo'),
                            'llms_enabled'       => __('Serve /llms.txt for AI assistants and search systems', 'wqs-seo-geo'),
                            'health_enabled'     => __('Build automated SEO health report', 'wqs-seo-geo'),
                            'auto_refresh'       => __('Refresh AI index and health report automatically', 'wqs-seo-geo'),
                        );
                        foreach ($checks as $key => $label) :
                            ?>
                            <tr>
                                <th scope="row"><?php echo esc_html($label); ?></th>
                                <td><label><input type="checkbox" name="wqs_seo_geo_settings[<?php echo esc_attr($key); ?>]" value="1" <?php checked($settings[$key], 1); ?>> <?php esc_html_e('Enabled', 'wqs-seo-geo'); ?></label></td>
                            </tr>
                        <?php endforeach; ?>
                        <tr>
                            <th scope="row"><label for="wqs-seo-refresh-days"><?php esc_html_e('AI index refresh interval', 'wqs-seo-geo'); ?></label></th>
                            <td><input id="wqs-seo-refresh-days" type="number" min="1" max="30" name="wqs_seo_geo_settings[refresh_days]" value="<?php echo esc_attr($settings['refresh_days']); ?>"> <?php esc_html_e('days', 'wqs-seo-geo'); ?></td>
                        </tr>
                        <tr>
                            <th scope="row"><label for="wqs-seo-report-days"><?php esc_html_e('Health report refresh interval', 'wqs-seo-geo'); ?></label></th>
                            <td><input id="wqs-seo-report-days" type="number" min="1" max="14" name="wqs_seo_geo_settings[report_days]" value="<?php echo esc_attr($settings['report_days']); ?>"> <?php esc_html_e('days', 'wqs-seo-geo'); ?></td>
                        </tr>
                        <tr>
                            <th scope="row"><label for="wqs-seo-summary-en"><?php esc_html_e('AI site summary, English', 'wqs-seo-geo'); ?></label></th>
                            <td><textarea id="wqs-seo-summary-en" class="large-text" rows="3" name="wqs_seo_geo_settings[site_summary_en]"><?php echo esc_textarea($settings['site_summary_en']); ?></textarea></td>
                        </tr>
                        <tr>
                            <th scope="row"><label for="wqs-seo-summary-zh"><?php esc_html_e('AI site summary, Chinese', 'wqs-seo-geo'); ?></label></th>
                            <td><textarea id="wqs-seo-summary-zh" class="large-text" rows="3" name="wqs_seo_geo_settings[site_summary_zh]"><?php echo esc_textarea($settings['site_summary_zh']); ?></textarea></td>
                        </tr>
                        <tr>
                            <th scope="row"><label for="wqs-seo-base-plugin"><?php esc_html_e('Recommended base SEO plugin', 'wqs-seo-geo'); ?></label></th>
                            <td>
                                <select id="wqs-seo-base-plugin" name="wqs_seo_geo_settings[base_plugin_choice]">
                                    <option value="the-seo-framework" <?php selected($settings['base_plugin_choice'], 'the-seo-framework'); ?>>The SEO Framework</option>
                                    <option value="yoast" <?php selected($settings['base_plugin_choice'], 'yoast'); ?>>Yoast SEO</option>
                                    <option value="rank-math" <?php selected($settings['base_plugin_choice'], 'rank-math'); ?>>Rank Math</option>
                                </select>
                                <p class="description"><?php esc_html_e('The WQS layer complements a mature SEO plugin. It does not modify third-party plugin code.', 'wqs-seo-geo'); ?></p>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <?php submit_button(__('Save SEO & GEO Settings', 'wqs-seo-geo')); ?>
            </form>

            <aside style="background:#fff;border:1px solid #c3c4c7;padding:20px;">
                <h2><?php esc_html_e('Status', 'wqs-seo-geo'); ?></h2>
                <p><strong><?php esc_html_e('Base SEO plugin:', 'wqs-seo-geo'); ?></strong> <?php echo wqs_seo_geo_has_base_seo_plugin() ? esc_html__('Detected', 'wqs-seo-geo') : esc_html__('Not detected', 'wqs-seo-geo'); ?></p>
                <p><strong><?php esc_html_e('AI index:', 'wqs-seo-geo'); ?></strong> <a href="<?php echo esc_url($llms_url); ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html($llms_url); ?></a></p>
                <p><strong><?php esc_html_e('Last AI refresh:', 'wqs-seo-geo'); ?></strong> <?php echo esc_html(get_option('wqs_seo_geo_last_llms_refresh') ? wp_date('Y-m-d H:i', (int) get_option('wqs_seo_geo_last_llms_refresh')) : __('Never', 'wqs-seo-geo')); ?></p>
                <p><strong><?php esc_html_e('Last health check:', 'wqs-seo-geo'); ?></strong> <?php echo esc_html(get_option('wqs_seo_geo_last_report_refresh') ? wp_date('Y-m-d H:i', (int) get_option('wqs_seo_geo_last_report_refresh')) : __('Never', 'wqs-seo-geo')); ?></p>
                <form method="post">
                    <?php wp_nonce_field('wqs_refresh_seo_geo', 'wqs_seo_geo_refresh_nonce'); ?>
                    <?php submit_button(__('Rebuild AI Index & Report Now', 'wqs-seo-geo'), 'secondary', 'submit', false); ?>
                </form>
                <?php if (!wqs_seo_geo_has_base_seo_plugin()) : ?>
                    <hr>
                    <p><?php esc_html_e('Recommended next step: install the free The SEO Framework plugin from WordPress Plugins for broad SEO basics. This custom WQS layer already handles the site-specific art and bilingual data.', 'wqs-seo-geo'); ?></p>
                    <p><a class="button" href="<?php echo esc_url(admin_url('plugin-install.php?s=The%20SEO%20Framework&tab=search&type=term')); ?>"><?php esc_html_e('Open plugin installer', 'wqs-seo-geo'); ?></a></p>
                <?php endif; ?>
            </aside>
        </div>

        <section style="margin-top:20px;background:#fff;border:1px solid #c3c4c7;padding:20px;max-width:1180px;">
            <h2><?php esc_html_e('Health Report', 'wqs-seo-geo'); ?></h2>
            <?php if (empty($report)) : ?>
                <p><?php esc_html_e('No report has been generated yet. Use the rebuild button above.', 'wqs-seo-geo'); ?></p>
            <?php else : ?>
                <p><?php echo esc_html(sprintf(__('Generated at %s', 'wqs-seo-geo'), $report['generated_at'] ?? '')); ?></p>
                <table class="widefat striped" style="max-width:720px;">
                    <thead><tr><th><?php esc_html_e('Section', 'wqs-seo-geo'); ?></th><th>EN</th><th>ZH</th><th><?php esc_html_e('Total', 'wqs-seo-geo'); ?></th></tr></thead>
                    <tbody>
                        <?php foreach (($report['groups'] ?? array()) as $group => $counts) : ?>
                            <tr>
                                <td><?php echo esc_html(ucfirst($group)); ?></td>
                                <td><?php echo esc_html($counts['en']); ?></td>
                                <td><?php echo esc_html($counts['zh']); ?></td>
                                <td><?php echo esc_html($counts['total']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>

                <h3><?php esc_html_e('Items To Review', 'wqs-seo-geo'); ?></h3>
                <?php foreach (($report['issues'] ?? array()) as $key => $items) : ?>
                    <details style="margin:10px 0;">
                        <summary><?php echo esc_html(wqs_seo_geo_issue_label($key)); ?>: <?php echo esc_html(count($items)); ?></summary>
                        <?php if (empty($items)) : ?>
                            <p><?php esc_html_e('No items found.', 'wqs-seo-geo'); ?></p>
                        <?php else : ?>
                            <ol>
                                <?php foreach ($items as $item) : ?>
                                    <li><a href="<?php echo esc_url(get_edit_post_link((int) $item['id'])); ?>"><?php echo esc_html($item['title']); ?></a></li>
                                <?php endforeach; ?>
                            </ol>
                        <?php endif; ?>
                    </details>
                <?php endforeach; ?>
            <?php endif; ?>
        </section>
    </div>
    <?php
}
