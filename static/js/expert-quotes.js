/**
 * Карусель цитат експертів
 * Автоматична зміна кожні 15 секунд
 */

class ExpertQuotesCarousel {
    constructor() {
        this.currentSlide = 0;
        this.slides = document.querySelectorAll('.quote-slide');
        this.indicators = document.querySelectorAll('.quote-indicator');
        this.autoplayInterval = null;

        if (this.slides.length > 0) {
            this.init();
        }
    }

    init() {
        // Обробники для індикаторів
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.goToSlide(index);
                this.resetAutoplay();
            });
        });

        // Запустити автоплей
        this.startAutoplay();

        // Зупинити автоплей при наведенні
        const carousel = document.querySelector('.expert-quotes-carousel');
        if (carousel) {
            carousel.addEventListener('mouseenter', () => this.stopAutoplay());
            carousel.addEventListener('mouseleave', () => this.startAutoplay());
        }
    }

    goToSlide(index) {
        // Приховати поточний слайд
        this.slides[this.currentSlide].classList.remove('active');
        this.indicators[this.currentSlide].classList.remove('active');

        // Показати новий слайд
        this.currentSlide = index;
        this.slides[this.currentSlide].classList.add('active');
        this.indicators[this.currentSlide].classList.add('active');
    }

    nextSlide() {
        const nextIndex = (this.currentSlide + 1) % this.slides.length;
        this.goToSlide(nextIndex);
    }

    startAutoplay() {
        // Перевірка prefers-reduced-motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return;
        }

        this.autoplayInterval = setInterval(() => {
            this.nextSlide();
        }, 15000); // 15 секунд
    }

    stopAutoplay() {
        if (this.autoplayInterval) {
            clearInterval(this.autoplayInterval);
            this.autoplayInterval = null;
        }
    }

    resetAutoplay() {
        this.stopAutoplay();
        this.startAutoplay();
    }
}

// Ініціалізація
document.addEventListener('DOMContentLoaded', () => {
    window.expertQuotesCarousel = new ExpertQuotesCarousel();
});

