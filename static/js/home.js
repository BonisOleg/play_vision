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
                this.slides = [];
            }
        } else {
            this.slides = [];
        }

        // Якщо немає слайдів - не ініціалізувати carousel
        if (this.slides.length === 0) {
            return;
        }

        this.titleElement = element.querySelector('.hero-title');
        this.subtitleElement = element.querySelector('.hero-subtitle');
        this.ctaButton = element.querySelector('.hero-buttons a');
        this.ctaButtonText = element.querySelector('.hero-buttons a .btn-text');
        this.dotsContainer = element.querySelector('.hero-slider-dots');
        this.sectionBg = element.querySelector('.section-bg');

        // Кеш для зображень
        this.imageCache = new Map();
        this.preloadedSlides = new Set();

        this.init();
    }

    init() {
        // Preload перші слайди одразу
        this.preloadSlides();
        
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

    // Preload перших 2-3 слайдів
    preloadSlides() {
        const slidesToPreload = Math.min(3, this.slides.length);
        
        for (let i = 0; i < slidesToPreload; i++) {
            this.preloadSlide(i, i === 0 ? 'high' : 'low');
        }
    }

    // Preload одного слайда
    preloadSlide(index, priority = 'low') {
        if (this.preloadedSlides.has(index)) return;
        
        const slide = this.slides[index];
        if (!slide) return;
        
        const imageUrl = this.getOptimizedImageUrl(slide.image);
        
        if (imageUrl) {
            const img = new Image();
            img.fetchPriority = priority;
            img.src = imageUrl;
            img.onload = () => {
                this.imageCache.set(index, img);
                this.preloadedSlides.add(index);
            };
        }
    }

    // Cloudinary оптимізація для мобільних
    getOptimizedImageUrl(url) {
        if (!url) return null;
        
        // Якщо це Cloudinary URL
        if (url.includes('cloudinary.com')) {
            const isMobile = window.innerWidth <= 768;
            if (isMobile) {
                // Додати трансформацію w_800 для мобільних
                return url.replace('/upload/', '/upload/w_800,f_auto,q_auto/');
            } else {
                // Для desktop - auto format і quality
                return url.replace('/upload/', '/upload/f_auto,q_auto/');
            }
        }
        
        return url;
    }

    // Preload наступних слайдів
    preloadNextSlides() {
        const next1 = (this.currentSlide + 1) % this.slides.length;
        const next2 = (this.currentSlide + 2) % this.slides.length;
        
        this.preloadSlide(next1, 'low');
        this.preloadSlide(next2, 'low');
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

        // Оновлюємо background-зображення/відео
        if (this.sectionBg) {
            const existingVideo = this.sectionBg.querySelector('.section-bg-video');
            const existingImage = this.sectionBg.querySelector('.section-bg-image');

            // Видаляємо існуючі елементи
            if (existingVideo) {
                existingVideo.remove();
            }
            if (existingImage) {
                existingImage.remove();
            }

            // Додаємо новий контент
            if (slide.video && slide.video.trim() !== '') {
                const video = document.createElement('video');
                video.className = 'section-bg-video';
                video.muted = true;
                video.loop = true;
                video.preload = 'metadata';
                video.playsInline = true;
                const source = document.createElement('source');
                source.src = slide.video;
                source.type = 'video/mp4';
                video.appendChild(source);
                
                // Обробка помилок завантаження відео - fallback на зображення
                video.addEventListener('error', () => {
                    if (slide.image && slide.image.trim() !== '') {
                        video.style.display = 'none';
                        const imageUrl = this.getOptimizedImageUrl(slide.image);
                        if (imageUrl) {
                            const img = document.createElement('img');
                            img.className = 'section-bg-image';
                            img.src = imageUrl;
                            img.alt = slide.title || '';
                            img.loading = 'eager';
                            this.sectionBg.appendChild(img);
                        }
                    }
                });
                
                // Якщо є зображення, додаємо його як fallback всередині відео
                if (slide.image && slide.image.trim() !== '') {
                    const imageUrl = this.getOptimizedImageUrl(slide.image);
                    if (imageUrl) {
                        const img = document.createElement('img');
                        img.className = 'section-bg-image';
                        img.src = imageUrl;
                        img.alt = slide.title || '';
                        img.loading = 'eager';
                        video.appendChild(img);
                    }
                }
                
                this.sectionBg.appendChild(video);
                // Спробувати відтворити відео
                video.play().catch(() => {
                    // Якщо автоплей не працює, відео все одно показуватиметься
                });
            } else if (slide.image && slide.image.trim() !== '') {
                // Використовуємо кешоване зображення якщо є
                const imageUrl = this.imageCache.has(this.currentSlide) 
                    ? this.imageCache.get(this.currentSlide).src 
                    : this.getOptimizedImageUrl(slide.image);
                
                if (imageUrl) {
                    const img = document.createElement('img');
                    img.className = 'section-bg-image';
                    img.src = imageUrl;
                    img.alt = slide.title || '';
                    img.loading = 'eager';
                    this.sectionBg.appendChild(img);
                }
            }
        }

        // Preload наступні 2 слайди в фоні
        this.preloadNextSlides();

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


// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    new ViewportHeightManager();

    const heroElement = document.querySelector('.hero-section');
    if (heroElement) {
        const carousel = new HeroCarousel(heroElement);
        // Carousel може не ініціалізуватися якщо немає слайдів
    }

    const coursesElement = document.querySelector('.featured-carousel-container');
    if (coursesElement) {
        new CoursesCarousel(coursesElement);
    }

});
