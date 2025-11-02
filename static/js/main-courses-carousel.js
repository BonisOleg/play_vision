/**
 * Main Courses Carousel (Наші основні програми)
 * Карусель для основних курсів на головній сторінці
 */

class MainCoursesCarousel {
    constructor(element) {
        this.section = element;
        this.currentIndex = 0;
        this.slidesPerView = 3;
        this.track = element.querySelector('.main-courses-track');
        this.prevBtn = element.querySelector('.course-nav-prev');
        this.nextBtn = element.querySelector('.course-nav-next');

        if (!this.track) {
            console.warn('Main courses track not found');
            return;
        }

        this.slides = this.track.querySelectorAll('.main-course-slide');
        this.totalSlides = this.slides.length;

        if (this.totalSlides === 0) {
            console.warn('No main course slides found');
            return;
        }

        this.init();
    }

    init() {
        this.updateSlidesPerView();
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
                this.updateSlidesPerView();
                this.currentIndex = Math.min(this.currentIndex, this.maxIndex);
                this.updatePosition();
                this.updateButtons();
            }, 150);
        });

        // Touch/swipe support для мобільних пристроїв
        this.addTouchSupport();
    }

    updateSlidesPerView() {
        const width = window.innerWidth;

        if (width < 576) {
            this.slidesPerView = 1;
        } else if (width < 768) {
            this.slidesPerView = 1;
        } else if (width < 1024) {
            this.slidesPerView = 2;
        } else {
            this.slidesPerView = 3;
        }
    }

    get slideWidth() {
        // Враховуємо gap між слайдами (20px)
        const gap = 20;
        return (100 / this.slidesPerView);
    }

    get maxIndex() {
        return Math.max(0, this.totalSlides - this.slidesPerView);
    }

    updatePosition() {
        if (!this.track) return;

        // Обчислюємо зсув з урахуванням gap
        const gap = 20;
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
    const mainCoursesSection = document.querySelector('.main-courses-section');

    if (mainCoursesSection) {
        new MainCoursesCarousel(mainCoursesSection);
    }
});

// Export для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MainCoursesCarousel;
}

