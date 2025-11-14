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
        
        // Слайди для Хабу Знань
        this.slides = [
            {
                title: 'Програма лояльності Хабу Знань',
                subtitle: 'Твоя бібліотека футбольних знань',
                ctaText: 'Дізнатися',
                ctaUrl: '/loyalty/'
            },
            {
                title: 'Ексклюзивні курси та матеріали',
                subtitle: 'Від базових знань до професійного рівня',
                ctaText: 'Переглянути курси',
                ctaUrl: '/hub/'
            },
            {
                title: 'Знання, що працюють на полі',
                subtitle: 'Навчання від практиків, а не теоретиків',
                ctaText: 'Обрати напрям',
                ctaUrl: '/hub/'
            }
        ];

        this.titleElement = element.querySelector('.hero-title');
        this.subtitleElement = element.querySelector('.hero-subtitle');
        this.ctaButton = element.querySelector('.hero-buttons a');
        this.ctaButtonText = element.querySelector('.hero-buttons a .btn-text');
        this.dotsContainer = element.querySelector('.hero-slider-dots');

        this.init();
    }

    init() {
        if (this.slides.length > 1) {
            this.renderDots();
            this.startAutoplay();
        } else if (this.dotsContainer) {
            this.dotsContainer.style.display = 'none';
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
            if (this.ctaButtonText && slide.ctaText) {
                this.ctaButtonText.textContent = slide.ctaText;
            } else if (slide.ctaText) {
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

        // Touch/swipe support
        this.addTouchSupport();
    }

    get maxIndex() {
        return Math.max(0, this.totalSlides - 1);
    }

    updatePosition() {
        if (!this.track) return;
        const translateX = -(this.currentIndex * 100);
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
 * Фільтри каталогу
 */
class HubFilters {
    constructor(form) {
        this.form = form;
        this.filterGroups = form.querySelectorAll('.hub-filter-group');
        this.resetBtn = form.querySelector('.hub-filter-reset');
        
        this.init();
    }

    init() {
        // Dropdown toggles
        this.filterGroups.forEach(group => {
            const toggle = group.querySelector('.hub-filter-toggle');
            if (toggle) {
                toggle.addEventListener('click', () => this.toggleGroup(group));
            }
        });

        // Reset filters (Відмінити)
        if (this.resetBtn) {
            this.resetBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.resetFilters();
            });
        }
        
        // Динамічне виділення активних чекбоксів
        this.attachCheckboxListeners();
    }

    toggleGroup(group) {
        const content = group.querySelector('.hub-filter-content');
        const isOpen = group.classList.contains('active');

        if (isOpen) {
            group.classList.remove('active');
            content.style.display = 'none';
        } else {
            group.classList.add('active');
            content.style.display = 'block';
        }
    }

    resetFilters() {
        // Uncheck all inputs
        this.form.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(input => {
            input.checked = false;
        });
        
        // Remove active classes
        this.form.querySelectorAll('.hub-filter-checkbox-active').forEach(label => {
            label.classList.remove('hub-filter-checkbox-active');
        });
        
        // Clear search input
        const searchForm = document.querySelector('.hub-search-form');
        if (searchForm) {
            const searchInput = searchForm.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.value = '';
            }
        }
        
        // Trigger HTMX request to reload without filters
        if (typeof htmx !== 'undefined') {
            htmx.ajax('GET', window.location.pathname, {
                target: '#catalog-content',
                swap: 'innerHTML'
            });
        } else {
            // Fallback if HTMX not available
            window.location.href = window.location.pathname;
        }
    }
    
    attachCheckboxListeners() {
        const checkboxes = this.form.querySelectorAll('.hub-filter-checkbox input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const label = e.target.closest('.hub-filter-checkbox');
                if (e.target.checked) {
                    label.classList.add('hub-filter-checkbox-active');
                } else {
                    label.classList.remove('hub-filter-checkbox-active');
                }
            });
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

/**
 * Менеджер пошуку з кнопкою очищення
 */
class SearchManager {
    constructor() {
        this.searchForm = document.querySelector('.hub-search-form');
        this.searchInput = document.querySelector('[data-search-input]');
        this.clearButton = document.querySelector('[data-search-clear]');
        
        if (!this.searchForm || !this.searchInput || !this.clearButton) {
            return;
        }
        
        this.init();
    }
    
    init() {
        // Show/hide clear button based on input value
        this.toggleClearButton();
        
        // Listen to input changes
        this.searchInput.addEventListener('input', () => {
            this.toggleClearButton();
        });
        
        // Handle clear button click
        this.clearButton.addEventListener('click', () => {
            this.clearSearch();
        });
    }
    
    toggleClearButton() {
        const hasValue = this.searchInput.value.trim().length > 0;
        
        if (hasValue) {
            this.clearButton.classList.add('visible');
        } else {
            this.clearButton.classList.remove('visible');
        }
    }
    
    clearSearch() {
        // Clear input
        this.searchInput.value = '';
        
        // Hide clear button
        this.clearButton.classList.remove('visible');
        
        // Trigger HTMX request with filters included
        if (typeof htmx !== 'undefined') {
            // Get current filter form values
            const filterForm = document.querySelector('.hub-filter-form');
            const formData = new FormData(filterForm);
            const params = new URLSearchParams(formData);
            
            // Make HTMX request
            htmx.ajax('GET', `${window.location.pathname}?${params.toString()}`, {
                target: '#catalog-content',
                swap: 'innerHTML'
            });
        } else {
            // Fallback: submit form without search query
            this.searchForm.submit();
        }
    }
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
    
    // Filters
    const filtersForm = document.querySelector('.hub-filters-form');
    if (filtersForm) {
        new HubFilters(filtersForm);
    }
    
    // Search manager (clear button)
    new SearchManager();
    
    // Favorite buttons
    initFavoriteButtons();
});

// Re-initialize favorite buttons after HTMX swap
document.body.addEventListener('htmx:afterSwap', (event) => {
    if (event.detail.target.id === 'catalog-content') {
        initFavoriteButtons();
    }
});
