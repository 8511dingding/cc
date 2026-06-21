<?php
/**
 * WQS editor usability improvements.
 *
 * @package WQS_Portfolio
 */

defined('ABSPATH') || exit;

/**
 * Register the original content creation time for REST-backed block editing.
 */
function wqs_editor_tools_register_created_at_meta()
{
    register_post_meta(
        'post',
        '_wqs_created_at',
        array(
            'type'              => 'string',
            'single'            => true,
            'show_in_rest'      => true,
            'sanitize_callback' => 'wqs_editor_tools_sanitize_created_at',
            'auth_callback'     => static function () {
                return current_user_can('edit_posts');
            },
        )
    );

    register_post_meta(
        'post',
        '_wqs_creation_year',
        array(
            'type'              => 'integer',
            'single'            => true,
            'show_in_rest'      => true,
            'sanitize_callback' => 'wqs_editor_tools_sanitize_creation_year',
            'auth_callback'     => static function () {
                return current_user_can('edit_posts');
            },
        )
    );
}
add_action('init', 'wqs_editor_tools_register_created_at_meta');

/**
 * Normalize a local date-time value for storage.
 */
function wqs_editor_tools_sanitize_created_at($value)
{
    $value = trim((string) $value);
    if ($value === '') {
        return '';
    }

    $date = date_create(str_replace('T', ' ', $value), wp_timezone());
    return $date ? $date->format('Y-m-d H:i:s') : '';
}

/**
 * Validate the exact year used by archive menus, filters, and list displays.
 */
function wqs_editor_tools_sanitize_creation_year($value)
{
    $year = absint($value);
    $maximum_year = (int) current_time('Y') + 10;

    return $year >= 1900 && $year <= $maximum_year ? $year : 0;
}

/**
 * Preserve a creation time independently from later publication changes.
 */
function wqs_editor_tools_initialize_created_at($post_id, $post, $update)
{
    if (
        wp_is_post_revision($post_id) ||
        wp_is_post_autosave($post_id) ||
        $post->post_type !== 'post'
    ) {
        return;
    }

    if (get_post_meta($post_id, '_wqs_created_at', true) === '') {
        update_post_meta($post_id, '_wqs_created_at', $post->post_date);
    }

    if (get_post_meta($post_id, '_wqs_creation_year', true) === '') {
        update_post_meta($post_id, '_wqs_creation_year', (int) substr($post->post_date, 0, 4));
    }
}
add_action('save_post_post', 'wqs_editor_tools_initialize_created_at', 10, 3);

/**
 * Ensure Polylang's block editor autocomplete dependency is loaded first.
 */
function wqs_editor_tools_fix_polylang_dependencies()
{
    global $wp_scripts;

    if (
        !isset($wp_scripts->registered['pll_block-editor']) ||
        in_array('jquery-ui-autocomplete', $wp_scripts->registered['pll_block-editor']->deps, true)
    ) {
        return;
    }

    $wp_scripts->registered['pll_block-editor']->deps[] = 'jquery-ui-autocomplete';
}
add_action('admin_enqueue_scripts', 'wqs_editor_tools_fix_polylang_dependencies', 20);

/**
 * Load the editor and post-list enhancements.
 */
function wqs_editor_tools_enqueue_assets($hook_suffix)
{
    $screen = get_current_screen();
    if (!$screen || $screen->post_type !== 'post') {
        return;
    }

    $is_editor = in_array($hook_suffix, array('post.php', 'post-new.php'), true);
    $is_list = $hook_suffix === 'edit.php';
    if (!$is_editor && !$is_list) {
        return;
    }

    $base_url = content_url('mu-plugins/assets/');
    $base_path = WPMU_PLUGIN_DIR . '/assets/';
    $dependencies = array('jquery', 'jquery-ui-autocomplete');

    if ($is_editor) {
        $dependencies = array_merge(
            $dependencies,
            array('wp-components', 'wp-data', 'wp-edit-post', 'wp-element', 'wp-i18n', 'wp-plugins')
        );
    }

    wp_enqueue_script(
        'wqs-editor-tools',
        $base_url . 'wqs-editor-tools.js',
        $dependencies,
        (string) filemtime($base_path . 'wqs-editor-tools.js'),
        true
    );
    wp_enqueue_style(
        'wqs-editor-tools',
        $base_url . 'wqs-editor-tools.css',
        array(),
        (string) filemtime($base_path . 'wqs-editor-tools.css')
    );

    $post_id = 0;
    if ($is_editor && isset($_GET['post'])) {
        $post_id = absint($_GET['post']);
    }

    $language = $post_id && function_exists('pll_get_post_language')
        ? pll_get_post_language($post_id, 'slug')
        : '';
    $categories_by_language = array(
        'all' => wqs_editor_tools_get_categories_for_language(''),
    );

    if (function_exists('pll_languages_list')) {
        foreach (pll_languages_list(array('fields' => 'slug')) as $language_slug) {
            $categories_by_language[$language_slug] = wqs_editor_tools_get_categories_for_language($language_slug);
        }
    }

    wp_localize_script(
        'wqs-editor-tools',
        'wqsEditorTools',
        array(
            'ajaxUrl'          => admin_url('admin-ajax.php'),
            'adminPostUrl'     => admin_url('post.php'),
            'postId'           => $post_id,
            'postType'         => 'post',
            'language'         => $language,
            'categories'       => $categories_by_language,
            'linkNonce'        => wp_create_nonce('wqs_link_post_translation'),
            'isEditor'         => $is_editor,
            'isList'           => $is_list,
            'focusTranslation' => isset($_GET['wqs_link_translation']),
            'currentTime'      => current_time('Y-m-d H:i:s'),
        )
    );
}
add_action('admin_enqueue_scripts', 'wqs_editor_tools_enqueue_assets', 30);

/**
 * Add a clear translation action to each row in the post list.
 */
function wqs_editor_tools_post_row_actions($actions, $post)
{
    if (
        $post->post_type !== 'post' ||
        !current_user_can('edit_post', $post->ID) ||
        !function_exists('pll_get_post_language') ||
        !function_exists('pll_languages_list')
    ) {
        return $actions;
    }

    $current_language = pll_get_post_language($post->ID, 'slug');
    $languages = pll_languages_list(array('fields' => 'slug'));
    $target_language = '';

    foreach ($languages as $language) {
        if ($language !== $current_language) {
            $target_language = $language;
            break;
        }
    }

    if (!$target_language) {
        return $actions;
    }

    $translation_id = function_exists('pll_get_post')
        ? (int) pll_get_post($post->ID, $target_language)
        : 0;

    if ($translation_id && current_user_can('edit_post', $translation_id)) {
        $actions['wqs_translation'] = sprintf(
            '<a href="%s">%s</a>',
            esc_url(get_edit_post_link($translation_id)),
            esc_html($target_language === 'zh' ? '编辑中文版本' : '编辑英文版本')
        );
    } else {
        $actions['wqs_translation'] = sprintf(
            '<a href="%s">%s</a>',
            esc_url(add_query_arg('wqs_link_translation', '1', get_edit_post_link($post->ID))),
            esc_html($target_language === 'zh' ? '关联已有中文文章' : '关联已有英文文章')
        );
    }

    return $actions;
}
add_filter('post_row_actions', 'wqs_editor_tools_post_row_actions', 20, 2);

/**
 * Return all categories for one editor language.
 */
function wqs_editor_tools_get_categories_for_language($language = '')
{
    $args = array(
        'taxonomy'   => 'category',
        'hide_empty' => false,
        'orderby'    => 'name',
        'order'      => 'ASC',
        'number'     => 0,
    );

    $language = sanitize_key((string) $language);
    if ($language !== '') {
        $args['lang'] = $language;
    }

    $terms = get_terms($args);
    if (is_wp_error($terms)) {
        return array();
    }

    return array_map(
        static function ($term) {
            return array(
                'id'     => (int) $term->term_id,
                'name'   => $term->name,
                'slug'   => $term->slug,
                'parent' => (int) $term->parent,
                'count'  => (int) $term->count,
            );
        },
        $terms
    );
}

/**
 * Link an existing post as the selected language translation immediately.
 */
function wqs_editor_tools_link_post_translation()
{
    check_ajax_referer('wqs_link_post_translation', 'nonce');

    $post_id = isset($_POST['post_id']) ? absint($_POST['post_id']) : 0;
    $translation_id = isset($_POST['translation_id']) ? absint($_POST['translation_id']) : 0;
    $target_language = isset($_POST['target_language'])
        ? sanitize_key(wp_unslash($_POST['target_language']))
        : '';

    if (
        !$post_id ||
        !$translation_id ||
        !$target_language ||
        !current_user_can('edit_post', $post_id) ||
        !current_user_can('edit_post', $translation_id)
    ) {
        wp_send_json_error(array('message' => '没有权限关联这两篇文章。'), 403);
    }

    $post = get_post($post_id);
    $translation = get_post($translation_id);
    if (
        !$post instanceof WP_Post ||
        !$translation instanceof WP_Post ||
        $post->post_type !== $translation->post_type ||
        $post_id === $translation_id
    ) {
        wp_send_json_error(array('message' => '所选文章不能作为当前文章的翻译。'), 400);
    }

    if (
        !function_exists('pll_get_post_language') ||
        !function_exists('pll_set_post_language') ||
        !function_exists('pll_get_post_translations') ||
        !function_exists('pll_save_post_translations')
    ) {
        wp_send_json_error(array('message' => 'Polylang 翻译功能当前不可用。'), 500);
    }

    $source_language = pll_get_post_language($post_id, 'slug');
    if (!$source_language || $source_language === $target_language) {
        wp_send_json_error(array('message' => '文章语言设置不正确。'), 400);
    }

    pll_set_post_language($translation_id, $target_language);

    $translations = pll_get_post_translations($post_id);
    $translations[$source_language] = $post_id;
    $translations[$target_language] = $translation_id;
    pll_save_post_translations($translations);

    wp_send_json_success(
        array(
            'message' => '已关联现有翻译文章。',
            'editUrl' => get_edit_post_link($translation_id, 'raw'),
        )
    );
}
add_action('wp_ajax_wqs_link_post_translation', 'wqs_editor_tools_link_post_translation');

/**
 * Let Polylang return enough matching existing articles for practical searches.
 */
function wqs_editor_tools_polylang_search_limit($args)
{
    $args['numberposts'] = 50;
    return $args;
}
add_filter('pll_ajax_posts_not_translated_args', 'wqs_editor_tools_polylang_search_limit');
