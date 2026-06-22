(function() {
    'use strict';

    var header = document.getElementById('masthead');

    function updateHeader() {
        if (header) {
            header.classList.toggle('is-compact', window.scrollY > 48);
        }
    }

    function updateProgress(rail) {
        var progressTrack = rail.parentElement.querySelector('.wqs-home-rail__progress');
        var progress = progressTrack ? progressTrack.querySelector('span') : null;
        if (!progressTrack || !progress) {
            return;
        }
        var contentWidth = Number(rail.dataset.loopWidth) || rail.scrollWidth;
        var currentScroll = contentWidth ? rail.scrollLeft % contentWidth : rail.scrollLeft;
        var maxScroll = Math.max(1, contentWidth - rail.clientWidth);
        var visibleRatio = Math.min(1, rail.clientWidth / contentWidth);
        var travel = (1 - visibleRatio) * 100;
        var offset = (Math.min(currentScroll, maxScroll) / maxScroll) * travel;
        progress.style.width = (visibleRatio * 100) + '%';
        progress.style.transform = 'translateX(' + (offset / visibleRatio) + '%)';
        progressTrack.setAttribute('aria-valuenow', Math.round((Math.min(currentScroll, maxScroll) / maxScroll) * 100));
    }

    function stabilizeSlider() {
        var hero = document.querySelector('.wqs-home-hero');
        if (!hero) {
            return;
        }

        hero.querySelectorAll('.metaslider > div, .metaslider > div > div').forEach(function(element) {
            element.style.height = '100%';
        });

        hero.querySelectorAll('img').forEach(function(image) {
            image.addEventListener('error', function() {
                var slide = image.closest('li');
                if (slide) {
                    slide.hidden = true;
                }
                var nextSlide = hero.querySelector('.slides > li:not([hidden]) img');
                if (nextSlide && nextSlide !== image) {
                    nextSlide.closest('li').style.display = 'block';
                }
            }, { once: true });
        });

        var captionMap = {};
        try {
            captionMap = JSON.parse(hero.dataset.slideCaptions || '{}');
        } catch (error) {
            captionMap = {};
        }

        hero.querySelectorAll('.slides > li').forEach(function(slide) {
            var link = slide.querySelector('.metaslider_image_link');
            if (!link || slide.querySelector('.wqs-slider-caption')) {
                return;
            }
            var key = link.href.replace(/\/$/, '');
            var caption = captionMap[key];
            if (!caption) {
                return;
            }
            var overlay = document.createElement('span');
            overlay.className = 'wqs-slider-caption';
            overlay.innerHTML = '<strong></strong><small></small>';
            overlay.querySelector('strong').textContent = caption.title;
            overlay.querySelector('small').textContent = caption.year;
            link.appendChild(overlay);
        });
    }

    function initAutoRails() {
        var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        document.querySelectorAll('.wqs-home-rail').forEach(function(rail) {
            var originalCards = Array.from(rail.children);
            if (originalCards.length < 2) {
                return;
            }

            originalCards.forEach(function(card) {
                var clone = card.cloneNode(true);
                clone.classList.add('is-loop-clone');
                clone.setAttribute('aria-hidden', 'true');
                clone.querySelectorAll('a, button, input, select, textarea').forEach(function(control) {
                    control.setAttribute('tabindex', '-1');
                });
                rail.appendChild(clone);
            });

            if (!reducedMotion) {
                rail.classList.add('is-auto-moving');
            }
            var paused = false;
            var inViewport = true;
            var dragging = false;
            var dragMoved = false;
            var dragStartX = 0;
            var dragStartScroll = 0;
            var resumeTimer = 0;
            var lastTime = 0;
            var loopWidth = 0;

            function measure() {
                var firstClone = rail.querySelector('.is-loop-clone');
                loopWidth = firstClone ? firstClone.offsetLeft - rail.firstElementChild.offsetLeft : rail.scrollWidth / 2;
                rail.dataset.loopWidth = loopWidth;
                updateProgress(rail);
            }

            function pauseTemporarily() {
                paused = true;
                window.clearTimeout(resumeTimer);
                resumeTimer = window.setTimeout(function() {
                    paused = false;
                }, 2800);
            }

            function setScrollFromRatio(ratio) {
                var maxScroll = Math.max(1, loopWidth - rail.clientWidth);
                rail.scrollLeft = Math.max(0, Math.min(1, ratio)) * maxScroll;
                updateProgress(rail);
            }

            function tick(time) {
                if (!lastTime) {
                    lastTime = time;
                }
                var elapsed = Math.min(40, time - lastTime);
                lastTime = time;

                if (!reducedMotion && !paused && !dragging && inViewport && !document.hidden && loopWidth > 0) {
                    rail.scrollLeft += elapsed * 0.032;
                    if (rail.scrollLeft >= loopWidth) {
                        rail.scrollLeft -= loopWidth;
                    }
                }
                window.requestAnimationFrame(tick);
            }

            rail.addEventListener('mouseenter', function() {
                paused = true;
            });
            rail.addEventListener('mouseleave', function() {
                paused = false;
            });
            rail.addEventListener('focusin', function() {
                paused = true;
            });
            rail.addEventListener('focusout', function() {
                paused = false;
            });
            rail.addEventListener('pointerdown', function(event) {
                if (event.button !== 0) {
                    return;
                }
                dragging = true;
                dragMoved = false;
                dragStartX = event.clientX;
                dragStartScroll = rail.scrollLeft;
                paused = true;
                rail.classList.add('is-dragging');
                rail.setPointerCapture(event.pointerId);
            });
            rail.addEventListener('pointermove', function(event) {
                if (!dragging) {
                    return;
                }
                var distance = event.clientX - dragStartX;
                if (Math.abs(distance) > 4) {
                    dragMoved = true;
                }
                rail.scrollLeft = dragStartScroll - distance;
            });
            rail.addEventListener('pointerup', function(event) {
                if (!dragging) {
                    return;
                }
                dragging = false;
                rail.classList.remove('is-dragging');
                if (rail.hasPointerCapture(event.pointerId)) {
                    rail.releasePointerCapture(event.pointerId);
                }
                pauseTemporarily();
            });
            rail.addEventListener('click', function(event) {
                if (dragMoved) {
                    event.preventDefault();
                    event.stopPropagation();
                    dragMoved = false;
                }
            }, true);
            rail.addEventListener('wheel', pauseTemporarily, { passive: true });
            rail.addEventListener('wqs:pause', pauseTemporarily);
            window.addEventListener('resize', measure);

            if ('IntersectionObserver' in window) {
                var visibilityObserver = new IntersectionObserver(function(entries) {
                    inViewport = entries[0].isIntersecting;
                }, { threshold: 0.05 });
                visibilityObserver.observe(rail);
            }

            measure();
            window.requestAnimationFrame(tick);

            var progressTrack = rail.parentElement.querySelector('.wqs-home-rail__progress');
            if (progressTrack) {
                function seekFromPointer(event) {
                    var rect = progressTrack.getBoundingClientRect();
                    setScrollFromRatio((event.clientX - rect.left) / rect.width);
                }

                progressTrack.addEventListener('pointerdown', function(event) {
                    paused = true;
                    progressTrack.classList.add('is-dragging');
                    progressTrack.setPointerCapture(event.pointerId);
                    seekFromPointer(event);
                });
                progressTrack.addEventListener('pointermove', function(event) {
                    if (progressTrack.hasPointerCapture(event.pointerId)) {
                        seekFromPointer(event);
                    }
                });
                progressTrack.addEventListener('pointerup', function(event) {
                    progressTrack.classList.remove('is-dragging');
                    if (progressTrack.hasPointerCapture(event.pointerId)) {
                        progressTrack.releasePointerCapture(event.pointerId);
                    }
                    pauseTemporarily();
                });
                progressTrack.addEventListener('keydown', function(event) {
                    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') {
                        return;
                    }
                    event.preventDefault();
                    var direction = event.key === 'ArrowRight' ? 1 : -1;
                    rail.scrollLeft += direction * Math.max(160, rail.clientWidth * 0.2);
                    pauseTemporarily();
                });
            }
        });
    }

    document.querySelectorAll('.wqs-home-rail').forEach(function(rail) {
        updateProgress(rail);
        rail.addEventListener('scroll', function() {
            window.requestAnimationFrame(function() {
                updateProgress(rail);
            });
        }, { passive: true });
    });

    document.querySelectorAll('[data-rail-target]').forEach(function(button) {
        button.addEventListener('click', function() {
            var rail = document.getElementById(button.getAttribute('data-rail-target'));
            if (!rail) {
                return;
            }
            var direction = Number(button.getAttribute('data-direction')) || 1;
            var loopWidth = Number(rail.dataset.loopWidth) || 0;
            var distance = Math.max(320, rail.clientWidth * 0.72);
            rail.dispatchEvent(new CustomEvent('wqs:pause'));
            if (direction < 0 && loopWidth && rail.scrollLeft < distance) {
                rail.scrollLeft += loopWidth;
            }
            rail.scrollTo({ left: rail.scrollLeft + direction * distance, behavior: 'smooth' });
        });
    });

    updateHeader();
    stabilizeSlider();
    initAutoRails();
    window.addEventListener('scroll', updateHeader, { passive: true });
    window.addEventListener('resize', function() {
        document.querySelectorAll('.wqs-home-rail').forEach(updateProgress);
    });
})();
