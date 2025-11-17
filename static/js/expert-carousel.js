/**
 * Expert Carousel - Логіка стрілок для команди
 * Показує стрілки тільки якщо карток більше 4
 */

(function() {
    'use strict';
    
    // Ініціалізація при завантаженні
    document.addEventListener('DOMContentLoaded', function() {
        initExpertCarousel();
    });
    
    function initExpertCarousel() {
        const carouselContainers = document.querySelectorAll('.expert-carousel-container');
        
        carouselContainers.forEach(container => {
            const carousel = container.querySelector('.expert-carousel');
            const leftArrow = container.querySelector('.carousel-arrow-left');
            const rightArrow = container.querySelector('.carousel-arrow-right');
            const cards = carousel.querySelectorAll('.expert-card');
            
            // Якщо карток <= 4,ховаємо стрілки
            if (cards.length <= 4) {
                if (leftArrow) leftArrow.style.display = 'none';
                if (rightArrow) rightArrow.style.display = 'none';
                return;
            }
            
            // Показуємо стрілки
            if (leftArrow) leftArrow.style.display = 'flex';
            if (rightArrow) rightArrow.style.display = 'flex';
            
            let currentIndex = 0;
            const cardWidth = cards[0].offsetWidth;
            const gap = 16; // Gap між картками
            const visibleCards = 4;
            const maxIndex = Math.max(0, cards.length - visibleCards);
            
            // Лівая стрілка
            if (leftArrow) {
                leftArrow.addEventListener('click', function() {
                    if (currentIndex > 0) {
                        currentIndex--;
                        updateCarousel();
                    }
                });
            }
            
            // Права стрілка
            if (rightArrow) {
                rightArrow.addEventListener('click', function() {
                    if (currentIndex < maxIndex) {
                        currentIndex++;
                        updateCarousel();
                    }
                });
            }
            
            function updateCarousel() {
                const offset = -(currentIndex * (cardWidth + gap));
                carousel.style.transform = `translateX(${offset}px)`;
                
                // Активність стрілок
                if (leftArrow) {
                    leftArrow.classList.toggle('disabled', currentIndex === 0);
                }
                if (rightArrow) {
                    rightArrow.classList.toggle('disabled', currentIndex >= maxIndex);
                }
            }
            
            // Початковий стан
            updateCarousel();
            
            // Ре-калькуляція при зміні розміру вікна
            window.addEventListener('resize', function() {
                updateCarousel();
            });
        });
    }
    
    // Експорт для використання з HTMX
    window.initExpertCarousel = initExpertCarousel;
})();

