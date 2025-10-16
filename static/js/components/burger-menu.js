/**
 * Burger Menu Toggle
 * Керування відкриттям/закриттям навігаційного меню
 * БЕЗ globals, БЕЗ eval, тільки зовнішній JS
 */

(function () {
    'use strict';

    const CLASS_NAV_OPEN = 'nav-open';

    function init() {
        const burgerToggle = document.querySelector('[data-burger-toggle]');
        const navMenu = document.querySelector('[data-nav-menu]');

        if (!burgerToggle || !navMenu) {
            return;
        }

        burgerToggle.addEventListener('click', function () {
            toggleMenu(burgerToggle, navMenu);
        });

        // Закрити меню при кліку на лінк
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(function (link) {
            link.addEventListener('click', function () {
                if (navMenu.classList.contains(CLASS_NAV_OPEN)) {
                    toggleMenu(burgerToggle, navMenu);
                }
            });
        });

        // Закрити меню при натисканні Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && navMenu.classList.contains(CLASS_NAV_OPEN)) {
                toggleMenu(burgerToggle, navMenu);
            }
        });
    }

    function toggleMenu(button, menu) {
        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        const newState = !isExpanded;

        button.setAttribute('aria-expanded', String(newState));

        if (newState) {
            menu.classList.add(CLASS_NAV_OPEN);
            button.setAttribute('aria-label', 'Закрити меню');
        } else {
            menu.classList.remove(CLASS_NAV_OPEN);
            button.setAttribute('aria-label', 'Відкрити меню');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

