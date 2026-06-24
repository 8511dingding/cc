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
        initArticleLightbox();
        initMissingTranslationNotice();
    }

    function initMissingTranslationNotice() {
        var buttons = document.querySelectorAll('[data-wqs-missing-translation="1"]');
        if (!buttons.length) {
            return;
        }

        var dialog = null;
        var messageNode = null;
        var closeButton = null;
        var lastTrigger = null;

        function ensureDialog() {
            if (dialog) {
                return;
            }

            dialog = document.createElement('dialog');
            dialog.className = 'wqs-language-notice';
            dialog.setAttribute('aria-label', 'Language notice');
            dialog.innerHTML = [
                '<div class="wqs-language-notice__surface">',
                '<p class="wqs-language-notice__message"></p>',
                '<button class="wqs-language-notice__close" type="button">OK</button>',
                '</div>'
            ].join('');
            document.body.appendChild(dialog);

            messageNode = dialog.querySelector('.wqs-language-notice__message');
            closeButton = dialog.querySelector('.wqs-language-notice__close');

            closeButton.addEventListener('click', closeDialog);
            dialog.addEventListener('click', function(event) {
                if (event.target === dialog) {
                    closeDialog();
                }
            });
            dialog.addEventListener('close', function() {
                document.documentElement.classList.remove('wqs-language-notice-open');
                if (lastTrigger && typeof lastTrigger.focus === 'function') {
                    lastTrigger.focus({ preventScroll: true });
                }
            });
        }

        function openDialog(message, trigger) {
            ensureDialog();
            lastTrigger = trigger;
            messageNode.textContent = message;
            document.documentElement.classList.add('wqs-language-notice-open');

            if (typeof dialog.showModal === 'function') {
                dialog.showModal();
                closeButton.focus({ preventScroll: true });
                return;
            }

            window.alert(message);
            closeDialog();
        }

        function closeDialog() {
            if (dialog && dialog.open) {
                dialog.close();
            } else {
                document.documentElement.classList.remove('wqs-language-notice-open');
            }
        }

        buttons.forEach(function(button) {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                openDialog(button.dataset.wqsMissingTranslationMessage || button.textContent, button);
            });
        });
    }

    function initArticleLightbox() {
        var content = document.querySelector('.single-works-content');
        if (!content || typeof HTMLDialogElement === 'undefined') {
            return;
        }

        var imagePattern = /\.(?:avif|gif|jpe?g|png|webp)(?:$|[?#])/i;
        var items = [];

        content.querySelectorAll('img:not(.wp-smiley)').forEach(function(image) {
            var link = image.closest('a[href]');
            var linkHref = link ? link.href : '';
            if (link && !imagePattern.test(linkHref)) {
                return;
            }

            var source = linkHref
                || image.getAttribute('data-orig-file')
                || image.getAttribute('data-large-file')
                || image.currentSrc
                || image.src;

            if (!source) {
                return;
            }

            var figure = image.closest('figure');
            var captionNode = figure ? figure.querySelector('figcaption') : null;
            var trigger = link || image;

            items.push({
                source: source,
                alt: image.alt || '',
                caption: captionNode ? captionNode.textContent.trim() : (image.alt || ''),
                trigger: trigger
            });

            trigger.classList.add('wqs-lightbox-trigger');
            if (!link) {
                trigger.tabIndex = 0;
                trigger.setAttribute('role', 'button');
                trigger.setAttribute('aria-label', image.alt
                    ? 'Open image: ' + image.alt
                    : 'Open image');
            }
        });

        if (!items.length) {
            return;
        }

        var dialog = document.createElement('dialog');
        dialog.className = 'wqs-article-lightbox';
        dialog.setAttribute('aria-label', 'Image viewer');
        dialog.innerHTML = [
            '<div class="wqs-article-lightbox__stage">',
            '<button class="wqs-article-lightbox__close" type="button" aria-label="Close image viewer"><span aria-hidden="true">&times;</span></button>',
            '<button class="wqs-article-lightbox__nav wqs-article-lightbox__nav--prev" type="button" aria-label="Previous image"><span aria-hidden="true">&larr;</span></button>',
            '<figure class="wqs-article-lightbox__figure">',
            '<img class="wqs-article-lightbox__image" alt="">',
            '<figcaption class="wqs-article-lightbox__meta">',
            '<span class="wqs-article-lightbox__caption"></span>',
            '<span class="wqs-article-lightbox__counter"></span>',
            '</figcaption>',
            '</figure>',
            '<button class="wqs-article-lightbox__nav wqs-article-lightbox__nav--next" type="button" aria-label="Next image"><span aria-hidden="true">&rarr;</span></button>',
            '</div>'
        ].join('');
        document.body.appendChild(dialog);

        var lightboxImage = dialog.querySelector('.wqs-article-lightbox__image');
        var caption = dialog.querySelector('.wqs-article-lightbox__caption');
        var counter = dialog.querySelector('.wqs-article-lightbox__counter');
        var previousButton = dialog.querySelector('.wqs-article-lightbox__nav--prev');
        var nextButton = dialog.querySelector('.wqs-article-lightbox__nav--next');
        var closeButton = dialog.querySelector('.wqs-article-lightbox__close');
        var stage = dialog.querySelector('.wqs-article-lightbox__stage');
        var currentIndex = 0;
        var lastTrigger = null;
        var renderTimer = null;

        function preload(index) {
            if (items.length < 2) {
                return;
            }
            var preloadImage = new Image();
            preloadImage.src = items[(index + items.length) % items.length].source;
        }

        function render(index) {
            currentIndex = (index + items.length) % items.length;
            var item = items[currentIndex];

            lightboxImage.classList.add('is-changing');
            window.clearTimeout(renderTimer);
            renderTimer = window.setTimeout(function() {
                lightboxImage.src = item.source;
                lightboxImage.alt = item.alt;
                caption.textContent = item.caption;
                caption.hidden = !item.caption;
                counter.textContent = (currentIndex + 1) + ' / ' + items.length;
                lightboxImage.classList.remove('is-changing');
            }, 100);

            previousButton.hidden = items.length < 2;
            nextButton.hidden = items.length < 2;
            preload(currentIndex + 1);
            preload(currentIndex - 1);
        }

        function open(index, trigger) {
            lastTrigger = trigger;
            render(index);
            if (dialog.open) {
                return;
            }
            document.documentElement.classList.add('wqs-lightbox-open');
            dialog.showModal();
            closeButton.focus({ preventScroll: true });
        }

        function close() {
            if (dialog.open) {
                dialog.close();
            }
        }

        items.forEach(function(item, index) {
            item.trigger.addEventListener('click', function(event) {
                event.preventDefault();
                open(index, item.trigger);
            });

            if (item.trigger.tagName !== 'A') {
                item.trigger.addEventListener('keydown', function(event) {
                    if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        open(index, item.trigger);
                    }
                });
            }
        });

        previousButton.addEventListener('click', function() {
            render(currentIndex - 1);
        });
        nextButton.addEventListener('click', function() {
            render(currentIndex + 1);
        });
        closeButton.addEventListener('click', close);
        stage.addEventListener('click', function(event) {
            if (!event.target.closest('.wqs-article-lightbox__image, .wqs-article-lightbox__nav, .wqs-article-lightbox__close')) {
                close();
            }
        });
        dialog.addEventListener('click', function(event) {
            if (event.target === dialog) {
                close();
            }
        });
        dialog.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowLeft' && items.length > 1) {
                event.preventDefault();
                render(currentIndex - 1);
            } else if (event.key === 'ArrowRight' && items.length > 1) {
                event.preventDefault();
                render(currentIndex + 1);
            }
        });
        dialog.addEventListener('close', function() {
            document.documentElement.classList.remove('wqs-lightbox-open');
            lightboxImage.removeAttribute('src');
            if (lastTrigger) {
                lastTrigger.focus({ preventScroll: true });
            }
        });
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

})();
