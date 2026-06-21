<?php
/**
 * Cinematic Archive homepage.
 *
 * @package WQS_Portfolio
 */
?>
<main id="main-content" class="wqs-homepage wqs-homepage--cinematic">
    <?php wqs_render_home_hero('cinematic'); ?>
    <?php wqs_render_home_search(true); ?>
    <div class="wqs-home-shell">
        <?php wqs_render_home_rail('photography', wqs_home_label('photography'), 14); ?>
        <?php wqs_render_home_rail('exhibitions', wqs_home_label('exhibitions'), 12); ?>
        <?php wqs_render_home_shooting(); ?>
    </div>
    <?php wqs_render_home_reviews('', true); ?>
</main>
