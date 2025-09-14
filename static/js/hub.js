/**
 * Hub Knowledge Base JavaScript
 * Handles interactive functionality for the knowledge hub page
 */

// Expert quotes carousel functionality
function quotesCarousel() {
    return {
        currentQuote: 0,
        quotes: 3, // Total number of quotes
        autoPlay: true,
        interval: null,

        init() {
            this.startAutoPlay();
            // Pause on hover
            this.$el.addEventListener('mouseenter', () => this.stopAutoPlay());
            this.$el.addEventListener('mouseleave', () => this.startAutoPlay());
        },

        setQuote(index) {
            this.currentQuote = index;
            this.restartAutoPlay();
        },

        nextQuote() {
            this.currentQuote = (this.currentQuote + 1) % this.quotes;
        },

        startAutoPlay() {
            if (this.autoPlay) {
                this.interval = setInterval(() => {
                    this.nextQuote();
                }, 15000); // 15 seconds
            }
        },

        stopAutoPlay() {
            if (this.interval) {
                clearInterval(this.interval);
                this.interval = null;
            }
        },

        restartAutoPlay() {
            this.stopAutoPlay();
            this.startAutoPlay();
        }
    };
}

// Materials carousel functionality
function materialsCarousel() {
    return {
        currentSlide: 0,
        totalSlides: 0,
        autoPlay: true,
        interval: null,

        init() {
            this.totalSlides = this.$el.querySelectorAll('.material-slide').length;
            if (this.totalSlides > 1) {
                this.startAutoPlay();
                // Pause on hover
                this.$el.addEventListener('mouseenter', () => this.stopAutoPlay());
                this.$el.addEventListener('mouseleave', () => this.startAutoPlay());
            }
        },

        nextSlide() {
            this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
            this.restartAutoPlay();
        },

        prevSlide() {
            this.currentSlide = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
            this.restartAutoPlay();
        },

        startAutoPlay() {
            if (this.autoPlay && this.totalSlides > 1) {
                this.interval = setInterval(() => {
                    this.nextSlide();
                }, 20000); // 20 seconds as specified in requirements
            }
        },

        stopAutoPlay() {
            if (this.interval) {
                clearInterval(this.interval);
                this.interval = null;
            }
        },

        restartAutoPlay() {
            this.stopAutoPlay();
            this.startAutoPlay();
        }
    };
}

// Filter functionality
class HubFilters {
    constructor() {
        this.initFilters();
        this.initSort();
        this.initSearch();
        this.initFavorites();
    }

    initFilters() {
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) return;

        // Auto-submit on filter change
        const filterInputs = filterForm.querySelectorAll('input[type="radio"]');
        const debouncedSubmit = this.debounce(() => {
            filterForm.submit();
        }, 300);

        filterInputs.forEach(input => {
            input.addEventListener('change', () => {
                debouncedSubmit();
            });
        });

        // Reset filters
        const resetBtn = filterForm.querySelector('a[href*="course_list"]');
        if (resetBtn) {
            resetBtn.addEventListener('click', (e) => {
                e.preventDefault();
                filterInputs.forEach(input => input.checked = false);
                window.location.href = resetBtn.href;
            });
        }
    }

    initSort() {
        const sortSelect = document.getElementById('sort');
        if (!sortSelect) return;

        sortSelect.addEventListener('change', () => {
            const url = new URL(window.location);
            url.searchParams.set('sort', sortSelect.value);
            window.location.href = url.toString();
        });
    }

    initSearch() {
        const searchForm = document.getElementById('searchForm');
        const searchInput = searchForm?.querySelector('.search-input');
        if (!searchInput) return;

        // Search suggestions (simple implementation)
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.handleSearchSuggestions(e.target.value);
            }, 300);
        });

        // Submit on Enter
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchForm.submit();
            }
        });
    }

    initFavorites() {
        const favoriteButtons = document.querySelectorAll('.favorite-btn');
        favoriteButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleFavoriteClick(e, btn);
            });
        });
    }

    handleSearchSuggestions(query) {
        // Enhanced search suggestions with autocomplete
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        // Show loading state
        this.showSuggestionsLoading();

        // Simulate API call with timeout (replace with actual AJAX)
        setTimeout(() => {
            const suggestions = this.generateSuggestions(query);
            this.displaySuggestions(suggestions, query);
        }, 200);
    }

    generateSuggestions(query) {
        // Mock suggestions - replace with actual API call
        const mockSuggestions = [
            { type: 'course', title: 'Python для початківців', category: 'Програмування' },
            { type: 'course', title: 'Data Science з Python', category: 'Аналітика' },
            { type: 'course', title: 'Web-розробка з Django', category: 'Веб-розробка' },
            { type: 'material', title: 'Вступ до алгоритмів', category: 'Комп\'ютерні науки' },
            { type: 'material', title: 'Основи дизайну', category: 'Дизайн' }
        ];

        return mockSuggestions.filter(item =>
            item.title.toLowerCase().includes(query.toLowerCase()) ||
            item.category.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 5);
    }

    displaySuggestions(suggestions, query) {
        let suggestionsContainer = document.getElementById('search-suggestions');

        if (!suggestionsContainer) {
            suggestionsContainer = this.createSuggestionsContainer();
        }

        if (suggestions.length === 0) {
            suggestionsContainer.innerHTML = `
                <div class="suggestion-item no-results">
                    <span class="suggestion-text">Результатів не знайдено для "${query}"</span>
                </div>
            `;
        } else {
            suggestionsContainer.innerHTML = suggestions.map((item, index) => `
                <div class="suggestion-item" data-index="${index}" data-type="${item.type}">
                    <span class="suggestion-icon">${item.type === 'course' ? '📚' : '📄'}</span>
                    <div class="suggestion-content">
                        <span class="suggestion-title">${this.highlightQuery(item.title, query)}</span>
                        <span class="suggestion-category">${item.category}</span>
                    </div>
                </div>
            `).join('');

            // Add click handlers
            suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    const title = item.querySelector('.suggestion-title').textContent;
                    this.selectSuggestion(title);
                });
            });
        }

        suggestionsContainer.classList.add('visible');
    }

    createSuggestionsContainer() {
        const container = document.createElement('div');
        container.id = 'search-suggestions';
        container.className = 'search-suggestions-container';

        const searchInput = document.querySelector('.search-input');
        const searchWrapper = searchInput.closest('.search-input-wrapper') || searchInput.parentElement;
        searchWrapper.style.position = 'relative';
        searchWrapper.appendChild(container);

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .search-suggestions-container {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid var(--hub-border);
                border-top: none;
                border-radius: 0 0 var(--hub-radius) var(--hub-radius);
                box-shadow: var(--hub-shadow);
                z-index: 100;
                max-height: 300px;
                overflow-y: auto;
                opacity: 0;
                transform: translateY(-10px);
                transition: all 0.2s ease;
                pointer-events: none;
            }
            
            .search-suggestions-container.visible {
                opacity: 1;
                transform: translateY(0);
                pointer-events: all;
            }
            
            .suggestion-item {
                display: flex;
                align-items: center;
                padding: 0.75rem;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
                transition: background 0.2s ease;
            }
            
            .suggestion-item:hover,
            .suggestion-item.highlighted {
                background: var(--hub-bg-gray);
            }
            
            .suggestion-item.no-results {
                color: var(--hub-text-light);
                cursor: default;
            }
            
            .suggestion-icon {
                margin-right: 0.75rem;
                font-size: 1.2rem;
            }
            
            .suggestion-content {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .suggestion-title {
                font-weight: 500;
                color: var(--hub-text);
                margin-bottom: 0.25rem;
            }
            
            .suggestion-category {
                font-size: 0.85rem;
                color: var(--hub-text-light);
            }
            
            .suggestion-title mark {
                background: var(--hub-primary);
                color: white;
                padding: 0.1rem 0.2rem;
                border-radius: 2px;
            }
            
            .search-suggestions-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
                color: var(--hub-text-light);
            }
        `;

        if (!document.querySelector('#search-suggestions-styles')) {
            style.id = 'search-suggestions-styles';
            document.head.appendChild(style);
        }

        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-input-wrapper')) {
                this.hideSuggestions();
            }
        });

        return container;
    }

    showSuggestionsLoading() {
        let suggestionsContainer = document.getElementById('search-suggestions');

        if (!suggestionsContainer) {
            suggestionsContainer = this.createSuggestionsContainer();
        }

        suggestionsContainer.innerHTML = `
            <div class="search-suggestions-loading">
                <span>🔍 Пошук...</span>
            </div>
        `;
        suggestionsContainer.classList.add('visible');
    }

    hideSuggestions() {
        const suggestionsContainer = document.getElementById('search-suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.classList.remove('visible');
        }
    }

    selectSuggestion(title) {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.value = title;
            this.hideSuggestions();

            // Submit the form
            const form = searchInput.closest('form');
            if (form) {
                form.submit();
            }
        }
    }

    highlightQuery(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    handleFavoriteClick(e, btn) {
        e.preventDefault();
        e.stopPropagation();

        const courseId = btn.dataset.courseId;
        if (!courseId) return;

        // Optimistic UI update
        btn.classList.toggle('active');

        // Handle HTMX response
        btn.addEventListener('htmx:afterRequest', (event) => {
            if (event.detail.successful) {
                // Success feedback
                this.showToast(
                    btn.classList.contains('active')
                        ? 'Додано в улюблені'
                        : 'Видалено з улюблених',
                    'success'
                );
            } else {
                // Revert optimistic update on error
                btn.classList.toggle('active');
                this.showToast('Помилка при оновленні улюблених', 'error');
            }
        });
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        // Style the toast
        Object.assign(toast.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            background: type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#333',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '6px',
            zIndex: '1001',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);

        // Animate out and remove
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Intersection Observer for lazy loading and animations
class HubAnimations {
    constructor() {
        this.initIntersectionObserver();
        this.initParallax();
    }

    initIntersectionObserver() {
        if (!('IntersectionObserver' in window)) return;

        const options = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');

                    // Lazy load images
                    const imgs = entry.target.querySelectorAll('img[data-src]');
                    imgs.forEach(img => this.lazyLoadImage(img));
                }
            });
        }, options);

        // Observe elements for animation
        const animatedElements = document.querySelectorAll('.product-card, .material-card, .section-title');
        animatedElements.forEach(el => {
            el.classList.add('animate-on-scroll');
            observer.observe(el);
        });
    }

    lazyLoadImage(img) {
        const src = img.dataset.src;
        if (!src) return;

        img.src = src;
        img.removeAttribute('data-src');
        img.classList.add('loaded');
    }

    initParallax() {
        // Simple parallax effect for hero sections
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        const parallaxElements = document.querySelectorAll('[data-parallax]');
        if (parallaxElements.length === 0) return;

        let ticking = false;

        const updateParallax = () => {
            const scrollY = window.pageYOffset;

            parallaxElements.forEach(el => {
                const speed = el.dataset.parallax || 0.5;
                const yPos = -(scrollY * speed);
                el.style.transform = `translateY(${yPos}px)`;
            });

            ticking = false;
        };

        const requestTick = () => {
            if (!ticking) {
                requestAnimationFrame(updateParallax);
                ticking = true;
            }
        };

        window.addEventListener('scroll', requestTick, { passive: true });
    }
}

// Performance optimizations
class HubPerformance {
    constructor() {
        this.initImageOptimization();
        this.initPrefetching();
    }

    initImageOptimization() {
        // Convert images to WebP if supported
        if (this.supportsWebP()) {
            const images = document.querySelectorAll('img[src$=".jpg"], img[src$=".png"]');
            images.forEach(img => {
                const webpSrc = img.src.replace(/\.(jpg|png)$/i, '.webp');

                // Test if WebP version exists
                const testImg = new Image();
                testImg.onload = () => {
                    img.src = webpSrc;
                };
                testImg.src = webpSrc;
            });
        }
    }

    initPrefetching() {
        // Prefetch course detail pages on hover
        const courseLinks = document.querySelectorAll('.product-title a, .material-card a');
        courseLinks.forEach(link => {
            link.addEventListener('mouseenter', () => {
                this.prefetchPage(link.href);
            }, { once: true });
        });
    }

    prefetchPage(url) {
        if (document.querySelector(`link[rel="prefetch"][href="${url}"]`)) return;

        const linkEl = document.createElement('link');
        linkEl.rel = 'prefetch';
        linkEl.href = url;
        document.head.appendChild(linkEl);
    }

    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }
}

// Accessibility enhancements
class HubAccessibility {
    constructor() {
        this.initKeyboardNavigation();
        this.initFocusManagement();
        this.initScreenReaderSupport();
    }

    initKeyboardNavigation() {
        // Arrow key navigation for carousels
        document.addEventListener('keydown', (e) => {
            if (e.target.closest('.quotes-carousel')) {
                this.handleCarouselKeyboard(e, 'quotes');
            } else if (e.target.closest('.materials-carousel')) {
                this.handleCarouselKeyboard(e, 'materials');
            }
        });

        // Skip links
        this.addSkipLinks();
    }

    handleCarouselKeyboard(e, type) {
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            e.preventDefault();
            const direction = e.key === 'ArrowLeft' ? 'prev' : 'next';

            // Trigger Alpine.js methods
            const carousel = e.target.closest(`[x-data*="${type}Carousel"]`);
            if (carousel && carousel._x_dataStack) {
                const data = carousel._x_dataStack[0];
                if (direction === 'next') {
                    data.nextSlide ? data.nextSlide() : data.nextQuote();
                } else {
                    data.prevSlide ? data.prevSlide() : data.setQuote(Math.max(0, data.currentQuote - 1));
                }
            }
        }
    }

    initFocusManagement() {
        // Manage focus for mobile filters
        const filtersToggle = document.querySelector('.mobile-filters-toggle');
        const filtersContent = document.querySelector('.filters-content');

        if (filtersToggle && filtersContent) {
            filtersToggle.addEventListener('click', () => {
                setTimeout(() => {
                    if (filtersContent.classList.contains('mobile-open')) {
                        const firstInput = filtersContent.querySelector('input');
                        if (firstInput) firstInput.focus();
                    }
                }, 100);
            });
        }
    }

    initScreenReaderSupport() {
        // Add aria-labels and descriptions
        this.enhanceCarouselAccessibility();
        this.enhanceFilterAccessibility();
    }

    enhanceCarouselAccessibility() {
        const carousels = document.querySelectorAll('[data-carousel]');
        carousels.forEach(carousel => {
            carousel.setAttribute('role', 'region');
            carousel.setAttribute('aria-label', 'Карусель матеріалів');

            const slides = carousel.querySelectorAll('.material-slide, .quote-slide');
            slides.forEach((slide, index) => {
                slide.setAttribute('aria-label', `Слайд ${index + 1} з ${slides.length}`);
            });
        });
    }

    enhanceFilterAccessibility() {
        const filterGroups = document.querySelectorAll('.filter-group');
        filterGroups.forEach(group => {
            const heading = group.querySelector('h4');
            const options = group.querySelectorAll('.filter-option');

            if (heading) {
                const id = `filter-${heading.textContent.toLowerCase().replace(/\s+/g, '-')}`;
                heading.id = id;

                options.forEach(option => {
                    option.setAttribute('aria-describedby', id);
                });
            }
        });
    }

    addSkipLinks() {
        const skipLinks = document.createElement('div');
        skipLinks.className = 'skip-links';
        skipLinks.innerHTML = `
            <a href="#main-content" class="skip-link">Перейти до основного контенту</a>
            <a href="#filters" class="skip-link">Перейти до фільтрів</a>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .skip-links {
                position: absolute;
                top: -100px;
                left: 0;
                z-index: 1000;
            }
            .skip-link {
                position: absolute;
                left: -10000px;
                width: 1px;
                height: 1px;
                overflow: hidden;
            }
            .skip-link:focus {
                position: static;
                left: auto;
                width: auto;
                height: auto;
                overflow: visible;
                background: var(--hub-primary);
                color: white;
                padding: 0.5rem 1rem;
                text-decoration: none;
                border-radius: 4px;
            }
        `;

        document.head.appendChild(style);
        document.body.insertBefore(skipLinks, document.body.firstChild);
    }
}

// Alpine.js components are now defined inline in the template

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components
    new HubFilters();
    new HubAnimations();
    new HubPerformance();
    new HubAccessibility();

    // Add main content landmark
    const mainContent = document.querySelector('.products-content');
    if (mainContent) {
        mainContent.id = 'main-content';
    }

    // Add filters landmark
    const filters = document.querySelector('.filters-sidebar');
    if (filters) {
        filters.id = 'filters';
    }

    console.log('Hub Knowledge Base initialized successfully');
});

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
    // Refresh HTMX elements on navigation
    if (typeof htmx !== 'undefined') {
        htmx.process(document.body);
    }
});

// Export functions for global access (if needed)
window.HubKnowledgeBase = {
    quotesCarousel,
    materialsCarousel,
    HubFilters,
    HubAnimations,
    HubPerformance,
    HubAccessibility
};

// Make Alpine.js functions globally available
window.quotesCarousel = quotesCarousel;
window.materialsCarousel = materialsCarousel;
