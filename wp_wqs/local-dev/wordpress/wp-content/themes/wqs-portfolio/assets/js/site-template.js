(function() {
    'use strict';

    var header = document.getElementById('masthead');
    if (!header) {
        return;
    }

    function updateHeader() {
        header.classList.toggle('is-compact', window.scrollY > 48);
    }

    updateHeader();
    window.addEventListener('scroll', updateHeader, { passive: true });
})();
