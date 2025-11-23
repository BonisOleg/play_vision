/**
 * Home Page Components
 * Vanilla JS implementation without Alpine.js
 */

/**
 * Viewport Height Manager для iOS Safari fix
 */
class ViewportHeightManager {
    constructor() {
        this.updateViewportHeight();
        this.attachEvents();
    }

    updateViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    attachEvents() {
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                this.updateViewportHeight();
            }, 100);
        });

        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.updateViewportHeight();
            }, 200);
        });
    }
}

class HeroCarousel {
    constructor(element) {
        this.element = element;
        this.currentSlide = 0;

        // Check for CMS slides data
        const cmsDataElement = document.getElementById('hero-slides-data');
        if (cmsDataElement) {
            try {
                this.slides = JSON.parse(cmsDataElement.textContent);
            } catch (e) {
                console.error('Failed to parse CMS slides data:', e);
                this.slides = this.getDefaultSlides();
            }
        } else {
            this.slides = this.getDefaultSlides();
        }

        this.titleElement = element.querySelector('.hero-title');
        this.subtitleElement = element.querySelector('.hero-subtitle');
        this.ctaButton = element.querySelector('.hero-buttons a');
        this.ctaButtonText = element.querySelector('.hero-buttons a .btn-text');
        this.dotsContainer = element.querySelector('.hero-slider-dots');

        this.init();
    }

    getDefaultSlides() {
        return [
            {
                title: 'Продуктивна практика у футбольних клубах',
                subtitle: 'Реальні кейси, стажування та менторинг з професіоналами індустрії',
                ctaText: 'Детальніше',
                ctaUrl: '/about/'
            },
            {
                title: 'Ми відкрились!',
                subtitle: 'Приєднуйтесь до спільноти футбольних професіоналів України',
                ctaText: 'Детальніше',
                ctaUrl: '/about/'
            },
            {
                title: 'Івенти',
                subtitle: 'Вебінари, майстер-класи та форуми від міжнародних експертів',
                ctaText: 'Переглянути івенти',
                ctaUrl: '/events/'
            },
            {
                title: 'Хаб знань — долучайся першим',
                subtitle: 'Ексклюзивні курси та матеріали для розвитку футбольних фахівців',
                ctaText: 'До хабу знань',
                ctaUrl: '/hub/'
            },
            {
                title: 'КОУЧИНГ',
                subtitle: 'Індивідуальний підхід до комплексного розвитку кожного футболіста',
                ctaText: 'Детальніше',
                ctaUrl: '/mentor-coaching/'
            },
            {
                title: 'Про нас',
                subtitle: 'Дізнайтеся більше про нашу місію, цінності та команду експертів',
                ctaText: 'Про нас',
                ctaUrl: '/about/'
            },
            {
                title: 'НАПРЯМИ',
                subtitle: '4 ключових напрямки для професійного зростання у футболі',
                ctaText: 'Детальніше',
                ctaUrl: '/about/#directions'
            }
        ];
    }

    init() {
        // Only show dots and autoplay if more than 1 slide
        if (this.slides.length > 1) {
            this.renderDots();
            this.startAutoplay();
        } else {
            // Hide dots container if only 1 slide
            if (this.dotsContainer) {
                this.dotsContainer.style.display = 'none';
            }
        }
        this.updateSlide();
    }

    renderDots() {
        if (!this.dotsContainer) return;

        this.dotsContainer.innerHTML = '';
        this.slides.forEach((slide, index) => {
            const dot = document.createElement('button');
            dot.className = 'slider-dot';
            dot.setAttribute('aria-label', `Слайд ${index + 1}`);

            if (index === 0) {
                dot.classList.add('active');
            }

            dot.addEventListener('click', () => this.goToSlide(index));
            this.dotsContainer.appendChild(dot);
        });
    }

    updateSlide() {
        const slide = this.slides[this.currentSlide];

        if (this.titleElement) {
            this.titleElement.textContent = slide.title;
        }

        if (this.subtitleElement) {
            this.subtitleElement.textContent = slide.subtitle;
        }

        if (this.ctaButton) {
            this.ctaButton.href = slide.ctaUrl;
            // Оновлюємо тільки текст всередині span.btn-text
            if (this.ctaButtonText && slide.ctaText) {
                this.ctaButtonText.textContent = slide.ctaText;
            } else if (slide.ctaText) {
                // Fallback для старого дизайну
                this.ctaButton.textContent = slide.ctaText;
            }
        }

        this.updateDots();
    }

    updateDots() {
        if (!this.dotsContainer) return;

        const dots = this.dotsContainer.querySelectorAll('.slider-dot');
        dots.forEach((dot, index) => {
            if (index === this.currentSlide) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    goToSlide(index) {
        this.currentSlide = index;
        this.updateSlide();
    }

    nextSlide() {
        this.currentSlide = (this.currentSlide + 1) % this.slides.length;
        this.updateSlide();
    }

    startAutoplay() {
        setInterval(() => {
            this.nextSlide();
        }, 5000);
    }
}

class CoursesCarousel {
    constructor(element) {
        this.element = element;
        this.currentIndex = 0;
        this.slidesPerView = 4; // 4 картки для featured courses
        this.track = element.querySelector('.carousel-track');
        this.prevBtn = element.querySelector('.featured-nav-prev');
        this.nextBtn = element.querySelector('.featured-nav-next');

        if (!this.track) return;

        this.totalSlides = this.track.querySelectorAll('.carousel-slide').length;

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
    }

    updateSlidesPerView() {
        const width = window.innerWidth;

        if (width < 576) {
            this.slidesPerView = 1;
        } else if (width < 768) {
            this.slidesPerView = 2;
        } else if (width < 1024) {
            this.slidesPerView = 3;
        } else {
            this.slidesPerView = 4; // 4 картки на desktop
        }
    }

    get slideWidth() {
        return 100 / this.slidesPerView;
    }

    get maxIndex() {
        return Math.max(0, this.totalSlides - this.slidesPerView);
    }

    updatePosition() {
        if (!this.track) return;

        const translateX = -(this.currentIndex * this.slideWidth);
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
}


// Ініціалізація home page
function initHome() {
    new ViewportHeightManager();

    const heroElement = document.querySelector('.hero-section');
    if (heroElement) {
        new HeroCarousel(heroElement);
    }

    const coursesElement = document.querySelector('.featured-carousel-container');
    if (coursesElement) {
        new CoursesCarousel(coursesElement);
    }
}

// Експорт для HTMX coordinator
window.initHome = initHome;

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', initHome);
