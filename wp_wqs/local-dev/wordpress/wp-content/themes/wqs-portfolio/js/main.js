/**
 * Main JavaScript
 *
 * @package WQS_Portfolio
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', init);

    function init() {
        // Initialize AOS (Animate On Scroll)
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-out-cubic',
                once: true,
                offset: 50,
                disable: window.innerWidth < 768
            });
        }

        // PhotoSwipe is initialized in template files
        // This file handles other interactive features
    }

    /**
     * Debounce utility
     */
    function debounce(func, wait) {
        var timeout;
        return function executedFunction(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Expose for debugging
    window.WQSPortfolio = {
        init: init,
        debounce: debounce
    };

})();