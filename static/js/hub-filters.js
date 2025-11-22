class HubFilters {
    constructor() {
        this.selectedFilters = new Set();
        this.searchQuery = '';
        this.isMobile = window.innerWidth <= 1024;
        
        // Кешування DOM елементів
        this.sidebar = null;
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
        if (!this.isMobile) return;
        
        this.sidebar = document.querySelector('.hub-filters-sidebar');
        this.toggleBtn = document.getElementById('hub-filters-toggle');
        this.closeBtn = document.getElementById('hub-filters-close');
        
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', () => {
                this.sidebar?.classList.add('active');
            });
        }
        
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => {
                this.sidebar?.classList.remove('active');
            });
        }
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sidebar?.classList.contains('active')) {
                this.sidebar.classList.remove('active');
            }
        }, { passive: true });
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
        // Фільтри застосовуються тільки через кнопку "Шукати"
        // Нічого не робимо автоматично
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
        
        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                this.applyFilters();
                if (this.isMobile) {
                    this.sidebar?.classList.remove('active');
                }
            });
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.resetFilters();
                if (this.isMobile) {
                    this.sidebar?.classList.remove('active');
                }
            });
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
    
    // === RESIZE HANDLER з debounce ===
    initResizeHandler() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                const wasMobile = this.isMobile;
                this.isMobile = window.innerWidth <= 1024;
                
                if (wasMobile && !this.isMobile) {
                    this.sidebar?.classList.remove('active');
                }
            }, 250);
        });
    }
}

// Ініціалізація
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.hub-filters-sidebar');
    if (sidebar) {
        new HubFilters();
    }
});
