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
        this.badgeElement = element.querySelector('.hero-badge');
        this.ctaButton = element.querySelector('.hero-buttons a');
        this.dotsContainer = element.querySelector('.hero-slider-dots');

        this.init();
    }

    getDefaultSlides() {
        return [
            {
                title: 'Продуктивна практика у футбольних клубах',
                subtitle: 'Реальні кейси, стажування та менторинг з професіоналами індустрії',
                badge: 'ГОЛОВНЕ ЗАРАЗ',
                ctaText: 'Дізнатись більше',
                ctaUrl: '/about/'
            },
            {
                title: 'Ми відкрились!',
                subtitle: 'Приєднуйтесь до спільноти футбольних професіоналів України',
                badge: 'НОВИНА',
                ctaText: 'Дізнатись більше',
                ctaUrl: '/about/'
            },
            {
                title: 'Івенти',
                subtitle: 'Вебінари, майстер-класи та форуми від міжнародних експертів',
                badge: 'ПОДІЯ',
                ctaText: 'Переглянути івенти',
                ctaUrl: '/events/'
            },
            {
                title: 'Хаб знань — долучайся першим',
                subtitle: 'Ексклюзивні курси та матеріали для розвитку футбольних фахівців',
                badge: 'НАВЧАННЯ',
                ctaText: 'До хабу знань',
                ctaUrl: '/hub/'
            },
            {
                title: 'КОУЧИНГ',
                subtitle: 'Індивідуальний підхід до комплексного розвитку кожного футболіста',
                badge: 'РОЗВИТОК',
                ctaText: 'Дізнатись більше',
                ctaUrl: '/mentor-coaching/'
            },
            {
                title: 'Про нас',
                subtitle: 'Дізнайтеся більше про нашу місію, цінності та команду експертів',
                badge: 'ПРО ПРОЕКТ',
                ctaText: 'Про нас',
                ctaUrl: '/about/'
            },
            {
                title: 'НАПРЯМИ',
                subtitle: '4 ключових напрямки для професійного зростання у футболі',
                badge: 'НАПРЯМКИ',
                ctaText: 'Дізнатись більше',
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

        if (this.badgeElement && slide.badge) {
            this.badgeElement.textContent = slide.badge;
        }

        if (this.titleElement) {
            this.titleElement.textContent = slide.title;
        }

        if (this.subtitleElement) {
            this.subtitleElement.textContent = slide.subtitle;
        }

        if (this.ctaButton) {
            this.ctaButton.href = slide.ctaUrl;
            if (slide.ctaText) {
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
        this.slidesPerView = 3;
        this.track = element.querySelector('.carousel-track');
        this.prevBtn = element.querySelector('.carousel-btn-prev');
        this.nextBtn = element.querySelector('.carousel-btn-next');

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

        window.addEventListener('resize', () => {
            this.updateSlidesPerView();
            this.updatePosition();
            this.updateButtons();
        });
    }

    updateSlidesPerView() {
        if (window.innerWidth < 768) {
            this.slidesPerView = 1;
        } else if (window.innerWidth < 1024) {
            this.slidesPerView = 2;
        } else {
            this.slidesPerView = 3;
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

/* ВИДАЛЕНО АНІМАЦІЮ ГЕКСАГОНІВ (8-й скрін - статично БЕЗ анімації) */
/*
class MentorHexagonAnimation {
    ... вся анімація видалена для статичного дизайну ...
}
*/

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    new ViewportHeightManager();

    const heroElement = document.querySelector('.hero-section');
    if (heroElement) {
        new HeroCarousel(heroElement);
    }

    const coursesElement = document.querySelector('.featured-carousel-container');
    if (coursesElement) {
        new CoursesCarousel(coursesElement);
    }

    // Анімацію гексагонів видалено (8-й скрін - статичний дизайн)
    // const mentorAnimationContainer = document.querySelector('.mentor-animation-container');
    // if (mentorAnimationContainer) {
    //     new MentorHexagonAnimation(mentorAnimationContainer);
    // }
});
