/**
 * Navigation Tabs Animated Slider
 * Плавна анімація жолобка при переході між пунктами меню
 * Оновлена версія з точнішим позиціонуванням
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

        // Константи для точного позиціонування
        const CONTAINER_PADDING = 3.6; // padding контейнера в px
        const TAB_GAP = 2; // gap між табами в px
        const WIDTH_REDUCTION = 5; // зменшення ширини всіх кнопок в px
        const RIGHT_OFFSET = 10; // додатковий відступ справа для останньої кнопки в px

        /**
         * Оновлює позицію та розмір слайдера з точним обрамленням
         * @param {HTMLElement} targetTab - Цільовий таб
         * @param {boolean} instant - Миттєве позиціонування без анімації
         */
        function updateSliderPosition(targetTab, instant = false) {
            if (!targetTab) return;

            const containerRect = container.getBoundingClientRect();
            const tabRect = targetTab.getBoundingClientRect();

            // Обчислюємо позицію відносно контейнера
            const left = tabRect.left - containerRect.left;
            const width = tabRect.width;

            // Отримуємо всі таби як масив
            const tabsArray = Array.from(tabs);
            const tabIndex = tabsArray.indexOf(targetTab);
            const isLastTab = tabIndex === tabsArray.length - 1;

            // Зменшуємо ширину всіх кнопок на WIDTH_REDUCTION
            // Для останньої кнопки додаємо ще RIGHT_OFFSET
            const adjustedWidth = isLastTab ? width - WIDTH_REDUCTION - RIGHT_OFFSET : width - WIDTH_REDUCTION;

            // Застосовуємо стилі з точним позиціонуванням
            if (instant) {
                slider.style.transition = 'none';
            }

            slider.style.width = `${adjustedWidth}px`;
            slider.style.transform = `translateX(${left}px)`;

            // Відновлюємо анімацію після миттєвого позиціонування
            if (instant) {
                requestAnimationFrame(() => {
                    slider.style.transition = 'all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                });
            }
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
                // Встановлюємо позицію миттєво при завантаженні
                updateSliderPosition(activeTab, true);
            }
        }

        /**
         * Обробляє hover на табах з плавною анімацією
         */
        function handleTabHover() {
            tabs.forEach(tab => {
                // Hover in - плавно переміщуємо до tab
                tab.addEventListener('mouseenter', function () {
                    updateSliderPosition(this, false);
                });

                // Hover out - плавно повертаємося до активного
                tab.addEventListener('mouseleave', function () {
                    const activeTab = findActiveTab();
                    if (activeTab) {
                        updateSliderPosition(activeTab, false);
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
                // При resize робимо миттєве оновлення
                updateSliderPosition(activeTab, true);
            }
        }

        /**
         * Debounce функція для оптимізації
         */
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        // Ініціалізація
        initSliderPosition();
        handleTabHover();

        // Обробляємо зміну розміру вікна з debounce
        const debouncedResize = debounce(handleResize, 150);
        window.addEventListener('resize', debouncedResize);

        // Обробляємо зміну орієнтації на мобільних
        window.addEventListener('orientationchange', function () {
            setTimeout(handleResize, 100);
        });

        // Обробляємо зміну теми (може змінити розміри)
        const themeObserver = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.attributeName === 'data-theme') {
                    setTimeout(() => {
                        const activeTab = findActiveTab();
                        if (activeTab) {
                            updateSliderPosition(activeTab, true);
                        }
                    }, 50);
                }
            });
        });

        themeObserver.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });

        // Обробляємо клік по табу (для навігації)
        tabs.forEach(tab => {
            tab.addEventListener('click', function (e) {
                // Видаляємо активний клас зі всіх табів
                tabs.forEach(t => t.classList.remove('active'));
                // Додаємо активний клас до поточного табу
                this.classList.add('active');
                // Оновлюємо позицію слайдера з анімацією
                updateSliderPosition(this, false);
            });
        });

        // Експортуємо функцію оновлення для зовнішнього використання
        window.updateNavSlider = function (instant = false) {
            const activeTab = findActiveTab();
            if (activeTab) {
                updateSliderPosition(activeTab, instant);
            }
        };

        // Додаткове оновлення після повного завантаження шрифтів
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
