/**
 * Hub Knowledge Page Main JS (скопійовано логіку з home.js та main-courses-carousel.js)
 */

'use strict';

/**
 * Hero Carousel для Хабу Знань (адаптовано з home.js)
 */
class HubHeroCarousel {
    constructor(element) {
        this.element = element;
        this.currentSlide = 0;
        
        // Завантажити слайди з JSON або використати fallback
        this.slides = this.loadSlidesFromJSON();
        
        this.titleElement = element.querySelector('.hero-title');
        this.subtitleElement = element.querySelector('.hero-subtitle');
        this.ctaButton = element.querySelector('.hero-buttons a');
        this.ctaButtonText = element.querySelector('.hero-buttons a .btn-text');
        this.dotsContainer = element.querySelector('.hero-slider-dots');
        this.heroBg = element.querySelector('.hub-hero-bg');

        // Кеш для зображень
        this.imageCache = new Map();
        this.preloadedSlides = new Set();

        this.init();
    }
    
    loadSlidesFromJSON() {
        // Спробувати завантажити дані з JSON
        const dataElement = document.getElementById('hub-hero-slides-data');
        if (dataElement) {
            try {
                const slides = JSON.parse(dataElement.textContent);
                if (slides && slides.length > 0) {
                    // Зберегти всі дані з JSON, включаючи ctaText та ctaUrl
                    return slides.map(slide => ({
                        title: slide.title || '',
                        subtitle: slide.subtitle || '',
                        ctaText: slide.ctaText || 'Дізнатися',
                        ctaUrl: slide.ctaUrl || '#catalog',
                        image: slide.image || null,
                        video: slide.video || null
                    }));
                }
            } catch (e) {
                console.warn('Failed to parse hub hero slides data:', e);
            }
        }
        
        // Fallback: дефолтні слайди
        return [
            {
                title: 'Програма лояльності Хабу Знань',
                subtitle: 'Твоя бібліотека футбольних знань',
                ctaText: 'Дізнатися',
                ctaUrl: '/loyalty/',
                image: null,
                video: null
            },
            {
                title: 'Ексклюзивні курси та матеріали',
                subtitle: 'Від базових знань до професійного рівня',
                ctaText: 'Переглянути курси',
                ctaUrl: '/hub/',
                image: null,
                video: null
            },
            {
                title: 'Знання, що працюють на полі',
                subtitle: 'Навчання від практиків, а не теоретиків',
                ctaText: 'Обрати напрям',
                ctaUrl: '/hub/',
                image: null,
                video: null
            }
        ];
    }

    init() {
        // Preload перші слайди одразу
        this.preloadSlides();
        
        if (this.slides.length > 1) {
            this.renderDots();
            this.startAutoplay();
        } else if (this.dotsContainer) {
            this.dotsContainer.style.display = 'none';
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
            this.ctaButton.href = slide.ctaUrl || '#catalog';
            const ctaText = slide.ctaText || 'Дізнатися';
            if (this.ctaButtonText) {
                this.ctaButtonText.textContent = ctaText;
            } else {
                this.ctaButton.textContent = ctaText;
            }
        }

        // Оновлюємо background-зображення/відео
        this.updateBackground(slide);

        // Preload наступні 2 слайди в фоні
        this.preloadNextSlides();

        this.updateDots();
    }

    updateBackground(slide) {
        if (!this.heroBg) return;
        
        // Видаляємо ВСІ існуючі img та video елементи
        const allImages = this.heroBg.querySelectorAll('img');
        const allVideos = this.heroBg.querySelectorAll('video');
        allImages.forEach(img => img.remove());
        allVideos.forEach(video => video.remove());

        // Додаємо новий контент
        if (slide.video && typeof slide.video === 'string' && slide.video.trim() !== '') {
            const video = document.createElement('video');
            video.className = 'hub-hero-bg-video';
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
                if (slide.image && typeof slide.image === 'string' && slide.image.trim() !== '') {
                    video.style.display = 'none';
                    const imageUrl = this.getOptimizedImageUrl(slide.image);
                    if (imageUrl) {
                        const img = document.createElement('img');
                        img.className = 'hub-hero-bg-image';
                        img.src = imageUrl;
                        img.alt = slide.title || '';
                        img.loading = 'eager';
                        this.heroBg.appendChild(img);
                    }
                }
            });
            
            // Якщо є зображення, додаємо його як fallback всередині відео
            if (slide.image && typeof slide.image === 'string' && slide.image.trim() !== '') {
                const imageUrl = this.getOptimizedImageUrl(slide.image);
                if (imageUrl) {
                    const img = document.createElement('img');
                    img.className = 'hub-hero-bg-image';
                    img.src = imageUrl;
                    img.alt = slide.title || '';
                    img.loading = 'eager';
                    video.appendChild(img);
                }
            }
            
            this.heroBg.appendChild(video);
            // Спробувати відтворити відео
            video.play().catch(() => {
                // Якщо автоплей не працює, відео все одно показуватиметься
            });
        } else if (slide.image && typeof slide.image === 'string' && slide.image.trim() !== '') {
            // Використовуємо кешоване зображення якщо є
            const imageUrl = this.imageCache.has(this.currentSlide) 
                ? this.imageCache.get(this.currentSlide).src 
                : this.getOptimizedImageUrl(slide.image);
            
            if (imageUrl) {
                const img = document.createElement('img');
                img.className = 'hub-hero-bg-image';
                img.src = imageUrl;
                img.alt = slide.title || '';
                img.loading = 'eager';
                this.heroBg.appendChild(img);
            }
        } else {
            // Fallback до дефолтного зображення (всі старі елементи вже видалені)
            const img = document.createElement('img');
            img.className = 'hub-hero-bg-image';
            img.src = '/static/images/Hiro.png';
            img.alt = slide.title || '';
            img.loading = 'eager';
            this.heroBg.appendChild(img);
        }
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

/**
 * Featured Carousel для "Найкращі" (скопійовано з main-courses-carousel.js)
 */
class HubFeaturedCarousel {
    constructor(element) {
        this.section = element;
        this.currentIndex = 0;
        this.track = element.querySelector('.hub-featured-carousel');
        this.prevBtn = element.querySelector('.hub-nav-prev');
        this.nextBtn = element.querySelector('.hub-nav-next');

        if (!this.track) {
            console.warn('Hub featured track not found');
            return;
        }

        this.slides = this.track.querySelectorAll('.hub-featured-card');
        this.totalSlides = this.slides.length;

        if (this.totalSlides === 0) {
            console.warn('No featured slides found');
            return;
        }

        this.init();
    }

    init() {
        // Затримка для коректного обчислення розмірів після завантаження
        requestAnimationFrame(() => {
            this.updatePosition();
            this.updateButtons();
        });
        this.attachEvents();
        
        // Обробка зміни розміру вікна для коректного перерахунку позиції
        window.addEventListener('resize', () => {
            requestAnimationFrame(() => {
                this.updatePosition();
            });
        });
    }

    attachEvents() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevSlide());
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextSlide());
        }

        // Touch/swipe support
        this.addTouchSupport();
    }

    get maxIndex() {
        return Math.max(0, this.totalSlides - 1);
    }

    updatePosition() {
        if (!this.track || this.slides.length === 0) return;
        
        // Отримуємо реальну ширину картки
        const firstSlide = this.slides[0];
        const slideWidth = firstSlide.offsetWidth;
        
        // Отримуємо gap з CSS (48px)
        const trackStyles = window.getComputedStyle(this.track);
        const gap = parseFloat(trackStyles.gap) || 48;
        
        const slideWithGap = slideWidth + gap;
        
        // Отримуємо ширину контейнера (section-content) для обчислення центрування
        const container = this.track.parentElement; // section-content
        const containerWidth = container.offsetWidth;
        
        // Обчислюємо відступ для центрування: (100% - 95%) / 2 = 2.5%
        const centerOffset = (containerWidth - slideWidth) / 2;
        
        // Обчислюємо зсув: для першої картки центруємо, для інших зсуваємо на ширину + gap
        const translateX = centerOffset - (this.currentIndex * slideWithGap);
        
        this.track.style.transform = `translateX(${translateX}px)`;
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
                    this.nextSlide();
                } else {
                    this.prevSlide();
                }
            }

            touchStartX = 0;
            touchEndX = 0;
        });
    }
}

/**
 * Обробка кнопки "Улюблене" (іконка сердечка)
 */
function initFavoriteButtons() {
    const favoriteButtons = document.querySelectorAll('.hub-favorite-icon, .hub-btn-favorite, .hub-favorite-btn');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const courseId = button.getAttribute('data-course-id');
            if (!courseId) return;
            
            try {
                const response = await fetch(`/hub/course/${courseId}/favorite/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.is_favorite) {
                        button.setAttribute('data-favorited', 'true');
                    } else {
                        button.removeAttribute('data-favorited');
                    }
                } else if (response.status === 401 || response.status === 403) {
                    // User not authenticated
                    alert('Будь ласка, увійдіть в систему для додавання до улюблених');
                }
            } catch (error) {
                console.error('Error toggling favorite:', error);
            }
        });
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Обробка згортання/розгортання опису в featured картках (тільки мобільні)
 */
function initDescriptionToggles() {
    const toggleButtons = document.querySelectorAll('.hub-featured-toggle');
    
    toggleButtons.forEach(button => {
        const handleToggle = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const wrapper = button.nextElementSibling;
            if (!wrapper || !wrapper.classList.contains('hub-featured-description-wrapper')) {
                console.warn('Description wrapper not found');
                return;
            }
            
            const isExpanded = button.getAttribute('aria-expanded') === 'true';
            const toggleText = button.querySelector('.toggle-text');
            
            if (isExpanded) {
                // Згортаємо
                button.setAttribute('aria-expanded', 'false');
                button.setAttribute('aria-label', 'Показати повний опис');
                wrapper.classList.remove('expanded');
                if (toggleText) toggleText.textContent = 'ще...';
            } else {
                // Розгортаємо
                button.setAttribute('aria-expanded', 'true');
                button.setAttribute('aria-label', 'Сховати повний опис');
                wrapper.classList.add('expanded');
                if (toggleText) toggleText.textContent = 'згорнути';
            }
        };
        
        // Click event
        button.addEventListener('click', handleToggle);
        
        // Keyboard support (Enter/Space)
        button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleToggle(e);
            }
        });
        
        // Touch events для запобігання конфлікту з carousel swipe
        button.addEventListener('touchstart', (e) => {
            e.stopPropagation();
        }, { passive: false });
        
        button.addEventListener('touchmove', (e) => {
            e.stopPropagation();
        }, { passive: false });
        
        button.addEventListener('touchend', (e) => {
            e.stopPropagation();
        }, { passive: false });
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Hero carousel
    const heroSection = document.querySelector('.hub-hero-section');
    if (heroSection) {
        new HubHeroCarousel(heroSection);
    }
    
    // Featured carousel
    const featuredSection = document.querySelector('.hub-featured-section');
    if (featuredSection) {
        new HubFeaturedCarousel(featuredSection);
    }
    
    // Favorite buttons
    initFavoriteButtons();
    
    // Description toggles
    initDescriptionToggles();
});

// Показувати індикатор під час будь-якого HTMX запиту до каталогу
document.body.addEventListener('htmx:beforeRequest', (e) => {
    if (e.detail.target?.id === 'catalog-content') {
        const indicator = document.getElementById('catalog-loading-indicator');
        if (indicator) {
            indicator.style.display = 'flex';
        }
    }
});

// Re-initialize favorite buttons after HTMX swap
document.body.addEventListener('htmx:afterSwap', (event) => {
    if (event.detail.target?.id === 'catalog-content') {
        initFavoriteButtons();
        
        // Сховати індикатор після успішного swap
        const indicator = document.getElementById('catalog-loading-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        // Розумний скрол: скролити тільки якщо каталог НЕ у viewport
        const catalogSection = document.getElementById('catalog');
        if (catalogSection) {
            const rect = catalogSection.getBoundingClientRect();
            const isVisible = rect.top >= 0 && rect.top <= window.innerHeight * 0.3;
            
            if (!isVisible) {
                catalogSection.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start'
                });
            }
        }
    }
});

// Обробка помилок при завантаженні каталогу
document.body.addEventListener('htmx:responseError', (e) => {
    if (e.detail.target?.id === 'catalog-content') {
        // Сховати індикатор при помилці
        const indicator = document.getElementById('catalog-loading-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        // Показати користувачу помилку
        const errorDiv = document.createElement('div');
        errorDiv.className = 'htmx-error-message';
        errorDiv.style.cssText = 'padding: 16px; margin: 16px 0; background: #fee; border: 1px solid #fcc; border-radius: 8px; color: #c33;';
        errorDiv.innerHTML = `
            <p style="margin: 0 0 8px 0; font-weight: 500;">Помилка завантаження каталогу</p>
            <button onclick="location.reload()" style="padding: 8px 16px; background: #c33; color: white; border: none; border-radius: 4px; cursor: pointer;">Оновити сторінку</button>
        `;
        
        // Видалити попередні повідомлення про помилки
        const existingError = e.detail.target.querySelector('.htmx-error-message');
        if (existingError) {
            existingError.remove();
        }
        
        e.detail.target.prepend(errorDiv);
    }
});

// Обробка помилок мережі
document.body.addEventListener('htmx:sendError', (e) => {
    if (e.detail.target?.id === 'catalog-content') {
        // Сховати індикатор при помилці
        const indicator = document.getElementById('catalog-loading-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        // Показати користувачу помилку
        const errorDiv = document.createElement('div');
        errorDiv.className = 'htmx-error-message';
        errorDiv.style.cssText = 'padding: 16px; margin: 16px 0; background: #fee; border: 1px solid #fcc; border-radius: 8px; color: #c33;';
        errorDiv.innerHTML = `
            <p style="margin: 0 0 8px 0; font-weight: 500;">Помилка з'єднання</p>
            <p style="margin: 0 0 8px 0; font-size: 0.875rem;">Перевірте інтернет-з'єднання та спробуйте ще раз.</p>
            <button onclick="location.reload()" style="padding: 8px 16px; background: #c33; color: white; border: none; border-radius: 4px; cursor: pointer;">Оновити сторінку</button>
        `;
        
        // Видалити попередні повідомлення про помилки
        const existingError = e.detail.target.querySelector('.htmx-error-message');
        if (existingError) {
            existingError.remove();
        }
        
        e.detail.target.prepend(errorDiv);
    }
});
