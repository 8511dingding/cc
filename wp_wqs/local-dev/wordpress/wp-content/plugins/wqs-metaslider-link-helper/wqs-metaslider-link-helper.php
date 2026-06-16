<?php
/**
 * Plugin Name: WQS MetaSlider Link Helper
 * Description: Adds post and category target pickers to MetaSlider image slides and resolves links per language.
 * Version: 1.1.0
 * Author: WQS
 * Text Domain: wqs-metaslider-link-helper
 */

if (!defined('ABSPATH')) {
    exit;
}

class WQS_MetaSlider_Link_Helper
{
    const META_TARGET = '_wqs_metaslider_link_target';

    public function __construct()
    {
        add_filter('metaslider_slide_tabs', array($this, 'add_wqs_link_tab'), 20, 4);
        add_action('metaslider_save_image_slide', array($this, 'save_slide_target'), 20, 3);
        add_filter('metaslider_image_slide_attributes', array($this, 'resolve_frontend_slide_url'), 20, 3);
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_assets'));
        add_action('wp_ajax_wqs_ms_link_categories', array($this, 'ajax_search_categories'));
        add_action('wp_ajax_wqs_ms_link_posts', array($this, 'ajax_search_posts'));
    }

    /**
     * Add a dedicated WQS Link tab after MetaSlider's General tab.
     */
    public function add_wqs_link_tab($tabs, $slide, $slider, $settings)
    {
        if (empty($slide->ID)) {
            return $tabs;
        }

        $wqs_tab = array(
            'wqs-link' => array(
                'title' => __('WQS Link', 'wqs-metaslider-link-helper'),
                'content' => $this->render_target_picker((int) $slide->ID),
            ),
        );

        return $this->insert_tab_after($tabs, 'general', $wqs_tab);
    }

    /**
     * Save the selected WQS target and mirror it into MetaSlider's native URL field.
     */
    public function save_slide_target($slide_id, $slider_id, $fields)
    {
        if (!current_user_can('edit_post', $slide_id)) {
            return;
        }

        if (!array_key_exists('wqs_link_target', $fields)) {
            return;
        }

        $target = $this->sanitize_target($fields['wqs_link_target']);

        if (empty($target)) {
            delete_post_meta($slide_id, self::META_TARGET);
            return;
        }

        update_post_meta($slide_id, self::META_TARGET, $target);

        $url = $this->get_target_url($target);
        if (!empty($url)) {
            update_post_meta($slide_id, 'ml-slider_url', esc_url_raw($url));
        }
    }

    /**
     * Override MetaSlider's URL at render time so bilingual pages link to the matching language.
     */
    public function resolve_frontend_slide_url($slide, $slider_id, $settings)
    {
        if (empty($slide['id'])) {
            return $slide;
        }

        $target = get_post_meta((int) $slide['id'], self::META_TARGET, true);
        if (empty($target)) {
            return $slide;
        }

        $lang = function_exists('pll_current_language') ? pll_current_language('slug') : '';
        $url = $this->get_target_url($target, $lang);

        if (!empty($url)) {
            $slide['url'] = $url;
        }

        return $slide;
    }

    public function enqueue_admin_assets($hook)
    {
        if ($hook !== 'toplevel_page_metaslider') {
            return;
        }

        wp_enqueue_script(
            'wqs-metaslider-link-helper',
            plugins_url('assets/admin.js', __FILE__),
            array(),
            '1.1.0',
            true
        );

        wp_localize_script(
            'wqs-metaslider-link-helper',
            'wqsMetaSliderLinkHelper',
            array(
                'ajaxUrl' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('wqs_ms_link_helper'),
                'strings' => array(
                    'allCategories' => __('All categories', 'wqs-metaslider-link-helper'),
                    'loading' => __('Loading...', 'wqs-metaslider-link-helper'),
                    'manualLink' => __('Using the original MetaSlider link field.', 'wqs-metaslider-link-helper'),
                    'noResults' => __('No results found.', 'wqs-metaslider-link-helper'),
                    'selected' => __('Selected:', 'wqs-metaslider-link-helper'),
                ),
            )
        );

        wp_enqueue_style(
            'wqs-metaslider-link-helper',
            plugins_url('assets/admin.css', __FILE__),
            array(),
            '1.1.0'
        );
    }

    public function ajax_search_categories()
    {
        $this->verify_ajax_request();

        $search = isset($_GET['search']) ? sanitize_text_field(wp_unslash($_GET['search'])) : '';
        $selected = isset($_GET['selected']) ? absint($_GET['selected']) : 0;

        wp_send_json_success(array(
            'items' => $this->get_category_results($search, $selected),
        ));
    }

    public function ajax_search_posts()
    {
        $this->verify_ajax_request();

        $search = isset($_GET['search']) ? sanitize_text_field(wp_unslash($_GET['search'])) : '';
        $category_id = isset($_GET['category']) ? absint($_GET['category']) : 0;
        $selected = isset($_GET['selected']) ? absint($_GET['selected']) : 0;

        wp_send_json_success(array(
            'items' => $this->get_post_results($search, $category_id, $selected),
        ));
    }

    private function render_target_picker($slide_id)
    {
        $selected = get_post_meta($slide_id, self::META_TARGET, true);
        $selected_data = $this->get_target_data($selected);
        $mode = $selected_data['kind'] ? $selected_data['kind'] : 'none';

        ob_start();
        ?>
        <div
            class="wqs-ms-link-helper"
            data-selected-kind="<?php echo esc_attr($selected_data['kind']); ?>"
            data-selected-id="<?php echo esc_attr($selected_data['id']); ?>"
            data-selected-label="<?php echo esc_attr($selected_data['label']); ?>"
            data-selected-url="<?php echo esc_url($selected_data['url']); ?>"
        >
            <input
                type="hidden"
                class="wqs-ms-link-target-value"
                name="attachment[<?php echo esc_attr($slide_id); ?>][wqs_link_target]"
                value="<?php echo esc_attr($selected); ?>"
            />

            <fieldset class="wqs-ms-link-mode">
                <legend><?php esc_html_e('Link target type', 'wqs-metaslider-link-helper'); ?></legend>

                <label>
                    <input
                        type="radio"
                        name="attachment[<?php echo esc_attr($slide_id); ?>][wqs_link_mode]"
                        value="category"
                        <?php checked($mode, 'category'); ?>
                    />
                    <?php esc_html_e('Category', 'wqs-metaslider-link-helper'); ?>
                </label>

                <label>
                    <input
                        type="radio"
                        name="attachment[<?php echo esc_attr($slide_id); ?>][wqs_link_mode]"
                        value="post"
                        <?php checked($mode, 'post'); ?>
                    />
                    <?php esc_html_e('Post', 'wqs-metaslider-link-helper'); ?>
                </label>

                <label>
                    <input
                        type="radio"
                        name="attachment[<?php echo esc_attr($slide_id); ?>][wqs_link_mode]"
                        value="none"
                        <?php checked($mode, 'none'); ?>
                    />
                    <?php esc_html_e('Use MetaSlider URL', 'wqs-metaslider-link-helper'); ?>
                </label>
            </fieldset>

            <div class="wqs-ms-current-target">
                <span class="wqs-ms-current-target__label">
                    <?php esc_html_e('Selected:', 'wqs-metaslider-link-helper'); ?>
                </span>
                <a
                    class="wqs-ms-current-target__link"
                    href="<?php echo esc_url($selected_data['url']); ?>"
                    target="_blank"
                    rel="noopener noreferrer"
                    <?php echo empty($selected_data['url']) ? 'hidden' : ''; ?>
                >
                    <?php echo esc_html($selected_data['label']); ?>
                </a>
                <span class="wqs-ms-current-target__empty" <?php echo empty($selected_data['url']) ? '' : 'hidden'; ?>>
                    <?php esc_html_e('Using the original MetaSlider link field.', 'wqs-metaslider-link-helper'); ?>
                </span>
            </div>

            <div class="wqs-ms-link-panel" data-panel="category">
                <label for="wqs-ms-category-search-<?php echo esc_attr($slide_id); ?>">
                    <?php esc_html_e('Search categories', 'wqs-metaslider-link-helper'); ?>
                </label>
                <input
                    id="wqs-ms-category-search-<?php echo esc_attr($slide_id); ?>"
                    class="wqs-ms-category-search"
                    type="search"
                    placeholder="<?php esc_attr_e('Type to search categories...', 'wqs-metaslider-link-helper'); ?>"
                    autocomplete="off"
                />
                <select class="wqs-ms-category-results" size="9"></select>
            </div>

            <div class="wqs-ms-link-panel" data-panel="post">
                <div class="wqs-ms-filter-grid">
                    <div>
                        <label for="wqs-ms-post-category-search-<?php echo esc_attr($slide_id); ?>">
                            <?php esc_html_e('Filter by category', 'wqs-metaslider-link-helper'); ?>
                        </label>
                        <input
                            id="wqs-ms-post-category-search-<?php echo esc_attr($slide_id); ?>"
                            class="wqs-ms-post-category-search"
                            type="search"
                            placeholder="<?php esc_attr_e('Search categories...', 'wqs-metaslider-link-helper'); ?>"
                            autocomplete="off"
                        />
                        <select class="wqs-ms-post-category-results" size="7"></select>
                    </div>

                    <div>
                        <label for="wqs-ms-post-search-<?php echo esc_attr($slide_id); ?>">
                            <?php esc_html_e('Search posts', 'wqs-metaslider-link-helper'); ?>
                        </label>
                        <input
                            id="wqs-ms-post-search-<?php echo esc_attr($slide_id); ?>"
                            class="wqs-ms-post-search"
                            type="search"
                            placeholder="<?php esc_attr_e('Type to search posts...', 'wqs-metaslider-link-helper'); ?>"
                            autocomplete="off"
                        />
                        <select class="wqs-ms-post-results" size="9"></select>
                    </div>
                </div>
            </div>

            <p class="wqs-ms-link-helper__description">
                <?php esc_html_e('Selecting a WQS target fills MetaSlider\'s Image Link URL automatically. On the public site it will use the matching language when available.', 'wqs-metaslider-link-helper'); ?>
            </p>
        </div>
        <?php
        return ob_get_clean();
    }

    private function insert_tab_after($tabs, $after_key, $new_tabs)
    {
        $result = array();
        $inserted = false;

        foreach ($tabs as $key => $tab) {
            $result[$key] = $tab;

            if ($key === $after_key) {
                foreach ($new_tabs as $new_key => $new_tab) {
                    $result[$new_key] = $new_tab;
                }
                $inserted = true;
            }
        }

        if (!$inserted) {
            foreach ($new_tabs as $new_key => $new_tab) {
                $result[$new_key] = $new_tab;
            }
        }

        return $result;
    }

    private function verify_ajax_request()
    {
        check_ajax_referer('wqs_ms_link_helper', 'nonce');

        $capability = class_exists('MetaSliderPlugin')
            ? apply_filters('metaslider_capability', MetaSliderPlugin::DEFAULT_CAPABILITY_EDIT_SLIDES)
            : 'edit_posts';

        if (!current_user_can($capability)) {
            wp_send_json_error(array('message' => __('Access denied.', 'wqs-metaslider-link-helper')), 403);
        }
    }

    private function get_target_data($target)
    {
        $empty = array(
            'kind' => '',
            'id' => 0,
            'label' => '',
            'url' => '',
        );

        if (!preg_match('/^(post|category):([0-9]+)$/', (string) $target, $matches)) {
            return $empty;
        }

        $kind = $matches[1];
        $id = (int) $matches[2];

        if ($kind === 'post') {
            $post = get_post($id);
            if (!$post || $post->post_status !== 'publish') {
                return $empty;
            }

            return array(
                'kind' => 'post',
                'id' => $id,
                'label' => $this->format_object_label(
                    get_the_title($post),
                    function_exists('pll_get_post_language') ? pll_get_post_language($id, 'slug') : '',
                    $post->post_type,
                    $id
                ),
                'url' => get_permalink($id),
            );
        }

        $term = get_term($id, 'category');
        if (!$term || is_wp_error($term)) {
            return $empty;
        }

        $url = get_term_link($term, 'category');

        return array(
            'kind' => 'category',
            'id' => $id,
            'label' => $this->format_category_label($term),
            'url' => is_wp_error($url) ? '' : $url,
        );
    }

    private function get_category_results($search = '', $selected = 0)
    {
        $terms = get_terms(array(
            'taxonomy' => 'category',
            'hide_empty' => false,
            'orderby' => 'name',
            'order' => 'ASC',
            'number' => 80,
            'search' => $search,
            'lang' => '',
        ));

        if (is_wp_error($terms)) {
            $terms = array();
        }

        if ($selected) {
            $selected_term = get_term($selected, 'category');
            if ($selected_term && !is_wp_error($selected_term)) {
                array_unshift($terms, $selected_term);
            }
        }

        $results = array();
        $seen = array();

        foreach ($terms as $term) {
            if (isset($seen[$term->term_id])) {
                continue;
            }

            $url = get_term_link($term, 'category');
            if (is_wp_error($url)) {
                continue;
            }

            $seen[$term->term_id] = true;
            $results[] = array(
                'id' => (int) $term->term_id,
                'target' => 'category:' . (int) $term->term_id,
                'label' => $this->format_category_label($term),
                'url' => $url,
            );
        }

        return $results;
    }

    private function get_post_results($search = '', $category_id = 0, $selected = 0)
    {
        $query_args = array(
            'post_type' => array('post'),
            'post_status' => 'publish',
            'posts_per_page' => 80,
            'orderby' => 'date',
            'order' => 'DESC',
            'suppress_filters' => false,
            'lang' => '',
        );

        if ($search !== '') {
            $query_args['s'] = $search;
        }

        if ($category_id) {
            $query_args['cat'] = $category_id;
        }

        $query = new WP_Query($query_args);
        $posts = $query->posts;

        if ($selected) {
            $selected_post = get_post($selected);
            if ($selected_post && $selected_post->post_status === 'publish') {
                array_unshift($posts, $selected_post);
            }
        }

        $results = array();
        $seen = array();

        foreach ($posts as $post) {
            if (isset($seen[$post->ID])) {
                continue;
            }

            $url = get_permalink($post);
            if (empty($url)) {
                continue;
            }

            $seen[$post->ID] = true;
            $results[] = array(
                'id' => (int) $post->ID,
                'target' => 'post:' . (int) $post->ID,
                'label' => $this->format_object_label(
                    get_the_title($post),
                    function_exists('pll_get_post_language') ? pll_get_post_language($post->ID, 'slug') : '',
                    $post->post_type,
                    $post->ID
                ),
                'url' => $url,
            );
        }

        wp_reset_postdata();

        return $results;
    }

    private function format_category_label($term)
    {
        $depth = count(get_ancestors($term->term_id, 'category'));
        $prefix = str_repeat('— ', $depth);
        $lang = function_exists('pll_get_term_language') ? pll_get_term_language($term->term_id, 'slug') : '';
        $lang_prefix = $lang ? '[' . strtoupper($lang) . '] ' : '';

        return sprintf('%s%s%s (category #%d)', $prefix, $lang_prefix, $term->name, (int) $term->term_id);
    }

    private function format_object_label($title, $lang, $type, $id)
    {
        $title = html_entity_decode(wp_strip_all_tags($title), ENT_QUOTES, get_bloginfo('charset'));
        $title = trim($title);
        if ($title === '') {
            $title = __('Untitled', 'wqs-metaslider-link-helper');
        }

        $prefix = $lang ? '[' . strtoupper($lang) . '] ' : '';

        return sprintf('%s%s (%s #%d)', $prefix, $title, $type, (int) $id);
    }

    private function sanitize_target($target)
    {
        $target = sanitize_text_field((string) $target);
        if (!preg_match('/^(post|category):([0-9]+)$/', $target, $matches)) {
            return '';
        }

        $kind = $matches[1];
        $id = (int) $matches[2];

        if ($kind === 'post' && get_post_status($id) !== 'publish') {
            return '';
        }

        if ($kind === 'category' && !term_exists($id, 'category')) {
            return '';
        }

        return $kind . ':' . $id;
    }

    private function get_target_url($target, $lang = '')
    {
        if (!preg_match('/^(post|category):([0-9]+)$/', (string) $target, $matches)) {
            return '';
        }

        $kind = $matches[1];
        $id = (int) $matches[2];

        if ($kind === 'post') {
            if ($lang && function_exists('pll_get_post')) {
                $translated_id = pll_get_post($id, $lang);
                if (!empty($translated_id)) {
                    $id = (int) $translated_id;
                }
            }

            $url = get_permalink($id);
            return $url ? $url : '';
        }

        if ($kind === 'category') {
            if ($lang) {
                $id = $this->get_category_id_for_language($id, $lang);
            }

            $url = get_term_link($id, 'category');
            return is_wp_error($url) ? '' : $url;
        }

        return '';
    }

    private function get_category_id_for_language($term_id, $lang)
    {
        if (function_exists('pll_get_term')) {
            $translated_id = pll_get_term($term_id, $lang);
            if (!empty($translated_id)) {
                return (int) $translated_id;
            }
        }

        $term = get_term($term_id, 'category');
        if (!$term || is_wp_error($term) || empty($term->slug)) {
            return $term_id;
        }

        $slug = $term->slug;
        $candidates = array();

        if ($lang === 'en') {
            if (substr($slug, -3) === '-en') {
                return $term_id;
            }

            $base_slug = preg_replace('/-zh$/', '', $slug);
            $candidates[] = $base_slug . '-en';
        } elseif ($lang === 'zh') {
            if (substr($slug, -3) !== '-en') {
                return $term_id;
            }

            $base_slug = substr($slug, 0, -3);
            $candidates[] = $base_slug;
            $candidates[] = $base_slug . '-zh';
        }

        foreach (array_unique($candidates) as $candidate_slug) {
            $candidate = get_term_by('slug', $candidate_slug, 'category');
            if ($candidate && !is_wp_error($candidate)) {
                return (int) $candidate->term_id;
            }
        }

        return $term_id;
    }
}

new WQS_MetaSlider_Link_Helper();
