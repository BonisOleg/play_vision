/**
 * Shared Tab Slider Component
 * Reusable slider animation for tab navigation
 * Використовується: header nav, pricing periods, інші tabs
 */

(function(window) {
    'use strict';

    /**
     * Ініціалізує tab slider для контейнера
     * @param {string} containerSelector - CSS селектор контейнера
     * @param {Object} config - Конфігурація
     * @returns {Object|null} API об'єкт або null
     */
    function initTabSlider(containerSelector, config = {}) {
        const {
            sliderAttr = 'data-tab-slider',
            tabAttr = 'data-tab-button',
            activeClass = 'active',
            containerPadding = 3.6,
            widthReduction = 5,
            rightOffset = 10,
            onTabChange = null
        } = config;

        const container = document.querySelector(containerSelector);
        if (!container) {
            console.warn(`Tab slider: контейнер "${containerSelector}" не знайдено`);
            return null;
        }

        const slider = container.querySelector(`[${sliderAttr}]`);
        const tabs = container.querySelectorAll(`[${tabAttr}]`);

        if (!slider) {
            console.warn(`Tab slider: slider з атрибутом "${sliderAttr}" не знайдено`);
            return null;
        }

        if (tabs.length === 0) {
            console.warn(`Tab slider: tabs з атрибутом "${tabAttr}" не знайдено`);
            return null;
        }

        /**
         * Оновлює позицію та розмір слайдера
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

            // Визначаємо чи це останній таб
            const tabsArray = Array.from(tabs);
            const tabIndex = tabsArray.indexOf(targetTab);
            const isLastTab = tabIndex === tabsArray.length - 1;

            // Коригуємо ширину
            const adjustedWidth = isLastTab 
                ? width - widthReduction - rightOffset 
                : width - widthReduction;

            // Застосовуємо стилі
            if (instant) {
                slider.style.transition = 'none';
            }

            slider.style.width = `${adjustedWidth}px`;
            slider.style.transform = `translateX(${left}px)`;

            // Відновлюємо анімацію
            if (instant) {
                requestAnimationFrame(() => {
                    slider.style.transition = '';
                });
            }

            // Додаємо fallback клас для браузерів без :has()
            if (targetTab.classList.contains(activeClass)) {
                container.classList.add('has-active');
            }
        }

        /**
         * Знаходить активний таб
         * @returns {HTMLElement|null}
         */
        function findActiveTab() {
            return Array.from(tabs).find(tab => tab.classList.contains(activeClass)) || null;
        }

        /**
         * Встановлює активний таб за індексом
         * @param {number} index - Індекс табу
         */
        function setActiveTab(index) {
            if (index < 0 || index >= tabs.length) {
                console.warn(`Tab slider: неправильний індекс ${index}`);
                return;
            }

            tabs.forEach(t => t.classList.remove(activeClass));
            tabs[index].classList.add(activeClass);
            updateSliderPosition(tabs[index], false);

            if (onTabChange && typeof onTabChange === 'function') {
                onTabChange(tabs[index], index);
            }
        }

        /**
         * Ініціалізує початкову позицію
         */
        function initPosition() {
            const activeTab = findActiveTab();
            if (activeTab) {
                updateSliderPosition(activeTab, true);
            }
        }

        /**
         * Обробляє hover на табах
         */
        function handleHover() {
            tabs.forEach(tab => {
                tab.addEventListener('mouseenter', function() {
                    updateSliderPosition(this, false);
                });

                tab.addEventListener('mouseleave', function() {
                    const activeTab = findActiveTab();
                    if (activeTab) {
                        updateSliderPosition(activeTab, false);
                    }
                });
            });
        }

        /**
         * Обробляє клік на табі
         */
        function handleClick() {
            tabs.forEach((tab, index) => {
                tab.addEventListener('click', function(e) {
                    tabs.forEach(t => t.classList.remove(activeClass));
                    this.classList.add(activeClass);
                    updateSliderPosition(this, false);

                    if (onTabChange && typeof onTabChange === 'function') {
                        onTabChange(this, index);
                    }
                });
            });
        }

        /**
         * Обробляє resize
         */
        function handleResize() {
            const activeTab = findActiveTab();
            if (activeTab) {
                updateSliderPosition(activeTab, true);
            }
        }

        /**
         * Debounce функція
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
        initPosition();
        handleHover();
        handleClick();

        // Events
        const debouncedResize = debounce(handleResize, 150);
        window.addEventListener('resize', debouncedResize);
        window.addEventListener('orientationchange', () => {
            setTimeout(handleResize, 100);
        });

        // Theme change observer
        const themeObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
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

        // Font loading
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(() => {
                setTimeout(() => {
                    handleResize();
                }, 100);
            });
        }

        // Public API
        return {
            updatePosition: (tab, instant = false) => updateSliderPosition(tab, instant),
            getActiveTab: () => findActiveTab(),
            setActiveTab: (index) => setActiveTab(index),
            refresh: () => handleResize(),
            destroy: () => {
                window.removeEventListener('resize', debouncedResize);
                themeObserver.disconnect();
            }
        };
    }

    // Export для використання
    window.initTabSlider = initTabSlider;

})(window);

