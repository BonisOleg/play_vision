/**
 * Hub Page JavaScript
 * Vanilla JS implementation - БЕЗ Alpine.js
 */

// Subscription Banner
class SubscriptionBanner {
    constructor(element) {
        this.element = element;
        this.closeBtn = element.querySelector('.banner-close');
        this.init();
    }

    init() {
        // Перевіряємо чи вже закривали
        if (localStorage.getItem('banner_closed') === 'true') {
            this.element.classList.add('is-hidden');
            return;
        }

        // Обробник закриття
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.close());
        }
    }

    close() {
        this.element.classList.add('is-hidden');
        localStorage.setItem('banner_closed', 'true');
    }
}

// Materials Carousel
class MaterialsCarousel {
    constructor(element) {
        this.element = element;
        this.currentSlide = 0;
        this.track = element.querySelector('.carousel-content');
        this.prevBtn = element.querySelector('.nav-prev');
        this.nextBtn = element.querySelector('.nav-next');
        this.autoplayInterval = null;
        this.autoplayDelay = 20000; // 20 секунд

        if (!this.track) return;

        this.totalSlides = this.track.children.length;
        this.init();
    }

    init() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => {
                this.prevSlide();
                this.resetAutoplay();
            });
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => {
                this.nextSlide();
                this.resetAutoplay();
            });
        }

        this.updatePosition();

        // Запустити autoplay якщо є більше 1 слайду
        if (this.totalSlides > 1) {
            this.startAutoplay();

            // Зупинити при наведенні миші
            this.element.addEventListener('mouseenter', () => this.stopAutoplay());
            this.element.addEventListener('mouseleave', () => this.startAutoplay());
        }
    }

    updatePosition() {
        if (this.track) {
            this.track.style.transform = `translateX(-${this.currentSlide * 100}%)`;
        }
    }

    nextSlide() {
        this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
        this.updatePosition();
    }

    prevSlide() {
        this.currentSlide = this.currentSlide === 0 ? this.totalSlides - 1 : this.currentSlide - 1;
        this.updatePosition();
    }

    startAutoplay() {
        if (this.totalSlides <= 1) return;
        this.stopAutoplay(); // Очистити попередній інтервал
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

// Filters Manager
class FiltersManager {
    constructor(sidebar) {
        this.sidebar = sidebar;
        this.filtersOpen = false;
        this.form = sidebar.querySelector('form');
        this.mobileToggle = sidebar.querySelector('.mobile-filters-toggle');
        this.clearBtn = sidebar.querySelector('[data-action="clear-filters"]');
        this.filterToggles = sidebar.querySelectorAll('.filter-toggle');

        this.init();
    }

    init() {
        // Mobile toggle
        if (this.mobileToggle) {
            this.mobileToggle.addEventListener('click', () => this.toggleFilters());
        }

        // Clear filters
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => this.clearAllFilters());
        }

        // Expandable filter groups
        this.filterToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                const group = toggle.closest('.filter-group');
                if (group) {
                    group.classList.toggle('expanded');
                }
            });
        });

        // Auto-submit при зміні
        if (this.form) {
            const inputs = this.form.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    // Debounce submit
                    clearTimeout(this.submitTimeout);
                    this.submitTimeout = setTimeout(() => {
                        this.form.submit();
                    }, 300);
                });
            });
        }
    }

    toggleFilters() {
        this.filtersOpen = !this.filtersOpen;
        const content = this.sidebar.querySelector('.filters-content');

        if (content) {
            if (this.filtersOpen) {
                content.classList.remove('is-hidden');
            } else {
                content.classList.add('is-hidden');
            }
        }

        if (this.mobileToggle) {
            this.mobileToggle.setAttribute('aria-expanded', this.filtersOpen);
        }
    }

    clearAllFilters() {
        if (this.form) {
            const inputs = this.form.querySelectorAll('input[type="checkbox"]:checked');
            inputs.forEach(input => input.checked = false);

            const selects = this.form.querySelectorAll('select');
            selects.forEach(select => select.selectedIndex = 0);

            this.form.submit();
        }
    }

    hasActiveFilters() {
        if (!this.form) return false;

        const checkboxes = this.form.querySelectorAll('input[type="checkbox"]:checked');
        const selects = this.form.querySelectorAll('select');
        const activeSelects = Array.from(selects).filter(s => s.value !== '');

        return checkboxes.length > 0 || activeSelects.length > 0;
    }
}

// Support Widget
class SupportWidget {
    constructor(element) {
        this.element = element;
        this.button = element.querySelector('.support-btn');
        this.isOpen = false;
        this.init();
    }

    init() {
        if (this.button) {
            this.button.addEventListener('click', () => this.toggle());
        }
    }

    toggle() {
        this.isOpen = !this.isOpen;
        this.element.classList.toggle('is-open');
    }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Subscription banner
    const banner = document.getElementById('subscription-banner');
    if (banner) {
        new SubscriptionBanner(banner);
    }

    // Materials carousel
    const carousel = document.querySelector('.materials-carousel');
    if (carousel) {
        new MaterialsCarousel(carousel);
    }

    // Filters
    const filtersSidebar = document.querySelector('.filters-sidebar');
    if (filtersSidebar) {
        new FiltersManager(filtersSidebar);
    }

    // Support widget
    const supportWidget = document.querySelector('.support-widget');
    if (supportWidget) {
        new SupportWidget(supportWidget);
    }
});
