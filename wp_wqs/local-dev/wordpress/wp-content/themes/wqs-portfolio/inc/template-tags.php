<?php
/**
 * Template Tags
 *
 * @package WQS_Portfolio
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Prints HTML with meta information for the current post-date/time.
 */
function wqs_posted_on()
{
    $time_string = '<time class="entry-date published updated" datetime="%1$s">%2$s</time>';
    if (get_the_time('U') !== get_the_modified_time('U')) {
        $time_string = '<time class="entry-date published" datetime="%1$s">%2$s</time><time class="updated" datetime="%3$s">%4$s</time>';
    }

    $year = get_the_date('Y');
    // Get year as term for works_year taxonomy
    $year_term = get_term_by('name', $year, 'works_year');
    $year_link = !is_wp_error($year_term) ? get_term_link($year_term) : '#';

    printf(
        $time_string,
        esc_attr(get_the_date(DATE_W3C)),
        esc_html(get_the_date()),
        esc_attr(get_the_modified_date(DATE_W3C)),
        esc_html(get_the_modified_date())
    );
}

/**
 * Prints HTML with meta information for the author.
 */
function wqs_posted_by()
{
    $byline = sprintf(
        '<span class="author vcard"><a class="url fn n" href="%1$s">%2$s</a></span>',
        esc_url(get_author_posts_url(get_the_author_meta('ID'))),
        esc_html(get_the_author())
    );

    echo '<span class="byline"> ' . $byline . '</span>';
}

/**
 * Prints the categories for the current post.
 */
function wqs_post_categories()
{
    $categories = get_the_terms(get_the_ID(), 'works_category');
    if ($categories && !is_wp_error($categories)) {
        echo '<div class="entry-categories">';
        foreach ($categories as $category) {
            $link = get_term_link($category, 'works_category');
            if (!is_wp_error($link)) {
                echo '<a href="' . esc_url($link) . '" class="category-link">' . esc_html($category->name) . '</a>';
            }
        }
        echo '</div>';
    }
}

/**
 * Prints the year terms for the current post.
 */
function wqs_post_years()
{
    $years = get_the_terms(get_the_ID(), 'works_year');
    if ($years && !is_wp_error($years)) {
        echo '<div class="entry-years">';
        $year_links = array();
        foreach ($years as $year) {
            $link = get_term_link($year, 'works_year');
            if (!is_wp_error($link)) {
                $year_links[] = '<a href="' . esc_url($link) . '" class="year-link">' . esc_html($year->name) . '</a>';
            }
        }
        echo implode(', ', $year_links);
        echo '</div>';
    }
}

/**
 * Displays an optional post thumbnail.
 */
function wqs_post_thumbnail()
{
    if (post_password_required() || is_attachment() || !has_post_thumbnail()) {
        return;
    }

    if (is_singular()) :
        $thumbnail = get_the_post_thumbnail(null, 'large', array('class' => 'post-thumbnail'));
    else :
        $thumbnail = get_the_post_thumbnail(null, 'works-thumb', array('class' => 'post-thumbnail'));
    endif;

    if ($thumbnail) :
        echo '<div class="post-thumbnail">' . $thumbnail . '</div>';
    endif;
}

/**
 * Prints a link to the next/previous post.
 */
function wqs_post_navigation()
{
    $prev_post = get_previous_post();
    $next_post = get_next_post();

    if (!$prev_post && !$next_post) {
        return;
    }

    echo '<nav class="post-navigation">';

    if ($prev_post) {
        echo '<a href="' . esc_url(get_permalink($prev_post)) . '" class="nav-prev">';
        echo '&larr; ' . esc_html(get_the_title($prev_post));
        echo '</a>';
    }

    if ($next_post) {
        echo '<a href="' . esc_url(get_permalink($next_post)) . '" class="nav-next">';
        echo esc_html(get_the_title($next_post)) . ' &rarr;';
        echo '</a>';
    }

    echo '</nav>';
}

/**
 * Get the current category slug from the WordPress query or request path.
 */
function wqs_get_current_category_slug()
{
    if (is_category()) {
        $term = get_queried_object();
        if ($term && !empty($term->slug)) {
            return $term->slug;
        }
    }

    if (empty($_SERVER['REQUEST_URI'])) {
        return '';
    }

    $path = parse_url(wp_unslash($_SERVER['REQUEST_URI']), PHP_URL_PATH);
    if (empty($path)) {
        return '';
    }

    $parts = array_values(array_filter(explode('/', rawurldecode($path))));
    $category_index = array_search('category', $parts, true);
    if ($category_index === false || empty($parts[$category_index + 1])) {
        return '';
    }

    return sanitize_title(end($parts));
}

/**
 * Get a translated category URL when Polylang term links are incomplete.
 */
function wqs_get_translated_category_url($target_lang)
{
    $slug = wqs_get_current_category_slug();
    if (empty($slug)) {
        return '';
    }

    $term = get_term_by('slug', $slug, 'category');
    if ($term && !is_wp_error($term) && function_exists('pll_get_term')) {
        $translated_term_id = pll_get_term($term->term_id, $target_lang);
        if (!empty($translated_term_id) && (int) $translated_term_id !== (int) $term->term_id) {
            $translated_url = get_term_link((int) $translated_term_id, 'category');
            if (!is_wp_error($translated_url)) {
                return $translated_url;
            }
        }
    }

    $candidates = array();

    if ($target_lang === 'en') {
        $base_slug = preg_replace('/-zh$/', '', $slug);
        if (substr($base_slug, -3) === '-en') {
            $candidates[] = $base_slug;
        }
        $candidates[] = $base_slug . '-en';
    } elseif ($target_lang === 'zh') {
        if (substr($slug, -3) === '-en') {
            $base_slug = substr($slug, 0, -3);
            $candidates[] = $base_slug;
            $candidates[] = $base_slug . '-zh';
        } else {
            $candidates[] = $slug;
        }
    }

    foreach (array_unique($candidates) as $candidate_slug) {
        if ($candidate_slug === $slug) {
            continue;
        }

        $candidate = get_term_by('slug', $candidate_slug, 'category');
        if (!$candidate || is_wp_error($candidate)) {
            continue;
        }

        $url = get_term_link($candidate, 'category');
        if (!is_wp_error($url)) {
            return $url;
        }
    }

    return '';
}

/**
 * Get a clean URL for the target language.
 */
function wqs_get_clean_language_url($target_lang)
{
    $category_url = wqs_get_translated_category_url($target_lang);
    if (!empty($category_url)) {
        return remove_query_arg('lang', $category_url);
    }

    if (function_exists('pll_the_languages')) {
        $languages = pll_the_languages(array(
            'raw' => 1,
            'hide_if_empty' => 0,
            'hide_if_no_translation' => 0,
        ));

        if (!empty($languages[$target_lang]['url'])) {
            return remove_query_arg('lang', $languages[$target_lang]['url']);
        }
    }

    if (function_exists('pll_home_url')) {
        return remove_query_arg('lang', pll_home_url($target_lang));
    }

    return home_url('/');
}

/**
 * Prints the language switcher - shows only the OTHER language.
 */
function wqs_language_switcher()
{
    if (!function_exists('pll_current_language')) {
        return '';
    }

    $current_lang = pll_current_language('slug');
    $other_lang = ($current_lang === 'en') ? 'zh' : 'en';
    $other_name = ($current_lang === 'en') ? '中文' : 'EN';
    $other_url = wqs_get_clean_language_url($other_lang);

    $output = '<div class="language-switcher">';
    $output .= '<a href="' . esc_url($other_url) . '" class="lang-switch-btn" rel="nofollow">' . esc_html($other_name) . '</a>';
    $output .= '</div>';

    return $output;
}
