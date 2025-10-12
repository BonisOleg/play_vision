/**
 * Theme Toggle Button Handler
 * Використовує існуючий ThemeManager для перемикання теми
 */

(function () {
    'use strict';

    function initThemeToggle() {
        const toggleBtn = document.querySelector('[data-theme-toggle]');

        if (!toggleBtn) {
            console.warn('Theme toggle button not found');
            return;
        }

        // Перевірка наявності ThemeManager
        if (typeof window.ThemeManager === 'undefined') {
            console.error('ThemeManager not loaded');
            return;
        }

        // Обробник кліку
        toggleBtn.addEventListener('click', function () {
            window.ThemeManager.toggleTheme();
        });

        // Підказка при hover (accessibility)
        const currentTheme = window.ThemeManager.getTheme();
        updateAriaLabel(toggleBtn, currentTheme);

        // Слухач змін теми для оновлення aria-label
        document.documentElement.addEventListener('themechange', function (e) {
            if (e.detail && e.detail.theme) {
                updateAriaLabel(toggleBtn, e.detail.theme);
            }
        });
    }

    function updateAriaLabel(button, theme) {
        const labels = {
            'light': 'Перемкнути на темну тему',
            'dark': 'Перемкнути на світлу тему',
            'auto': 'Перемкнути тему'
        };
        button.setAttribute('aria-label', labels[theme] || 'Перемкнути тему');
    }

    // Ініціалізація після завантаження DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeToggle);
    } else {
        initThemeToggle();
    }
})();

