<?php
/**
 * Editorial Index homepage.
 *
 * @package WQS_Portfolio
 */
?>
<main id="main-content" class="wqs-homepage wqs-homepage--editorial">
    <?php wqs_render_home_hero('editorial'); ?>
    <div class="wqs-home-shell">
        <?php wqs_render_home_search(false); ?>
        <?php wqs_render_home_rail('photography', wqs_home_label('photography'), 14, '01'); ?>
        <?php wqs_render_home_rail('exhibitions', wqs_home_label('exhibitions'), 12, '02'); ?>
        <?php wqs_render_home_shooting('03'); ?>
        <?php wqs_render_home_reviews('04'); ?>
    </div>
</main>
