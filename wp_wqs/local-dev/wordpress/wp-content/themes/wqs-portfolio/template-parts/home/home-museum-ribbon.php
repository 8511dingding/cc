<?php
/**
 * Museum Ribbon homepage.
 *
 * @package WQS_Portfolio
 */
?>
<main id="main-content" class="wqs-homepage wqs-homepage--museum">
    <?php wqs_render_home_hero('museum'); ?>
    <div class="wqs-home-shell">
        <?php wqs_render_home_search(false); ?>
        <?php wqs_render_home_rail('photography', wqs_home_label('photography'), 14); ?>
        <?php wqs_render_home_rail('exhibitions', wqs_home_label('exhibitions'), 12); ?>
        <?php wqs_render_home_shooting(); ?>
        <?php wqs_render_home_reviews(); ?>
        <?php wqs_render_home_social_accounts(); ?>
    </div>
</main>
