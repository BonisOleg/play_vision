/**
 * HUB V2 - Хаб Знань JavaScript
 * Повністю переписаний модуль для сторінки Хаб Знань
 * ES6 Classes, без інлайн скриптів
 */

'use strict';

// === MATERIALS CAROUSEL CLASS ===
class MaterialsCarousel {
    constructor(element) {
        this.element = element;
        this.track = element.querySelector('.carousel-content');
        this.slides = element.querySelectorAll('.material-slide');
        this.prevBtn = element.querySelector('.nav-prev');
        this.nextBtn = element.querySelector('.nav-next');

        this.currentIndex = 0;
        this.totalSlides = this.slides.length;

        this.autoplayInterval = null;
        this.autoplayDelay = 20000;

        if (this.track && this.totalSlides > 0) {
            this.init();
        }
    }

    init() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevSlide());
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextSlide());
        }

        this.updatePosition();

        if (this.totalSlides > 1) {
            this.startAutoplay();
            this.element.addEventListener('mouseenter', () => this.stopAutoplay());
            this.element.addEventListener('mouseleave', () => this.startAutoplay());
        }

        window.addEventListener('resize', () => this.updatePosition());
    }

    updatePosition() {
        const offset = -this.currentIndex * 100;
        this.track.style.transform = `translateX(${offset}%)`;
    }

    nextSlide() {
        this.currentIndex = (this.currentIndex + 1) % this.totalSlides;
        this.updatePosition();
        this.resetAutoplay();
    }

    prevSlide() {
        this.currentIndex = (this.currentIndex - 1 + this.totalSlides) % this.totalSlides;
        this.updatePosition();
        this.resetAutoplay();
    }

    startAutoplay() {
        if (this.totalSlides <= 1) return;
        this.stopAutoplay();
        this.autoplayInterval = setInterval(() => {
            this.nextSlide();
        }, this.autoplayDelay);
    }

    stopAutoplay() {
        if (this.autoplayInterval) {
            clearInterval(this.autoplayInterval);
            this.autoplayInterval = null;
        }
    }

    resetAutoplay() {
        this.stopAutoplay();
        this.startAutoplay();
    }
}

// === FILTERS MANAGER CLASS ===
class FiltersManager {
    constructor(form) {
        this.form = form;
        this.filterOptions = form.querySelectorAll('input[type="checkbox"], input[type="radio"]');
        this.clearBtn = form.querySelector('[data-action="clear-filters"]');
        this.quickFilters = form.querySelector('.quick-filters');
        this.filterTags = form.querySelector('.filter-tags');
        this.activeCount = form.querySelector('.active-filters-count');

        this.init();
    }

    init() {
        this.filterOptions.forEach(input => {
            input.addEventListener('change', () => this.updateFilterTags());
        });

        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => this.clearAllFilters());
        }

        const toggleButtons = this.form.querySelectorAll('.filter-toggle');
        toggleButtons.forEach(btn => {
            btn.addEventListener('click', () => this.toggleSubFilters(btn));
        });

        this.updateFilterTags();
    }

    toggleSubFilters(button) {
        const subFilters = button.closest('.filter-group').querySelector('.sub-filters');
        if (subFilters) {
            const isExpanded = button.getAttribute('aria-expanded') === 'true';
            button.setAttribute('aria-expanded', !isExpanded);
            subFilters.classList.toggle('is-hidden');
        }
    }

    updateFilterTags() {
        const activeFilters = Array.from(this.filterOptions).filter(input => input.checked);

        if (activeFilters.length > 0) {
            this.quickFilters?.classList.remove('is-hidden');
            this.clearBtn?.classList.remove('is-hidden');
            this.updateActiveCount(activeFilters.length);
        } else {
            this.quickFilters?.classList.add('is-hidden');
            this.clearBtn?.classList.add('is-hidden');
            this.updateActiveCount(0);
        }

        if (this.filterTags) {
            this.filterTags.innerHTML = '';
            activeFilters.forEach(input => {
                const tag = this.createFilterTag(input);
                this.filterTags.appendChild(tag);
            });
        }
    }

    createFilterTag(input) {
        const tag = document.createElement('div');
        tag.className = 'filter-tag';

        const label = input.closest('.filter-option').querySelector('span').textContent;
        tag.textContent = label;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'filter-tag-remove';
        removeBtn.textContent = '×';
        removeBtn.addEventListener('click', () => {
            input.checked = false;
            this.updateFilterTags();
            this.form.dispatchEvent(new Event('submit'));
        });

        tag.appendChild(removeBtn);
        return tag;
    }

    updateActiveCount(count) {
        if (this.activeCount) {
            this.activeCount.textContent = count;
            if (count > 0) {
                this.activeCount.classList.remove('is-hidden');
            } else {
                this.activeCount.classList.add('is-hidden');
            }
        }
    }

    clearAllFilters() {
        this.filterOptions.forEach(input => {
            input.checked = false;
        });
        this.updateFilterTags();
    }
}

// === SEARCH AUTOCOMPLETE CLASS ===
class SearchAutocomplete {
    constructor(input) {
        this.input = input;
        this.form = input.closest('form');
        this.suggestionsContainer = input.closest('.search-container')?.querySelector('.search-suggestions');

        this.debounceTimeout = null;
        this.debounceDelay = 300;

        if (this.suggestionsContainer) {
            this.init();
        }
    }

    init() {
        this.input.addEventListener('input', () => this.handleInput());
        this.input.addEventListener('focus', () => this.handleInput());

        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.suggestionsContainer.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    handleInput() {
        clearTimeout(this.debounceTimeout);

        const query = this.input.value.trim();

        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        this.debounceTimeout = setTimeout(() => {
            this.fetchSuggestions(query);
        }, this.debounceDelay);
    }

    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/courses/search/?q=${encodeURIComponent(query)}&limit=5`);
            if (!response.ok) throw new Error('Failed to fetch');

            const data = await response.json();
            this.displaySuggestions(data.results || []);
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    displaySuggestions(results) {
        if (results.length === 0) {
            this.hideSuggestions();
            return;
        }

        this.suggestionsContainer.innerHTML = '';

        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-suggestion-item';
            item.innerHTML = `
                <div class="suggestion-title">${this.escapeHtml(result.title)}</div>
                <div class="suggestion-meta">${this.escapeHtml(result.category_name || '')}</div>
            `;

            item.addEventListener('click', () => {
                window.location.href = result.url;
            });

            this.suggestionsContainer.appendChild(item);
        });

        this.showSuggestions();
    }

    showSuggestions() {
        this.suggestionsContainer.classList.remove('is-hidden');
    }

    hideSuggestions() {
        this.suggestionsContainer.classList.add('is-hidden');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// === MASONRY GRID LAYOUT CLASS ===
class MasonryGrid {
    constructor(container) {
        this.container = container;
        this.cards = Array.from(container.querySelectorAll('.product-card'));

        this.init();
    }

    init() {
        this.setPopularityAttributes();
        window.addEventListener('resize', () => this.layout());
        this.layout();
    }

    setPopularityAttributes() {
        const viewCounts = this.cards.map(card => {
            const viewCount = parseInt(card.dataset.viewCount || 0);
            return { card, viewCount };
        });

        viewCounts.sort((a, b) => b.viewCount - a.viewCount);

        const total = viewCounts.length;
        const topThird = Math.ceil(total / 3);
        const middleThird = Math.ceil((total * 2) / 3);

        viewCounts.forEach((item, index) => {
            if (index < topThird) {
                item.card.setAttribute('data-popularity', 'high');
            } else if (index < middleThird) {
                item.card.setAttribute('data-popularity', 'medium');
            } else {
                item.card.setAttribute('data-popularity', 'low');
            }
        });
    }

    layout() {
        // Grid вже налаштований через CSS
        // Цей метод для майбутніх покращень
    }
}

// === MOBILE FILTERS TOGGLE ===
class MobileFiltersToggle {
    constructor() {
        this.toggleBtn = document.querySelector('.mobile-filters-toggle');
        this.sidebar = document.querySelector('.filters-sidebar');
        this.backdrop = this.createBackdrop();

        if (this.toggleBtn && this.sidebar) {
            this.init();
        }
    }

    init() {
        this.toggleBtn.addEventListener('click', () => this.toggle());
        this.backdrop.addEventListener('click', () => this.close());
    }

    createBackdrop() {
        const backdrop = document.createElement('div');
        backdrop.className = 'filters-backdrop';
        document.body.appendChild(backdrop);
        return backdrop;
    }

    toggle() {
        const isOpen = this.sidebar.classList.contains('is-open');
        if (isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.sidebar.classList.add('is-open');
        this.backdrop.classList.add('is-visible');
        document.body.style.overflow = 'hidden';
        this.toggleBtn.setAttribute('aria-expanded', 'true');
    }

    close() {
        this.sidebar.classList.remove('is-open');
        this.backdrop.classList.remove('is-visible');
        document.body.style.overflow = '';
        this.toggleBtn.setAttribute('aria-expanded', 'false');
    }
}

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', () => {
    // Materials Carousel
    const carousel = document.querySelector('.materials-carousel');
    if (carousel) {
        new MaterialsCarousel(carousel);
    }

    // Filters
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        new FiltersManager(filterForm);
    }

    // Search
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        new SearchAutocomplete(searchInput);
    }

    // Masonry Grid
    const productsGrid = document.querySelector('.products-grid');
    if (productsGrid) {
        new MasonryGrid(productsGrid);
    }

    // Mobile Filters
    if (window.innerWidth <= 768) {
        new MobileFiltersToggle();
    }
});

