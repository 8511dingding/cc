/**
 * WQS Portfolio Main JavaScript
 *
 * @package WQS_Portfolio
 * @since 1.0.0
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        initPhotoSwipeLightbox();
        initSmoothScroll();
        initMobileMenu();
    }

    /**
     * Initialize PhotoSwipe Lightbox for works gallery
     */
    function initPhotoSwipeLightbox() {
        const gallery = document.querySelector('.pswp-gallery');
        if (!gallery || typeof PhotoSwipeLightbox === 'undefined') {
            return;
        }

        try {
            const lightbox = new PhotoSwipeLightbox({
                gallery: '.pswp-gallery',
                children: '.works-gallery-item',
                pswpModule: () => import('https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/umd/photoswipe-lightbox.esm.js'),
                pswpCSS: 'https://cdn.jsdelivr.net/npm/photoswipe@5.4.4/dist/photoswipe.css',
                padding: { top: 20, bottom: 20, left: 20, right: 20 },
                zoom: true,
                bgOpacity: 0.9,
                showHideAnimation: 'fade',
                maxWidth: 2000,
                maxHeight: 2000,
            });

            // Custom filter to get correct thumbnail bounds
            lightbox.addFilter('thumbBounds', (thumbBounds, data, index) => {
                const img = data.element?.querySelector('img');
                if (img && img.complete && img.naturalWidth > 0) {
                    const rect = img.getBoundingClientRect();
                    thumbBounds.x = rect.left;
                    thumbBounds.y = rect.top;
                    thumbBounds.w = rect.width;
                    thumbBounds.h = rect.height;
                } else if (img) {
                    // Image not loaded yet, wait for it
                    return new Promise(resolve => {
                        if (img.complete && img.naturalWidth > 0) {
                            const rect = img.getBoundingClientRect();
                            resolve({
                                x: rect.left,
                                y: rect.top,
                                w: rect.width,
                                h: rect.height
                            });
                        } else {
                            img.addEventListener('load', () => {
                                const rect = img.getBoundingClientRect();
                                resolve({
                                    x: rect.left,
                                    y: rect.top,
                                    w: rect.width,
                                    h: rect.height
                                });
                            });
                        }
                    });
                }
                return thumbBounds;
            });

            lightbox.on('change', () => {
                // Update data-src with full resolution image
                const currentSlide = lightbox.currSlide;
                if (currentSlide && currentSlide.data.element) {
                    const img = currentSlide.data.element.querySelector('img');
                    const fullSrc = img?.dataset.fullSrc || img?.src;
                    if (fullSrc) {
                        currentSlide.data.src = fullSrc;
                    }
                }
            });

            lightbox.init();

            console.log('PhotoSwipe Lightbox initialized');
        } catch (e) {
            console.warn('PhotoSwipe initialization skipped:', e.message);
        }
    }

    /**
     * Smooth scroll for anchor links
     */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Mobile menu toggle
     */
    function initMobileMenu() {
        const menuToggle = document.querySelector('.menu-toggle');
        const mainNav = document.querySelector('.main-navigation');

        if (menuToggle && mainNav) {
            menuToggle.addEventListener('click', () => {
                mainNav.classList.toggle('toggled');
                menuToggle.classList.toggle('toggled');
            });
        }
    }

    /**
     * Debounce utility function
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Expose functions for debugging
    window.WQSPortfolio = {
        init: init,
        initPhotoSwipeLightbox: initPhotoSwipeLightbox
    };

})();