class HubFilters {
    constructor() {
        this.selectedFilters = new Set();
        this.searchQuery = '';
        this.init();
    }
    
    init() {
        this.initDropdowns();
        this.initCheckboxes();
        this.initSearch();
        this.initButtons();
    }
    
    initDropdowns() {
        document.querySelectorAll('[data-dropdown]').forEach(header => {
            header.addEventListener('click', (e) => {
                const key = e.currentTarget.dataset.dropdown;
                const submenu = document.querySelector(`[data-submenu="${key}"]`);
                const arrow = e.currentTarget.querySelector('.hub-filter-arrow');
                
                submenu.classList.toggle('open');
                arrow.classList.toggle('open');
            });
        });
    }
    
    initCheckboxes() {
        document.querySelectorAll('[data-checkbox]').forEach(label => {
            const value = label.dataset.checkbox;
            const checkbox = label.querySelector('.hub-filter-checkbox');
            const realCheckbox = label.querySelector('input[type="checkbox"]');
            
            label.addEventListener('click', (e) => {
                if (e.target.tagName === 'INPUT') return;
                
                e.preventDefault();
                
                if (this.selectedFilters.has(value)) {
                    this.selectedFilters.delete(value);
                    checkbox.classList.remove('checked');
                    realCheckbox.checked = false;
                } else {
                    this.selectedFilters.add(value);
                    checkbox.classList.add('checked');
                    realCheckbox.checked = true;
                }
                this.updateApplyButton();
            });
        });
        
        document.querySelectorAll('.hub-filter-subitem input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedFilters.add(e.target.value);
                } else {
                    this.selectedFilters.delete(e.target.value);
                }
                this.updateApplyButton();
            });
        });
    }
    
    initSearch() {
        const searchInput = document.getElementById('hub-search-field');
        const searchFindBtn = document.getElementById('hub-search-find');
        const searchResetBtn = document.getElementById('hub-search-reset');
        
        // Оновлюємо значення при введенні
        searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value;
        });
        
        // Пошук по Enter
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
            }
        });
        
        // Кнопка "Знайти"
        searchFindBtn.addEventListener('click', () => {
            this.performSearch();
        });
        
        // Кнопка "Скинути"
        searchResetBtn.addEventListener('click', () => {
            this.resetSearch();
        });
    }
    
    initButtons() {
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.applyFilters();
        });
        
        document.getElementById('cancel-filters').addEventListener('click', () => {
            this.resetFilters();
        });
    }
    
    updateApplyButton() {
        const btn = document.getElementById('apply-filters');
        // Активуємо тільки при наявності фільтрів, НЕ пошуку
        if (this.selectedFilters.size > 0) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    }
    
    performSearch() {
        const url = new URL(window.location.href);
        url.searchParams.delete('page');
        
        if (this.searchQuery.trim()) {
            url.searchParams.set('q', this.searchQuery.trim());
            
            // Застосовуємо також активні фільтри
            url.searchParams.delete('audience');
            this.selectedFilters.forEach(filter => {
                url.searchParams.append('audience', filter);
            });
            
            htmx.ajax('GET', url.toString(), {
                target: '#catalog-content',
                swap: 'innerHTML'
            });
            
            window.history.pushState({}, '', url.toString());
        }
    }
    
    resetSearch() {
        this.searchQuery = '';
        document.getElementById('hub-search-field').value = '';
        
        const url = new URL(window.location.href);
        url.searchParams.delete('q');
        url.searchParams.delete('page');
        
        // Зберігаємо фільтри, якщо є
        if (this.selectedFilters.size > 0) {
            url.searchParams.delete('audience');
            this.selectedFilters.forEach(filter => {
                url.searchParams.append('audience', filter);
            });
        }
        
        htmx.ajax('GET', url.toString(), {
            target: '#catalog-content',
            swap: 'innerHTML'
        });
        
        window.history.pushState({}, '', url.toString());
    }
    
    applyFilters() {
        const url = new URL(window.location.href);
        url.searchParams.delete('audience');
        url.searchParams.delete('page');
        
        this.selectedFilters.forEach(filter => {
            url.searchParams.append('audience', filter);
        });
        
        // Зберігаємо пошуковий запит, якщо є
        if (this.searchQuery.trim()) {
            url.searchParams.set('q', this.searchQuery.trim());
        }
        
        htmx.ajax('GET', url.toString(), {
            target: '#catalog-content',
            swap: 'innerHTML'
        });
        
        window.history.pushState({}, '', url.toString());
    }
    
    resetFilters() {
        this.selectedFilters.clear();
        this.searchQuery = '';
        
        document.querySelectorAll('.hub-filter-checkbox').forEach(cb => {
            cb.classList.remove('checked');
        });
        
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        
        document.getElementById('hub-search-input').value = '';
        
        this.updateApplyButton();
        
        const url = new URL(window.location.origin + window.location.pathname);
        htmx.ajax('GET', url.toString(), {
            target: '#catalog-content',
            swap: 'innerHTML'
        });
        
        window.history.pushState({}, '', url.toString());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.hub-filters-sidebar');
    if (sidebar) {
        new HubFilters();
    }
});

