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
 * Prints the language switcher - shows only the OTHER language.
 */
function wqs_language_switcher()
{
    if (!function_exists('pll_current_language') || !function_exists('pll_get_post')) {
        return '';
    }

    $current_lang = pll_current_language('slug');
    $other_lang = ($current_lang === 'en') ? 'zh' : 'en';
    $other_name = ($current_lang === 'en') ? '中文' : 'EN';

    // Get the current URL and replace/append the language parameter
    $current_url = (is_ssl() ? 'https://' : 'http://') . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];

    // Remove any existing lang parameter and add the new one
    $current_url = remove_query_arg('lang', $current_url);
    $other_url = add_query_arg('lang', $other_lang, $current_url);

    $output = '<div class="language-switcher">';
    $output .= '<a href="' . esc_url($other_url) . '" class="lang-switch-btn" rel="nofollow">' . esc_html($other_name) . '</a>';
    $output .= '</div>';

    return $output;
}