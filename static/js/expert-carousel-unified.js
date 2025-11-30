/**
 * Expert Carousel Unified (Команда експертів)
 * Карусель для карток експертів на всіх пристроях (desktop, tablet, mobile)
 * Використовує ту ж логіку як MainCoursesCarousel
 */

class ExpertCarouselUnified {
    constructor(element) {
        this.section = element;
        this.currentIndex = 0;
        this.slidesPerView = 4;
        this.track = element.querySelector('.experts-grid');
        this.prevBtn = element.querySelector('.expert-nav-prev');
        this.nextBtn = element.querySelector('.expert-nav-next');

        if (!this.track) {
            console.warn('Expert grid track not found');
            return;
        }

        this.slides = this.track.querySelectorAll('.expert-card');
        this.totalSlides = this.slides.length;

        if (this.totalSlides === 0) {
            console.warn('No expert cards found');
            return;
        }

        this.init();
    }

    init() {
        this.updateSlidesPerView();
        this.updatePosition();
        this.updateButtons();
        this.updateArrowsVisibility();
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
                this.updateSlidesPerView();
                this.currentIndex = Math.min(this.currentIndex, this.maxIndex);
                this.updatePosition();
                this.updateButtons();
                this.updateArrowsVisibility();
            }, 150);
        });

        // Touch/swipe support для мобільних пристроїв
        this.addTouchSupport();
    }

    updateSlidesPerView() {
        const width = window.innerWidth;

        if (width < 576) {
            this.slidesPerView = 2;
        } else if (width < 768) {
            this.slidesPerView = 2;
        } else if (width < 1024) {
            this.slidesPerView = 3;
        } else {
            this.slidesPerView = 4;
        }
    }

    get slideWidth() {
        // Враховуємо gap між слайдами (24px)
        const gap = 24;
        return (100 / this.slidesPerView);
    }

    get maxIndex() {
        return Math.max(0, this.totalSlides - this.slidesPerView);
    }

    updatePosition() {
        if (!this.track) return;

        // Обчислюємо зсув з урахуванням gap
        const gap = 24;
        const slideWidthPercent = 100 / this.slidesPerView;
        const gapInPercent = (gap * this.currentIndex * this.slidesPerView) / this.track.offsetWidth * 100;

        const translateX = -(this.currentIndex * slideWidthPercent + gapInPercent);
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

    updateArrowsVisibility() {
        // Показуємо стрілки тільки якщо карток >= 5
        const shouldShow = this.totalSlides >= 5;
        const navigation = this.section.querySelector('.experts-navigation');
        
        if (navigation) {
            navigation.style.display = shouldShow ? 'flex' : 'none';
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
    const expertsSection = document.querySelector('.experts-section');

    if (expertsSection) {
        new ExpertCarouselUnified(expertsSection);
    }
});

// Export для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExpertCarouselUnified;
}

