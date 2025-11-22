class HubFilters {
    constructor() {
        this.selectedFilters = new Set();
        this.searchQuery = '';
        this.scrollPosition = 0;
        this.isMobile = window.innerWidth <= 1024;
        
        // Кешування DOM елементів
        this.sidebar = null;
        this.overlay = null;
        this.toggleBtn = null;
        this.closeBtn = null;
        
        this.init();
    }
    
    init() {
        // Основні обробники
        this.initDropdowns();
        this.initCheckboxes();
        this.initSearch();
        this.initButtons();
        
        // Мобільна панель
        if (this.isMobile) {
            this.initMobilePanel();
        }
        
        // Resize handler з debounce
        this.initResizeHandler();
    }
    
    // === МОБІЛЬНА ПАНЕЛЬ ===
    initMobilePanel() {
        this.sidebar = document.querySelector('.hub-filters-sidebar');
        this.overlay = document.querySelector('.hub-filters-overlay');
        this.toggleBtn = document.getElementById('hub-filters-toggle');
        this.closeBtn = document.getElementById('hub-filters-close');
        
        if (!this.sidebar || !this.overlay || !this.toggleBtn || !this.closeBtn) {
            console.warn('Mobile panel elements not found');
            return;
        }
        
        // Відкриття
        this.toggleBtn.addEventListener('click', () => this.openPanel());
        
        // Закриття
        this.closeBtn.addEventListener('click', () => this.closePanel());
        
        // Overlay з passive listener
        this.overlay.addEventListener('click', () => this.closePanel(), { passive: true });
        
        // Escape key з passive listener
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sidebar.classList.contains('active')) {
                this.closePanel();
            }
        }, { passive: true });
    }
    
    openPanel() {
        if (!this.sidebar || !this.overlay) return;
        
        // Зберегти позицію скролу
        this.scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
        
        // Активувати панель і overlay
        this.sidebar.classList.add('active');
        this.overlay.classList.add('active');
        
        // Перевірка підтримки overscroll-behavior
        if (typeof CSS !== 'undefined' && CSS.supports && CSS.supports('overscroll-behavior', 'none')) {
            document.documentElement.style.overscrollBehavior = 'none';
        }
        
        // Блокувати скрол body (iOS compatible)
        document.body.classList.add('hub-filters-open');
        document.body.style.top = `-${this.scrollPosition}px`;
        
        // ARIA
        if (this.toggleBtn) {
            this.toggleBtn.setAttribute('aria-expanded', 'true');
        }
        this.overlay.setAttribute('aria-hidden', 'false');
        
        // Focus з requestAnimationFrame для smooth
        requestAnimationFrame(() => {
            if (this.closeBtn) {
                this.closeBtn.focus();
            }
        });
    }
    
    closePanel() {
        if (!this.sidebar || !this.overlay) return;
        
        // Деактивувати
        this.sidebar.classList.remove('active');
        this.overlay.classList.remove('active');
        
        // Розблокувати overscroll
        if (typeof CSS !== 'undefined' && CSS.supports && CSS.supports('overscroll-behavior', 'none')) {
            document.documentElement.style.overscrollBehavior = '';
        }
        
        // Розблокувати скрол
        document.body.classList.remove('hub-filters-open');
        document.body.style.top = '';
        
        // Відновити позицію скролу з requestAnimationFrame
        requestAnimationFrame(() => {
            window.scrollTo(0, this.scrollPosition);
        });
        
        // ARIA
        if (this.toggleBtn) {
            this.toggleBtn.setAttribute('aria-expanded', 'false');
        }
        this.overlay.setAttribute('aria-hidden', 'true');
        
        // Focus з requestAnimationFrame
        requestAnimationFrame(() => {
            if (this.toggleBtn) {
                this.toggleBtn.focus();
            }
        });
    }
    
    // === DROPDOWNS (без змін) ===
    initDropdowns() {
        document.querySelectorAll('[data-dropdown]').forEach(header => {
            header.addEventListener('click', (e) => {
                const key = e.currentTarget.dataset.dropdown;
                const submenu = document.querySelector(`[data-submenu="${key}"]`);
                const arrow = e.currentTarget.querySelector('.hub-filter-arrow');
                
                if (submenu && arrow) {
                    submenu.classList.toggle('open');
                    arrow.classList.toggle('open');
                }
            });
        });
    }
    
    // === CHECKBOXES з автозастосуванням ===
    initCheckboxes() {
        // Головні чекбокси
        document.querySelectorAll('[data-checkbox]').forEach(label => {
            const value = label.dataset.checkbox;
            const checkbox = label.querySelector('.hub-filter-checkbox');
            const realCheckbox = label.querySelector('input[type="checkbox"]');
            
            label.addEventListener('click', (e) => {
                if (e.target.tagName === 'INPUT') return;
                e.preventDefault();
                
                if (this.selectedFilters.has(value)) {
                    this.selectedFilters.delete(value);
                    if (checkbox) checkbox.classList.remove('checked');
                    if (realCheckbox) realCheckbox.checked = false;
                } else {
                    this.selectedFilters.add(value);
                    if (checkbox) checkbox.classList.add('checked');
                    if (realCheckbox) realCheckbox.checked = true;
                }
                
                this.handleFilterChange();
            });
        });
        
        // Субпункти (тренерство)
        document.querySelectorAll('.hub-filter-subitem input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedFilters.add(e.target.value);
                } else {
                    this.selectedFilters.delete(e.target.value);
                }
                this.handleFilterChange();
            });
        });
    }
    
    // Обробка зміни фільтрів
    handleFilterChange() {
        if (this.isMobile) {
            // На моб/планшет - автозастосування
            this.applyFilters();
        } else {
            // На десктопі - активувати кнопку "Застосувати"
            this.updateApplyButton();
        }
    }
    
    // === ПОШУК (без змін) ===
    initSearch() {
        const searchInput = document.getElementById('hub-search-field');
        const searchFindBtn = document.getElementById('hub-search-find');
        const searchResetBtn = document.getElementById('hub-search-reset');
        
        if (!searchInput || !searchFindBtn || !searchResetBtn) {
            console.warn('Search elements not found');
            return;
        }
        
        searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value;
        });
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
            }
        });
        
        searchFindBtn.addEventListener('click', () => {
            this.performSearch();
        });
        
        searchResetBtn.addEventListener('click', () => {
            this.resetSearch();
        });
    }
    
    // === КНОПКИ ===
    initButtons() {
        const applyBtn = document.getElementById('apply-filters');
        const cancelBtn = document.getElementById('cancel-filters');
        
        if (!applyBtn || !cancelBtn) {
            console.warn('Filter buttons not found');
            return;
        }
        
        applyBtn.addEventListener('click', () => {
            this.applyFilters();
            if (this.isMobile) {
                this.closePanel();
            }
        });
        
        cancelBtn.addEventListener('click', () => {
            this.resetFilters();
            if (this.isMobile) {
                this.closePanel();
            }
        });
    }
    
    updateApplyButton() {
        const btn = document.getElementById('apply-filters');
        if (!btn) return;
        
        if (this.selectedFilters.size > 0) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    }
    
    // === HTMX INTEGRATION ===
    performSearch() {
        const url = new URL(window.location.href);
        url.searchParams.delete('page');
        
        if (this.searchQuery.trim()) {
            url.searchParams.set('q', this.searchQuery.trim());
            url.searchParams.delete('audience');
            this.selectedFilters.forEach(filter => {
                url.searchParams.append('audience', filter);
            });
            
            if (typeof htmx !== 'undefined') {
                htmx.ajax('GET', url.toString(), {
                    target: '#catalog-content',
                    swap: 'innerHTML'
                });
            }
            
            window.history.pushState({}, '', url.toString());
        }
    }
    
    resetSearch() {
        this.searchQuery = '';
        const searchInput = document.getElementById('hub-search-field');
        if (searchInput) {
            searchInput.value = '';
        }
        
        const url = new URL(window.location.href);
        url.searchParams.delete('q');
        url.searchParams.delete('page');
        
        if (this.selectedFilters.size > 0) {
            url.searchParams.delete('audience');
            this.selectedFilters.forEach(filter => {
                url.searchParams.append('audience', filter);
            });
        }
        
        if (typeof htmx !== 'undefined') {
            htmx.ajax('GET', url.toString(), {
                target: '#catalog-content',
                swap: 'innerHTML'
            });
        }
        
        window.history.pushState({}, '', url.toString());
    }
    
    applyFilters() {
        const url = new URL(window.location.href);
        url.searchParams.delete('audience');
        url.searchParams.delete('page');
        
        this.selectedFilters.forEach(filter => {
            url.searchParams.append('audience', filter);
        });
        
        if (this.searchQuery.trim()) {
            url.searchParams.set('q', this.searchQuery.trim());
        }
        
        if (typeof htmx !== 'undefined') {
            htmx.ajax('GET', url.toString(), {
                target: '#catalog-content',
                swap: 'innerHTML'
            });
        }
        
        window.history.pushState({}, '', url.toString());
    }
    
    resetFilters() {
        this.selectedFilters.clear();
        
        document.querySelectorAll('.hub-filter-checkbox').forEach(cb => {
            cb.classList.remove('checked');
        });
        
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        
        this.updateApplyButton();
        
        const url = new URL(window.location.origin + window.location.pathname);
        
        if (this.searchQuery.trim()) {
            url.searchParams.set('q', this.searchQuery.trim());
        }
        
        if (typeof htmx !== 'undefined') {
            htmx.ajax('GET', url.toString(), {
                target: '#catalog-content',
                swap: 'innerHTML'
            });
        }
        
        window.history.pushState({}, '', url.toString());
    }
    
    // === RESIZE HANDLER з ResizeObserver ===
    initResizeHandler() {
        // Сучасний підхід: ResizeObserver
        if ('ResizeObserver' in window) {
            const resizeObserver = new ResizeObserver(entries => {
                for (const entry of entries) {
                    const width = entry.contentRect.width;
                    const wasMobile = this.isMobile;
                    this.isMobile = width <= 1024;
                    
                    if (wasMobile && !this.isMobile) {
                        if (this.sidebar?.classList.contains('active')) {
                            this.closePanel();
                        }
                    }
                    
                    if (!wasMobile && this.isMobile && !this.sidebar) {
                        this.initMobilePanel();
                    }
                }
            });
            
            resizeObserver.observe(document.body);
        } else {
            // Fallback для старих браузерів
            let resizeTimeout;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {
                    const wasMobile = this.isMobile;
                    this.isMobile = window.innerWidth <= 1024;
                    
                    if (wasMobile && !this.isMobile) {
                        if (this.sidebar && this.sidebar.classList.contains('active')) {
                            this.closePanel();
                        }
                    }
                    
                    if (!wasMobile && this.isMobile && !this.sidebar) {
                        this.initMobilePanel();
                    }
                }, 250);
            });
        }
    }
}

// Ініціалізація
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.hub-filters-sidebar');
    if (sidebar) {
        new HubFilters();
    }
});
