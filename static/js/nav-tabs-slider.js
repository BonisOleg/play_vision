/**
 * Navigation Tabs Animated Slider
 * Використовує shared tab-slider component
 * BACKWARD COMPATIBLE - wrapper для старого API
 */

(function () {
    'use strict';

    /**
     * Ініціалізація слайдера навігації
     * Тепер використовує shared tab-slider module
     */
    function initNavTabsSlider() {
        // Перевірка чи підключений shared модуль
        if (typeof window.initTabSlider !== 'function') {
            console.warn('nav-tabs-slider: shared tab-slider.js не підключено');
            return;
        }

        // Використовуємо shared компонент
        const navSlider = window.initTabSlider('.nav-tabs-container', {
            sliderAttr: 'data-nav-slider',
            tabAttr: 'data-nav-tab',
            activeClass: 'active',
            containerPadding: 3.6,
            widthReduction: 5,
            rightOffset: 10
        });

        if (!navSlider) {
            console.warn('nav-tabs-slider: не вдалося ініціалізувати slider');
            return;
        }

        // Експортуємо функцію оновлення для зовнішнього використання (backward compatibility)
        window.updateNavSlider = function (instant = false) {
            if (navSlider && navSlider.refresh) {
                navSlider.refresh();
            }
        };

        // Оновлення після повного завантаження шрифтів
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(() => {
                setTimeout(() => {
                    if (window.updateNavSlider) {
                        window.updateNavSlider(true);
                    }
                }, 100);
            });
        }
    }

    // Ініціалізація при завантаженні DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavTabsSlider);
    } else {
        initNavTabsSlider();
    }

    // Повторна ініціалізація після завантаження всіх ресурсів
    window.addEventListener('load', function () {
        setTimeout(function () {
            if (window.updateNavSlider) {
                window.updateNavSlider(true);
            }
        }, 150);
    });
})();
