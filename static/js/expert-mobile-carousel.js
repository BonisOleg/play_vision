/**
 * Expert Mobile Carousel (Картки команди)
 * Карусель для карток експертів на мобільних пристроях (≤768px)
 * Працює тільки на мобільних, не впливає на desktop версію
 */

class ExpertMobileCarousel {
    constructor(container) {
        this.container = container;
        this.currentIndex = 0;
        this.slidesPerView = 2; // Завжди 2 картки на мобільних
        this.track = container.querySelector('.experts-grid');
        // Стрілки знаходяться в sibling елементі .experts-navigation
        const section = container.closest('.section-content');
        this.prevBtn = section?.querySelector('.expert-nav-prev');
        this.nextBtn = section?.querySelector('.expert-nav-next');

        if (!this.track) {
            console.warn('Experts grid track not found');
            return;
        }

        this.cards = this.track.querySelectorAll('.expert-card');
        this.totalCards = this.cards.length;

        if (this.totalCards === 0) {
            console.warn('No expert cards found');
            return;
        }

        // Ініціалізуємо тільки якщо мобільна версія
        if (window.innerWidth <= 768) {
            this.init();
        }
    }

    init() {
        this.updatePosition();
        this.updateButtons();
        this.attachEvents();
    }

    attachEvents() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevSlide());
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextSlide());
        }

        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                const isMobile = window.innerWidth <= 768;
                
                if (isMobile && !this.isInitialized) {
                    // Перехід з desktop на mobile - ініціалізуємо
                    this.init();
                    this.isInitialized = true;
                } else if (!isMobile && this.isInitialized) {
                    // Перехід з mobile на desktop - скидаємо
                    this.reset();
                    this.isInitialized = false;
                } else if (isMobile) {
                    // Просто resize на mobile
                    this.updatePosition();
                    this.updateButtons();
                }
            }, 150);
        });

        // Touch/swipe support для мобільних пристроїв
        this.addTouchSupport();
        this.isInitialized = true;
    }

    get maxIndex() {
        return Math.max(0, this.totalCards - this.slidesPerView);
    }

    updatePosition() {
        if (!this.track) return;

        // Обчислюємо зсув з урахуванням gap (16px на мобільних, 12px на малих)
        const gap = window.innerWidth <= 576 ? 12 : 16;
        const cardWidthPercent = 50; // 2 картки = 50% кожна
        const gapPercent = (gap / this.track.offsetWidth) * 100;
        const cardWithGapPercent = cardWidthPercent + (gapPercent / 2);

        const translateX = -(this.currentIndex * cardWithGapPercent);
        this.track.style.transform = `translateX(${translateX}%)`;
    }

    updateButtons() {
        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentIndex === 0;
        }

        if (this.nextBtn) {
            this.nextBtn.disabled = this.currentIndex >= this.maxIndex;
        }
    }

    nextSlide() {
        if (this.currentIndex < this.maxIndex) {
            this.currentIndex++;
            this.updatePosition();
            this.updateButtons();
        }
    }

    prevSlide() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updatePosition();
            this.updateButtons();
        }
    }

    goToSlide(index) {
        if (index >= 0 && index <= this.maxIndex) {
            this.currentIndex = index;
            this.updatePosition();
            this.updateButtons();
        }
    }

    reset() {
        // Скидаємо позицію при переході на desktop
        if (this.track) {
            this.track.style.transform = 'translateX(0)';
        }
        this.currentIndex = 0;
        if (this.prevBtn) this.prevBtn.disabled = false;
        if (this.nextBtn) this.nextBtn.disabled = false;
    }

    // Touch/Swipe підтримка для мобільних
    addTouchSupport() {
        let touchStartX = 0;
        let touchEndX = 0;
        let isDragging = false;

        this.track.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            isDragging = true;
        }, { passive: true });

        this.track.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            touchEndX = e.touches[0].clientX;
        }, { passive: true });

        this.track.addEventListener('touchend', () => {
            if (!isDragging) return;
            isDragging = false;

            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    // Swipe left - наступний слайд
                    this.nextSlide();
                } else {
                    // Swipe right - попередній слайд
                    this.prevSlide();
                }
            }

            touchStartX = 0;
            touchEndX = 0;
        });
    }
}

// Ініціалізація при завантаженні DOM
document.addEventListener('DOMContentLoaded', () => {
    // Знаходимо всі контейнери каруселі експертів
    const carouselContainers = document.querySelectorAll('.experts-carousel-container');

    carouselContainers.forEach(container => {
        // Ініціалізуємо тільки якщо мобільна версія
        if (window.innerWidth <= 768) {
            new ExpertMobileCarousel(container);
        }
    });
});

// Export для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExpertMobileCarousel;
}

