/**
 * Expert Quotes Carousel
 * Автоматична зміна 3 цитат експертів кожні 15 секунд
 */

class ExpertQuotesCarousel {
    constructor() {
        this.currentIndex = 0;
        this.slides = document.querySelectorAll('.quote-slide');
        this.indicators = document.querySelectorAll('.quote-indicator');
        this.autoplayInterval = null;
        this.autoplayDelay = 15000; // 15 секунд

        if (this.slides.length > 0) {
            this.init();
        }
    }

    init() {
        // Click на індикатори
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.goToSlide(index);
                this.resetAutoplay();
            });
        });

        // Запустити autoplay
        this.startAutoplay();

        // Зупинити при наведенні
        const carousel = document.querySelector('.expert-quotes-carousel');
        if (carousel) {
            carousel.addEventListener('mouseenter', () => this.stopAutoplay());
            carousel.addEventListener('mouseleave', () => this.startAutoplay());
        }
    }

    goToSlide(index) {
        // Приховати поточний слайд
        this.slides[this.currentIndex].classList.remove('active');
        this.indicators[this.currentIndex].classList.remove('active');

        // Показати новий слайд
        this.currentIndex = index;
        this.slides[this.currentIndex].classList.add('active');
        this.indicators[this.currentIndex].classList.add('active');
    }

    nextSlide() {
        const nextIndex = (this.currentIndex + 1) % this.slides.length;
        this.goToSlide(nextIndex);
    }

    startAutoplay() {
        this.autoplayInterval = setInterval(() => {
            this.nextSlide();
        }, this.autoplayDelay);
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

// Ініціалізація при завантаженні DOM
document.addEventListener('DOMContentLoaded', () => {
    new ExpertQuotesCarousel();
});
