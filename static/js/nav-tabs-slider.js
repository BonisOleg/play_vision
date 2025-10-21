/**
 * Navigation Tabs Animated Slider
 * Плавна анімація жолобка при переході між пунктами меню
 */

(function () {
    'use strict';

    /**
     * Ініціалізація слайдера навігації
     */
    function initNavTabsSlider() {
        const container = document.querySelector('.nav-tabs-container');
        if (!container) return;

        const slider = container.querySelector('[data-nav-slider]');
        const tabs = container.querySelectorAll('[data-nav-tab]');

        if (!slider || tabs.length === 0) return;

        /**
         * Оновлює позицію та розмір слайдера
         * @param {HTMLElement} targetTab - Цільовий таб
         */
        function updateSliderPosition(targetTab) {
            if (!targetTab) return;

            const containerRect = container.getBoundingClientRect();
            const tabRect = targetTab.getBoundingClientRect();

            // Обчислюємо позицію відносно контейнера
            const left = tabRect.left - containerRect.left;
            const width = tabRect.width;

            // Застосовуємо стилі
            slider.style.width = `${width}px`;
            slider.style.transform = `translateX(${left}px)`;
        }

        /**
         * Знаходить активний таб
         * @returns {HTMLElement|null}
         */
        function findActiveTab() {
            return container.querySelector('[data-nav-tab].active');
        }

        /**
         * Ініціалізує початкову позицію слайдера
         */
        function initSliderPosition() {
            const activeTab = findActiveTab();
            if (activeTab) {
                // Встановлюємо позицію без анімації при завантаженні
                slider.style.transition = 'none';
                updateSliderPosition(activeTab);

                // Відновлюємо анімацію через короткий час
                setTimeout(() => {
                    slider.style.transition = 'all 0.4s cubic-bezier(0.4, 0.0, 0.2, 1)';
                }, 50);
            }
        }

        /**
         * Обробляє hover на табах
         */
        function handleTabHover() {
            tabs.forEach(tab => {
                // Hover in
                tab.addEventListener('mouseenter', function () {
                    updateSliderPosition(this);
                });

                // Hover out - повертаємося до активного
                tab.addEventListener('mouseleave', function () {
                    const activeTab = findActiveTab();
                    if (activeTab) {
                        updateSliderPosition(activeTab);
                    }
                });
            });
        }

        /**
         * Обробляє зміну розміру вікна
         */
        function handleResize() {
            const activeTab = findActiveTab();
            if (activeTab) {
                updateSliderPosition(activeTab);
            }
        }

        // Ініціалізація
        initSliderPosition();
        handleTabHover();

        // Обробляємо зміну розміру вікна
        let resizeTimeout;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(handleResize, 100);
        });

        // Обробляємо зміну теми (може змінити розміри)
        const themeObserver = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.attributeName === 'data-theme') {
                    setTimeout(handleResize, 50);
                }
            });
        });

        themeObserver.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });

        // Обробляємо клік по табу (для SPA навігації)
        tabs.forEach(tab => {
            tab.addEventListener('click', function () {
                // Видаляємо активний клас зі всіх табів
                tabs.forEach(t => t.classList.remove('active'));
                // Додаємо активний клас до поточного табу
                this.classList.add('active');
                // Оновлюємо позицію слайдера
                updateSliderPosition(this);
            });
        });

        // Експортуємо функцію оновлення для зовнішнього використання
        window.updateNavSlider = function () {
            const activeTab = findActiveTab();
            if (activeTab) {
                updateSliderPosition(activeTab);
            }
        };
    }

    // Ініціалізація при завантаженні DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavTabsSlider);
    } else {
        initNavTabsSlider();
    }

    // Повторна ініціалізація після завантаження всіх ресурсів
    // (для точного обчислення розмірів)
    window.addEventListener('load', function () {
        setTimeout(function () {
            if (window.updateNavSlider) {
                window.updateNavSlider();
            }
        }, 100);
    });
})();

