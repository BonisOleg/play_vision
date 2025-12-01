/**
 * Main Courses Carousel (Наші основні програми)
 * Карусель для основних курсів на головній сторінці
 */

class MainCoursesCarousel {
    constructor(element) {
        this.section = element;
        this.currentIndex = 0;
        this.slidesPerView = 4;
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
        // На мобільних (≤767px) стрілки завжди видимі
        const isMobile = window.innerWidth <= 767;
        const shouldShow = isMobile || this.totalSlides >= 5;
        const navigation = this.section.querySelector('.main-courses-navigation');
        
        if (navigation) {
            navigation.style.display = shouldShow ? 'flex' : 'none';
        }
    }

    nextSlide() {
        const isMobile = window.innerWidth < 768;
        const step = isMobile ? this.slidesPerView : 1;
        
        if (this.currentIndex < this.maxIndex) {
            this.currentIndex = Math.min(this.currentIndex + step, this.maxIndex);
            this.updatePosition();
            this.updateButtons();
        }
    }

    prevSlide() {
        const isMobile = window.innerWidth < 768;
        const step = isMobile ? this.slidesPerView : 1;
        
        if (this.currentIndex > 0) {
            this.currentIndex = Math.max(this.currentIndex - step, 0);
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
        let touchStartY = 0;
        let touchEndY = 0;
        let isDragging = false;

        this.track.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            touchEndX = 0;
            touchEndY = 0;
            isDragging = true;
        }, { passive: true });

        this.track.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            touchEndX = e.touches[0].clientX;
            touchEndY = e.touches[0].clientY;
        }, { passive: true });

        this.track.addEventListener('touchend', (e) => {
            if (!isDragging) return;
            isDragging = false;

            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;
            
            // КРИТИЧНА ПЕРЕВІРКА: якщо це TAP на картці курсу - ІГНОРУВАТИ
            const deltaX = Math.abs(touchStartX - (touchEndX || touchStartX));
            const deltaY = Math.abs(touchStartY - (touchEndY || touchStartY));
            const isOnCard = e.target.closest('.main-course-card');  // ПРАВИЛЬНИЙ селектор
            const isTap = deltaX < 20 && deltaY < 20;
            
            if (isOnCard && isTap) {
                // Це TAP на картці курсу - ІГНОРУВАТИ, НЕ рухати карусель
                touchStartX = 0;
                touchEndX = 0;
                touchStartY = 0;
                touchEndY = 0;
                return;
            }

            // Якщо SWIPE (> 50px) - рухати карусель
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
            touchStartY = 0;
            touchEndY = 0;
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

