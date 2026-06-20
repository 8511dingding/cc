<?php
/**
 * Fix for WordPress 7.0 REST API 401 error when setting featured image.
 *
 * The bug: WordPress 7.0 REST API returns 401 (rest_forbidden_context) when
 * requesting media attachments with context=edit, even for admin users.
 * This breaks the "Set featured image" flow in the block editor.
 *
 * Fix: After the REST API response is generated (including error), intercept
 * and if it's a rest_forbidden_context on media for admin, re-fetch with
 * context=view and return that instead.
 *
 * @package WQS_Portfolio
 */
add_filter('rest_request_after_callbacks', function($response, $handler, $request) {
    // Only for WP_Error responses
    if (!is_wp_error($response)) {
        return $response;
    }

    // Only for rest_forbidden_context
    if ($response->get_error_code() !== 'rest_forbidden_context') {
        return $response;
    }

    // Only for media endpoint
    $route = $request->get_route();
    if (strpos($route, '/wp/v2/media/') === false) {
        return $response;
    }

    // Only for context=edit
    if (($request['context'] ?? 'view') !== 'edit') {
        return $response;
    }

    // Only for admin users
    if (!current_user_can('manage_options')) {
        return $response;
    }

    // Get the attachment and verify it exists
    $post_id = $request->get_param('id');
    if (!$post_id) {
        return $response;
    }

    // Get the post object
    $post = get_post((int) $post_id);
    if (!$post || $post->post_type !== 'attachment') {
        return $response;
    }

    // Create a new request with context=view
    $view_request = new WP_REST_Request($request->get_method(), $route);
    $view_request->set_url($request->get_route());
    $view_request->set_param('id', $post_id);
    $view_request->set_param('context', 'view');

    // Merge other params
    $params = $request->get_query_params();
    foreach ($params as $key => $value) {
        if ($key !== 'context' && $key !== 'id') {
            $view_request->set_param($key, $value);
        }
    }

    // Dispatch with context=view (which should work)
    remove_filter('rest_request_after_callbacks', __FUNCTION__);
    $view_response = rest_do_request($view_request);
    add_filter('rest_request_after_callbacks', __FUNCTION__);

    if ($view_response && !is_wp_error($view_response)) {
        return $view_response;
    }

    return $response;
}, 10, 3);
