(function() {
    'use strict';

    var header = document.getElementById('masthead');

    function updateHeader() {
        if (header) {
            header.classList.toggle('is-compact', window.scrollY > 48);
        }
    }

    function updateProgress(rail) {
        var progress = rail.parentElement.querySelector('.wqs-home-rail__progress span');
        if (!progress) {
            return;
        }
        var maxScroll = Math.max(1, rail.scrollWidth - rail.clientWidth);
        var visibleRatio = Math.min(1, rail.clientWidth / rail.scrollWidth);
        var travel = (1 - visibleRatio) * 100;
        var offset = (rail.scrollLeft / maxScroll) * travel;
        progress.style.width = (visibleRatio * 100) + '%';
        progress.style.transform = 'translateX(' + (offset / visibleRatio) + '%)';
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
            rail.scrollBy({
                left: direction * Math.max(320, rail.clientWidth * 0.72),
                behavior: 'smooth'
            });
        });
    });

    updateHeader();
    window.addEventListener('scroll', updateHeader, { passive: true });
    window.addEventListener('resize', function() {
        document.querySelectorAll('.wqs-home-rail').forEach(updateProgress);
    });
})();
