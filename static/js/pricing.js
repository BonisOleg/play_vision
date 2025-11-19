/**
 * Pricing Page JavaScript
 * Play Vision - Система тарифів
 * 
 * Функціонал:
 * - Перемикання періодів (місяць/3 міс/рік)
 * - Показ/приховування цін та кнопок
 * - Модальне вікно порівняння
 * - Слайдер на мобільних
 */

(function() {
    'use strict';

    // === ІНІЦІАЛІЗАЦІЯ ===
    document.addEventListener('DOMContentLoaded', function() {
        initPeriodSwitcher();
        initComparisonModal();
        initMobileSlider();
    });

    // === ПЕРЕМИКАЧ ПЕРІОДІВ ===
    function initPeriodSwitcher() {
        // Desktop кнопки
        const periodBtns = document.querySelectorAll('.period-btn');
        periodBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const period = this.getAttribute('data-period');
                switchPeriod(period);
                
                // Оновлюємо активну кнопку
                periodBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });

        // Mobile dropdown
        const periodSelect = document.getElementById('period-select');
        if (periodSelect) {
            periodSelect.addEventListener('change', function() {
                switchPeriod(this.value);
            });
        }
    }

    function switchPeriod(period) {
        console.log('Switching to period:', period);
        
        //Ховаємо всі блоки цін
        const allPriceBlocks = document.querySelectorAll('.price-block');
        allPriceBlocks.forEach(block => {
            block.style.display = 'none';
        });

        // Показуємо ціни для обраного періоду
        const activePriceBlocks = document.querySelectorAll(`.price-block[data-period="${period}"]`);
        activePriceBlocks.forEach(block => {
            block.style.display = 'block';
        });

        // Ховаємо всі кнопки
        const allActionWrappers = document.querySelectorAll('.action-wrapper');
        allActionWrappers.forEach(wrapper => {
            wrapper.style.display = 'none';
        });

        // Показуємо кнопки для обраного періоду
        const activeActionWrappers = document.querySelectorAll(`.action-wrapper[data-period="${period}"]`);
        activeActionWrappers.forEach(wrapper => {
            wrapper.style.display = 'block';
        });

        // Анімація
        const planCards = document.querySelectorAll('.plan-card');
        planCards.forEach((card, index) => {
            card.style.animation = 'none';
            // Trigger reflow
            card.offsetHeight;
            card.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s backwards`;
        });
    }

    // === МОДАЛЬНЕ ВІКНО ПОРІВНЯННЯ ===
    function initComparisonModal() {
        const btnCompare = document.getElementById('btn-compare');
        const modal = document.getElementById('comparison-modal');
        const modalClose = document.getElementById('modal-close');

        if (btnCompare && modal) {
            // Відкрити модалку
            btnCompare.addEventListener('click', function() {
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            });

            // Закрити модалку
            if (modalClose) {
                modalClose.addEventListener('click', closeModal);
            }

            // Закрити по кліку на overlay
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeModal();
                }
            });

            // Закрити по ESC
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modal.classList.contains('active')) {
                    closeModal();
                }
            });
        }

        function closeModal() {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // === МОБІЛЬНИЙ СЛАЙДЕР ===
    function initMobileSlider() {
        if (window.innerWidth <= 768) {
            const plansGrid = document.getElementById('plans-grid');
            
            if (plansGrid) {
                // Smooth scroll для слайдера
                let isDown = false;
                let startX;
                let scrollLeft;

                plansGrid.addEventListener('mousedown', (e) => {
                    isDown = true;
                    plansGrid.style.cursor = 'grabbing';
                    startX = e.pageX - plansGrid.offsetLeft;
                    scrollLeft = plansGrid.scrollLeft;
                });

                plansGrid.addEventListener('mouseleave', () => {
                    isDown = false;
                    plansGrid.style.cursor = 'grab';
                });

                plansGrid.addEventListener('mouseup', () => {
                    isDown = false;
                    plansGrid.style.cursor = 'grab';
                });

                plansGrid.addEventListener('mousemove', (e) => {
                    if (!isDown) return;
                    e.preventDefault();
                    const x = e.pageX - plansGrid.offsetLeft;
                    const walk = (x - startX) * 2;
                    plansGrid.scrollLeft = scrollLeft - walk;
                });

                // Touch events для мобільних
                let touchStartX = 0;
                let touchEndX = 0;

                plansGrid.addEventListener('touchstart', (e) => {
                    touchStartX = e.changedTouches[0].screenX;
                }, {passive: true});

                plansGrid.addEventListener('touchend', (e) => {
                    touchEndX = e.changedTouches[0].screenX;
                    handleSwipe();
                }, {passive: true});

                function handleSwipe() {
                    const swipeThreshold = 50;
                    const diff = touchStartX - touchEndX;

                    if (Math.abs(diff) > swipeThreshold) {
                        // Свайп виконано
                        console.log('Swipe detected:', diff > 0 ? 'left' : 'right');
                    }
                }

                // Snap to card при закінченні скролу
                let scrollTimeout;
                plansGrid.addEventListener('scroll', function() {
                    clearTimeout(scrollTimeout);
                    scrollTimeout = setTimeout(function() {
                        snapToNearestCard(plansGrid);
                    }, 150);
                }, {passive: true});
            }
        }
    }

    function snapToNearestCard(container) {
        const cards = container.querySelectorAll('.plan-card');
        if (!cards.length) return;

        const containerLeft = container.scrollLeft;
        const containerWidth = container.offsetWidth;
        const containerCenter = containerLeft + (containerWidth / 2);

        let closestCard = null;
        let closestDistance = Infinity;

        cards.forEach(card => {
            const cardLeft = card.offsetLeft;
            const cardWidth = card.offsetWidth;
            const cardCenter = cardLeft + (cardWidth / 2);
            const distance = Math.abs(containerCenter - cardCenter);

            if (distance < closestDistance) {
                closestDistance = distance;
                closestCard = card;
            }
        });

        if (closestCard) {
            const targetScroll = closestCard.offsetLeft - ((containerWidth - closestCard.offsetWidth) / 2);
            container.scrollTo({
                left: targetScroll,
                behavior: 'smooth'
            });
        }
    }

    // === UTILITY FUNCTIONS ===
    
    // Debounce для оптимізації
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

    // Реагування на зміну розміру вікна
    window.addEventListener('resize', debounce(function() {
        // Переініціалізація при зміні breakpoint
        const wasMobile = document.querySelector('.mobile-dropdown').style.display !== 'none';
        const isMobile = window.innerWidth <= 768;

        if (wasMobile !== isMobile) {
            location.reload();
        }
    }, 250));

})();

