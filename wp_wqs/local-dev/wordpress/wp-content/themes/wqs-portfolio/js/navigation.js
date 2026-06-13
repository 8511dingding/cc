/**
 * Navigation Menu
 *
 * @package WQS_Portfolio
 */

(function() {
    'use strict';

    var container, button, menu, links, i, len;

    container = document.getElementById('site-navigation');
    if (!container) {
        return;
    }

    button = container.getElementsByTagName('button')[0];
    menu = container.getElementsByTagName('ul')[0];

    // Hide menu toggle button if menu is empty or missing
    if ('undefined' === typeof menu || !menu.classList.contains('nav-menu')) {
        container.classList.add('menu-empty');
        return;
    }

    menu.classList.add('nav-menu');

    // Toggle button on click
    if (button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleMenu();
        });
    }

    // Get all the links inside the menu
    links = menu.getElementsByTagName('a');

    // Toggle menu on link click (for mobile)
    for (i = 0, len = links.length; i < len; i++) {
        links[i].addEventListener('click', function(e) {
            if (button.classList.contains('toggled')) {
                toggleMenu();
            }
        });
    }

    function toggleMenu() {
        if (-1 !== container.className.indexOf('toggled')) {
            container.classList.remove('toggled');
            button.setAttribute('aria-expanded', 'false');
            button.classList.remove('toggled');
            menu.classList.remove('toggled');
        } else {
            container.classList.add('toggled');
            button.setAttribute('aria-expanded', 'true');
            button.classList.add('toggled');
            menu.classList.add('toggled');
        }
    }

    // Handle focus management for accessibility
    document.addEventListener('click', function(event) {
        var isClickInside = container.contains(event.target);
        if (!isClickInside && container.classList.contains('toggled')) {
            toggleMenu();
        }
    });

    // Handle escape key to close menu
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && container.classList.contains('toggled')) {
            toggleMenu();
            button.focus();
        }
    });
})();