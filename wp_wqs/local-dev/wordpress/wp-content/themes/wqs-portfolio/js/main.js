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

        initTitleMotion();
        initBackToTop();
    }

    function initBackToTop() {
        var button = document.querySelector('.wqs-back-to-top');
        if (!button) {
            return;
        }

        var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        var ticking = false;

        function updateButton() {
            var pageIsLong = document.documentElement.scrollHeight > window.innerHeight * 1.15;
            var shouldShow = pageIsLong && window.scrollY > window.innerHeight * 0.55;
            button.classList.toggle('is-visible', shouldShow);
            button.tabIndex = shouldShow ? 0 : -1;
            ticking = false;
        }

        function requestUpdate() {
            if (!ticking) {
                ticking = true;
                window.requestAnimationFrame(updateButton);
            }
        }

        function easeOutQuart(progress) {
            return 1 - Math.pow(1 - progress, 4);
        }

        function scrollToTop() {
            var startY = window.scrollY;
            if (startY <= 0) {
                return;
            }

            if (reduceMotion.matches) {
                window.scrollTo(0, 0);
                return;
            }

            var duration = Math.min(950, Math.max(480, startY * 0.22));
            var startTime = performance.now();

            function step(now) {
                var progress = Math.min(1, (now - startTime) / duration);
                window.scrollTo(0, Math.round(startY * (1 - easeOutQuart(progress))));

                if (progress < 1) {
                    window.requestAnimationFrame(step);
                } else {
                    button.blur();
                }
            }

            window.requestAnimationFrame(step);
        }

        button.addEventListener('click', scrollToTop);
        window.addEventListener('scroll', requestUpdate, { passive: true });
        window.addEventListener('resize', requestUpdate);
        window.addEventListener('load', requestUpdate, { once: true });
        requestUpdate();
    }

    function initTitleMotion() {
        var sectionTitles = [
            'photography',
            'exhibition',
            'exhibitions',
            'reviews',
            'shooting',
            'biography',
            'contact',
            '摄影',
            '展览',
            '评论',
            '工作照',
            '简历',
            '联系'
        ];
        var titleSelector = [
            '.wqs-home-section__header h2',
            '.archive-header h1',
            '.works-archive-header h1',
            '.page-header h1'
        ].join(',');

        document.querySelectorAll(titleSelector).forEach(function(title) {
            var text = title.textContent.trim();
            if (sectionTitles.indexOf(text.toLowerCase()) === -1 && sectionTitles.indexOf(text) === -1) {
                return;
            }

            title.classList.add('wqs-type-title');
            title.setAttribute('aria-label', text);
            title.textContent = '';

            Array.from(text).forEach(function(character, index) {
                var span = document.createElement('span');
                span.className = 'wqs-type-title__char';
                span.setAttribute('aria-hidden', 'true');
                span.style.setProperty('--wqs-char-index', index);
                span.textContent = character === ' ' ? '\u00a0' : character;
                title.appendChild(span);
            });
        });

        document.querySelectorAll('.single-works-header h1').forEach(function(title) {
            var wrapper = document.createElement('span');
            wrapper.className = 'wqs-title-reveal__inner';
            while (title.firstChild) {
                wrapper.appendChild(title.firstChild);
            }
            title.appendChild(wrapper);
            title.classList.add('wqs-title-reveal');
        });

        var animatedTitles = document.querySelectorAll('.wqs-type-title, .wqs-title-reveal');
        if (!animatedTitles.length) {
            return;
        }

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
            animatedTitles.forEach(function(title) {
                title.classList.add('is-visible');
            });
            return;
        }

        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (!entry.isIntersecting) {
                    return;
                }
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.2 });

        animatedTitles.forEach(function(title) {
            observer.observe(title);
        });
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
