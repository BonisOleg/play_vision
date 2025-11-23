/**
 * HTMX Navigation Coordinator
 * Координує всі дії після динамічної зміни контенту через HTMX
 * 
 * Відповідає за:
 * 1. Оновлення активної кнопки меню
 * 2. Перерахунок slider позиції
 * 3. Ре-ініціалізацію page-specific JS
 * 4. Scroll до верху сторінки
 */

(function() {
    'use strict';

    // Мапа URL → page identifier для визначення активної сторінки
    const PAGE_IDENTIFIERS = {
        '/': 'home',
        '/about/': 'about',
        '/hub/': 'hub',
        '/events/': 'events',
        '/mentor-coaching/': 'mentoring',
        '/pricing/': 'pricing'
    };

    /**
     * Визначає page identifier з URL
     */
    function getPageFromUrl(url) {
        try {
            const path = new URL(url, window.location.origin).pathname;
            
            // Пряме співпадіння
            if (PAGE_IDENTIFIERS[path]) {
                return PAGE_IDENTIFIERS[path];
            }
            
            // Часткове співпадіння (для підсторінок)
            if (path.includes('/hub/') || path.includes('/content/')) return 'hub';
            if (path.includes('/events/')) return 'events';
            if (path.includes('/about/')) return 'about';
            if (path.includes('/mentor-coaching/')) return 'mentoring';
            if (path.includes('/pricing/')) return 'pricing';
            
            return 'home';
        } catch (e) {
            console.error('Error parsing URL:', e);
            return null;
        }
    }

    /**
     * Оновлює активну кнопку навігації
     */
    function updateActiveNavButton(page) {
        if (!page) return;

        const allButtons = document.querySelectorAll('.nav-tab-btn[data-nav-tab]');
        
        allButtons.forEach(btn => {
            const btnPage = btn.getAttribute('data-page');
            const isActive = btnPage === page;
            
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-current', isActive ? 'page' : 'false');
        });

        console.log(`[HTMX Nav] Active button updated: ${page}`);
    }

    /**
     * Оновлює позицію slider під активною кнопкою
     */
    function updateNavSlider() {
        // Викликаємо глобальну функцію з nav-tabs-slider.js
        if (typeof window.updateNavSlider === 'function') {
            window.updateNavSlider();
            console.log('[HTMX Nav] Slider position updated');
        } else {
            console.warn('[HTMX Nav] window.updateNavSlider not available');
        }
    }

    /**
     * Ре-ініціалізує page-specific JavaScript
     */
    function reinitializePageScripts(page) {
        console.log(`[HTMX Nav] Reinitializing scripts for: ${page}`);

        // Home page
        if (page === 'home' && typeof window.initHome === 'function') {
            window.initHome();
        }

        // About page
        if (page === 'about' && typeof window.initAbout === 'function') {
            window.initAbout();
        }

        // Mentoring page
        if (page === 'mentoring' && typeof window.initMentoring === 'function') {
            window.initMentoring();
        }

        // Hub page
        if (page === 'hub' && typeof window.initHub === 'function') {
            window.initHub();
        }

        // Events page
        if (page === 'events' && typeof window.initEvents === 'function') {
            window.initEvents();
        }

        // Pricing page
        if (page === 'pricing' && typeof window.initPricing === 'function') {
            window.initPricing();
        }

        // Expert flip cards (якщо є на сторінці)
        if ((page === 'home' || page === 'about' || page === 'mentoring') && 
            typeof window.initExpertFlipCards === 'function') {
            window.initExpertFlipCards();
        }

        // Main courses carousel (якщо є на home)
        if (page === 'home' && typeof window.initMainCoursesCarousel === 'function') {
            window.initMainCoursesCarousel();
        }

        console.log(`[HTMX Nav] Scripts reinitialized for: ${page}`);
    }

    /**
     * Чекає завантаження всіх CSS перед тим як продовжити
     */
    function waitForStyles(timeout = 1000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            
            function checkStyles() {
                // Перевіряємо чи всі <link> завантажені
                const links = document.querySelectorAll('link[rel="stylesheet"]');
                const allLoaded = Array.from(links).every(link => {
                    // link.sheet буде null поки CSS не завантажиться
                    try {
                        return link.sheet !== null && link.sheet.cssRules !== null;
                    } catch (e) {
                        // Може бути CORS помилка для external stylesheets
                        return true;
                    }
                });
                
                if (allLoaded) {
                    console.log(`[HTMX Nav] All styles loaded in ${Date.now() - startTime}ms`);
                    resolve();
                } else if (Date.now() - startTime > timeout) {
                    console.warn('[HTMX Nav] Timeout waiting for styles, proceeding anyway');
                    reject(new Error('Timeout waiting for styles'));
                } else {
                    requestAnimationFrame(checkStyles);
                }
            }
            
            checkStyles();
        });
    }

    /**
     * Головний обробник afterSwap
     */
    function handleAfterSwap(event) {
        console.log('[HTMX Nav] afterSwap triggered');

        // Визначаємо сторінку з URL
        const newUrl = event.detail.pathInfo.responsePath || window.location.href;
        const page = getPageFromUrl(newUrl);

        if (!page) {
            console.warn('[HTMX Nav] Could not determine page from URL:', newUrl);
            return;
        }

        // 1. Оновлюємо активну кнопку
        updateActiveNavButton(page);

        // 2. Чекаємо завантаження CSS перед оновленням UI
        waitForStyles().then(() => {
            // Оновлюємо slider
            updateNavSlider();
            
            // Ре-ініціалізуємо page-specific scripts (з невеликою затримкою для DOM)
            setTimeout(() => {
                reinitializePageScripts(page);
            }, 50);
        }).catch(err => {
            // Якщо timeout - продовжуємо в будь-якому випадку
            console.warn('[HTMX Nav] Proceeding without waiting for all styles');
            updateNavSlider();
            reinitializePageScripts(page);
        });

        console.log('[HTMX Nav] Navigation completed:', page);
    }

    /**
     * Ініціалізація при завантаженні сторінки
     */
    function init() {
        // Підключаємо обробник до htmx:afterSwap
        document.body.addEventListener('htmx:afterSwap', handleAfterSwap);

        console.log('[HTMX Nav] Coordinator initialized');
    }

    // Запускаємо після повного завантаження DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

