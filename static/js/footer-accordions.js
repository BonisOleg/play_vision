/**
 * FOOTER ACCORDIONS
 * Обробка акордеонів у мобільному футері
 */

(function () {
    function initAccordions() {
        const accordionToggles = document.querySelectorAll('[data-accordion-toggle]');

        if (!accordionToggles.length) {
            return;
        }

        accordionToggles.forEach(toggle => {
            toggle.addEventListener('click', function () {
                const accordionItem = this.closest('.accordion-item');
                const accordionContent = accordionItem.querySelector('.accordion-content');
                const isActive = accordionItem.classList.contains('active');

                // Закрити всі інші акордеони
                closeAllAccordions();

                // Перемкнути поточний акордеон
                if (!isActive) {
                    accordionItem.classList.add('active');
                    accordionContent.style.maxHeight = accordionContent.scrollHeight + 'px';
                }
            });
        });
    }

    function closeAllAccordions() {
        const allAccordions = document.querySelectorAll('.accordion-item');

        allAccordions.forEach(item => {
            const content = item.querySelector('.accordion-content');
            item.classList.remove('active');
            content.style.maxHeight = null;
        });
    }

    // Ініціалізація при завантаженні сторінки
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAccordions);
    } else {
        initAccordions();
    }

    // Обробка зміни розміру вікна для коректного перерахунку висоти
    let resizeTimer;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            const activeAccordions = document.querySelectorAll('.accordion-item.active');
            activeAccordions.forEach(item => {
                const content = item.querySelector('.accordion-content');
                content.style.maxHeight = content.scrollHeight + 'px';
            });
        }, 250);
    });
})();

