<?php
/**
 * Restore legacy Joomla exhibition pages as individual WordPress exhibitions.
 *
 * Usage:
 * php migration-scripts/import-exhibition-articles.php --dry-run
 * php migration-scripts/import-exhibition-articles.php
 */

require dirname(__DIR__) . '/local-dev/wordpress/wp-load.php';

$dry_run = in_array('--dry-run', $argv, true);
$legacy_db = new PDO(
    'mysql:host=127.0.0.1;port=3306;dbname=wqs_joomla_analysis;charset=utf8mb4',
    'root',
    'GM3750-jm',
    array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION)
);

function wqs_legacy_exhibition_clean_text($text)
{
    $text = html_entity_decode(wp_strip_all_tags($text), ENT_QUOTES | ENT_HTML5, 'UTF-8');
    return trim(preg_replace('/\s+/u', ' ', $text));
}

function wqs_legacy_exhibition_image_url($url)
{
    $url = html_entity_decode((string) $url, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    $path_start = stripos($url, 'images/stories/exhibition/');
    if ($path_start === false) {
        return '';
    }

    $path = substr($url, $path_start);
    $path = preg_replace('/[?#].*$/', '', $path);
    $path = preg_replace('#/index/#', '/', $path);
    $path = trim($path);

    if (!preg_match('/\.(?:jpe?g|png|gif|webp)$/i', $path)) {
        return '';
    }

    return home_url('/' . ltrim($path, '/'));
}

function wqs_legacy_exhibition_block_has_content(DOMElement $element)
{
    if (wqs_legacy_exhibition_clean_text($element->textContent) !== '') {
        return true;
    }

    return $element->getElementsByTagName('img')->length > 0;
}

function wqs_legacy_exhibition_collect_blocks(DOMNode $node, array &$blocks)
{
    $block_tags = array('div', 'p', 'table', 'tbody', 'tr', 'td', 'section', 'article');

    foreach ($node->childNodes as $child) {
        if (!$child instanceof DOMElement) {
            continue;
        }

        $has_meaningful_block_child = false;
        foreach ($child->childNodes as $grandchild) {
            if (
                $grandchild instanceof DOMElement
                && in_array(strtolower($grandchild->tagName), $block_tags, true)
                && wqs_legacy_exhibition_block_has_content($grandchild)
            ) {
                $has_meaningful_block_child = true;
                break;
            }
        }

        if ($has_meaningful_block_child) {
            wqs_legacy_exhibition_collect_blocks($child, $blocks);
            continue;
        }

        $text = wqs_legacy_exhibition_clean_text($child->textContent);
        $images = array();

        foreach ($child->getElementsByTagName('a') as $link) {
            $image_url = wqs_legacy_exhibition_image_url($link->getAttribute('href'));
            if ($image_url !== '') {
                $images[] = $image_url;
            }
        }

        if (empty($images)) {
            foreach ($child->getElementsByTagName('img') as $image) {
                $image_url = wqs_legacy_exhibition_image_url($image->getAttribute('src'));
                if ($image_url !== '') {
                    $images[] = $image_url;
                }
            }
        }

        $images = array_values(array_unique($images));
        if ($text !== '' || !empty($images)) {
            $blocks[] = array('text' => $text, 'images' => $images);
        }
    }
}

function wqs_legacy_exhibition_parse_groups($html, $fallback_title)
{
    $document = new DOMDocument();
    libxml_use_internal_errors(true);
    $document->loadHTML(
        '<?xml encoding="utf-8" ?><div id="wqs-legacy-root">' . $html . '</div>',
        LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD
    );
    libxml_clear_errors();

    $xpath = new DOMXPath($document);
    $root = $xpath->query('//*[@id="wqs-legacy-root"]')->item(0);
    $blocks = array();
    wqs_legacy_exhibition_collect_blocks($root, $blocks);

    $groups = array();
    $current = null;

    foreach ($blocks as $block) {
        if ($block['text'] !== '') {
            if ($current && !empty($current['images'])) {
                $groups[] = $current;
            }

            $current = array(
                'title'  => $block['text'],
                'images' => $block['images'],
            );
            continue;
        }

        if (!empty($block['images'])) {
            if (!$current) {
                $current = array('title' => $fallback_title, 'images' => array());
            }
            $current['images'] = array_merge($current['images'], $block['images']);
        }
    }

    if ($current && !empty($current['images'])) {
        $groups[] = $current;
    }

    if (empty($groups)) {
        return array();
    }

    foreach ($groups as &$group) {
        $group['images'] = array_values(array_unique($group['images']));
    }

    return $groups;
}

function wqs_legacy_exhibition_content(array $images)
{
    $html = '<div class="exhibition-gallery pswp-gallery">';
    foreach ($images as $image_url) {
        $html .= '<figure class="exhibition-gallery-item">';
        $html .= '<a href="' . esc_url($image_url) . '">';
        $html .= '<img src="' . esc_url($image_url) . '" alt="" loading="lazy">';
        $html .= '</a></figure>';
    }
    return $html . '</div>';
}

function wqs_legacy_exhibition_term($year)
{
    $slugs = array(sanitize_title($year . '-exhibitions'));
    if ($year === '2018-2019') {
        $slugs[] = '18-19-exhibitions';
    }

    foreach ($slugs as $slug) {
        $term = wqs_legacy_exhibition_term_by_slug($slug, 'category');
        if ($term && !is_wp_error($term)) {
            return $term;
        }
    }

    return null;
}

function wqs_legacy_exhibition_term_by_slug($slug, $taxonomy)
{
    global $wpdb;

    $term_id = $wpdb->get_var($wpdb->prepare(
        "SELECT t.term_id
         FROM {$wpdb->terms} t
         INNER JOIN {$wpdb->term_taxonomy} tt ON tt.term_id = t.term_id
         WHERE t.slug = %s AND tt.taxonomy = %s
         LIMIT 1",
        $slug,
        $taxonomy
    ));

    return $term_id ? get_term((int) $term_id, $taxonomy) : null;
}

function wqs_legacy_exhibition_set_terms_exact($post_id, $taxonomy, array $term_ids)
{
    global $wpdb;

    $term_ids = array_values(array_unique(array_map('intval', array_filter($term_ids))));
    $term_taxonomy_ids = $wpdb->get_col($wpdb->prepare(
        "SELECT tt.term_taxonomy_id
         FROM {$wpdb->term_relationships} tr
         INNER JOIN {$wpdb->term_taxonomy} tt ON tt.term_taxonomy_id = tr.term_taxonomy_id
         WHERE tr.object_id = %d AND tt.taxonomy = %s",
        $post_id,
        $taxonomy
    ));

    $wpdb->query($wpdb->prepare(
        "DELETE tr
         FROM {$wpdb->term_relationships} tr
         INNER JOIN {$wpdb->term_taxonomy} tt ON tt.term_taxonomy_id = tr.term_taxonomy_id
         WHERE tr.object_id = %d AND tt.taxonomy = %s",
        $post_id,
        $taxonomy
    ));

    foreach ($term_ids as $term_id) {
        $term_taxonomy_id = $wpdb->get_var($wpdb->prepare(
            "SELECT term_taxonomy_id
             FROM {$wpdb->term_taxonomy}
             WHERE term_id = %d AND taxonomy = %s
             LIMIT 1",
            $term_id,
            $taxonomy
        ));

        if ($term_taxonomy_id) {
            $term_taxonomy_ids[] = (int) $term_taxonomy_id;
            $wpdb->insert(
                $wpdb->term_relationships,
                array(
                    'object_id'        => $post_id,
                    'term_taxonomy_id' => (int) $term_taxonomy_id,
                    'term_order'       => 0,
                ),
                array('%d', '%d', '%d')
            );
        }
    }

    clean_object_term_cache($post_id, 'post');
    wp_update_term_count(
        array_values(array_unique(array_map('intval', $term_taxonomy_ids))),
        $taxonomy,
        true
    );
}

function wqs_legacy_exhibition_apply_taxonomies($post_id, $lang, $year)
{
    $category_ids = array();
    $year_term = wqs_legacy_exhibition_term($year);
    if ($year_term && !is_wp_error($year_term)) {
        $category_ids[] = (int) $year_term->term_id;
    }

    if ($lang === 'zh') {
        $original_chinese = wqs_legacy_exhibition_term_by_slug('original-chinese', 'category');
        if ($original_chinese && !is_wp_error($original_chinese)) {
            $category_ids[] = (int) $original_chinese->term_id;
        }
    }

    wqs_legacy_exhibition_set_terms_exact($post_id, 'category', $category_ids);

    $language = wqs_legacy_exhibition_term_by_slug($lang, 'language');
    if ($language && !is_wp_error($language)) {
        wqs_legacy_exhibition_set_terms_exact($post_id, 'language', array((int) $language->term_id));
    }
}

function wqs_legacy_exhibition_upsert($legacy_key, $lang, $title, $content, $year, $date, $dry_run)
{
    global $wpdb;

    $existing = $wpdb->get_col($wpdb->prepare(
        "SELECT DISTINCT p.ID
         FROM {$wpdb->posts} p
         INNER JOIN {$wpdb->postmeta} legacy_key
             ON legacy_key.post_id = p.ID
             AND legacy_key.meta_key = '_wqs_legacy_exhibition_key'
             AND legacy_key.meta_value = %s
         INNER JOIN {$wpdb->postmeta} legacy_lang
             ON legacy_lang.post_id = p.ID
             AND legacy_lang.meta_key = '_wqs_legacy_exhibition_lang'
             AND legacy_lang.meta_value = %s
         WHERE p.post_type = 'post'
         ORDER BY p.ID ASC",
        $legacy_key,
        $lang
    ));

    if (count($existing) > 1 && !$dry_run) {
        foreach (array_slice($existing, 1) as $duplicate_id) {
            wp_delete_post((int) $duplicate_id, true);
        }
        $existing = array($existing[0]);
    }

    $post_data = array(
        'ID'           => $existing ? (int) $existing[0] : 0,
        'post_type'    => 'post',
        'post_status'  => 'publish',
        'post_title'   => $title,
        'post_name'    => sanitize_title('exhibition-' . $legacy_key . '-' . $lang),
        'post_content' => $content,
        'post_date'    => $date,
    );

    if ($dry_run) {
        echo sprintf("[%s] %s | %s | %d images\n", strtoupper($lang), $year, $title, substr_count($content, '<img'));
        return 0;
    }

    $post_id = wp_insert_post(wp_slash($post_data), true);
    if (is_wp_error($post_id)) {
        throw new RuntimeException($post_id->get_error_message());
    }

    update_post_meta($post_id, '_wqs_legacy_exhibition_key', $legacy_key);
    update_post_meta($post_id, '_wqs_legacy_exhibition_lang', $lang);
    update_post_meta($post_id, '_wqs_content_type', 'exhibition');
    wqs_legacy_exhibition_apply_taxonomies($post_id, $lang, $year);

    return $post_id;
}

$english_query = $legacy_db->query(
    "SELECT id, title, alias, created, CONCAT(introtext, `fulltext`) AS content
     FROM jos_content
     WHERE state = 1 AND catid = 4
     ORDER BY ordering, id"
);

$translation_query = $legacy_db->query(
    "SELECT reference_id,
        MAX(CASE WHEN reference_field = 'title' THEN value END) AS title,
        CONCAT(
            MAX(CASE WHEN reference_field = 'introtext' THEN value END),
            MAX(CASE WHEN reference_field = 'fulltext' THEN value END)
        ) AS content
     FROM jos_jf_content
     WHERE reference_table = 'content' AND language_id = 2
     GROUP BY reference_id"
);

$translations = array();
foreach ($translation_query as $translation) {
    $translations[(int) $translation['reference_id']] = $translation;
}

$created = 0;
foreach ($english_query as $article) {
    if (!preg_match('/^(\d{2,4}(?:-\d{2,4})?)/', $article['alias'], $year_match)) {
        continue;
    }

    $year = $year_match[1];
    $english_groups = wqs_legacy_exhibition_parse_groups($article['content'], $article['title']);
    $translation = isset($translations[(int) $article['id']]) ? $translations[(int) $article['id']] : null;
    $chinese_groups = $translation
        ? wqs_legacy_exhibition_parse_groups($translation['content'], $translation['title'])
        : array();

    foreach ($english_groups as $index => $english_group) {
        $legacy_key = (int) $article['id'] . '-' . ($index + 1);
        $year_for_date = (int) substr(wqs_format_archive_year_label($year), 0, 4);
        $post_date = sprintf('%04d-01-01 12:00:00', $year_for_date ?: 2000);

        $english_id = wqs_legacy_exhibition_upsert(
            $legacy_key,
            'en',
            $english_group['title'],
            wqs_legacy_exhibition_content($english_group['images']),
            $year,
            $post_date,
            $dry_run
        );

        $chinese_group = isset($chinese_groups[$index]) ? $chinese_groups[$index] : $english_group;
        if (count($chinese_group['images']) < count($english_group['images'])) {
            $chinese_group['images'] = $english_group['images'];
        }
        $chinese_id = wqs_legacy_exhibition_upsert(
            $legacy_key,
            'zh',
            $chinese_group['title'],
            wqs_legacy_exhibition_content($chinese_group['images']),
            $year,
            $post_date,
            $dry_run
        );

        if (!$dry_run && $english_id && $chinese_id && function_exists('pll_save_post_translations')) {
            pll_save_post_translations(array('en' => $english_id, 'zh' => $chinese_id));
            wqs_legacy_exhibition_apply_taxonomies($english_id, 'en', $year);
            wqs_legacy_exhibition_apply_taxonomies($chinese_id, 'zh', $year);
        }

        $created += 2;
    }
}

echo $dry_run
    ? "Dry run complete: {$created} language records inspected.\n"
    : "Import complete: {$created} language records created or updated.\n";
