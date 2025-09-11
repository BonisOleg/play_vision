/**
 * Search Autocomplete functionality
 * Provides real-time search suggestions and enhanced UX
 */

class SearchAutocomplete {
    constructor(searchInput, suggestionsContainer) {
        this.searchInput = searchInput;
        this.suggestionsContainer = suggestionsContainer;
        this.currentFocus = -1;
        this.suggestions = [];
        this.debounceTimer = null;
        this.minQueryLength = 2;
        this.maxSuggestions = 8;

        this.init();
    }

    init() {
        this.searchInput.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });

        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });

        this.searchInput.addEventListener('focus', () => {
            if (this.searchInput.value.length >= this.minQueryLength) {
                this.showSuggestions();
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.suggestionsContainer.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    handleInput(query) {
        clearTimeout(this.debounceTimer);

        if (query.length < this.minQueryLength) {
            this.hideSuggestions();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300); // 300ms debounce
    }

    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/v1/content/search/suggestions/?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            this.suggestions = data.suggestions || [];
            this.renderSuggestions(query);

        } catch (error) {
            console.error('Error fetching suggestions:', error);
            this.hideSuggestions();
        }
    }

    renderSuggestions(query) {
        if (this.suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        this.suggestionsContainer.innerHTML = '';
        this.currentFocus = -1;

        this.suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.setAttribute('data-index', index);

            // Highlight matching text
            const highlighted = this.highlightMatch(suggestion, query);
            item.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24">
                    <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
                </svg>
                <span>${highlighted}</span>
            `;

            item.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });

            this.suggestionsContainer.appendChild(item);
        });

        this.showSuggestions();
    }

    highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    handleKeydown(e) {
        const items = this.suggestionsContainer.querySelectorAll('.suggestion-item');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.currentFocus = Math.min(this.currentFocus + 1, items.length - 1);
            this.updateActiveSuggestion(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.currentFocus = Math.max(this.currentFocus - 1, -1);
            this.updateActiveSuggestion(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (this.currentFocus >= 0 && items[this.currentFocus]) {
                const suggestion = this.suggestions[this.currentFocus];
                this.selectSuggestion(suggestion);
            } else {
                // Submit search form
                this.submitSearch();
            }
        } else if (e.key === 'Escape') {
            this.hideSuggestions();
            this.searchInput.blur();
        }
    }

    updateActiveSuggestion(items) {
        items.forEach((item, index) => {
            item.classList.toggle('active', index === this.currentFocus);
        });
    }

    selectSuggestion(suggestion) {
        this.searchInput.value = suggestion;
        this.hideSuggestions();
        this.submitSearch();
    }

    submitSearch() {
        const form = this.searchInput.closest('form');
        if (form) {
            form.submit();
        }
    }

    showSuggestions() {
        this.suggestionsContainer.style.display = 'block';
        this.suggestionsContainer.setAttribute('aria-hidden', 'false');
    }

    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
        this.suggestionsContainer.setAttribute('aria-hidden', 'true');
        this.currentFocus = -1;
    }
}

// Popular searches functionality
class PopularSearches {
    constructor(container) {
        this.container = container;
        this.searches = [
            'техніка ведення м\'яча',
            'тактика футболу',
            'фізична підготовка',
            'воротарська техніка',
            'швидкість та спритність',
            'психологія спорту',
            'дитячий футбол',
            'професійний футбол',
        ];

        this.render();
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = '';

        const title = document.createElement('h4');
        title.textContent = 'Популярні пошуки:';
        title.className = 'popular-searches-title';
        this.container.appendChild(title);

        const list = document.createElement('div');
        list.className = 'popular-searches-list';

        this.searches.slice(0, 6).forEach(search => {
            const item = document.createElement('button');
            item.className = 'popular-search-item';
            item.textContent = search;
            item.type = 'button';

            item.addEventListener('click', () => {
                this.selectPopularSearch(search);
            });

            list.appendChild(item);
        });

        this.container.appendChild(list);
    }

    selectPopularSearch(search) {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.value = search;

            const form = searchInput.closest('form');
            if (form) {
                form.submit();
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Main search autocomplete
    const searchInput = document.querySelector('.search-input');
    const suggestionsContainer = document.querySelector('.search-suggestions');

    if (searchInput && suggestionsContainer) {
        new SearchAutocomplete(searchInput, suggestionsContainer);
    }

    // Popular searches in search results page
    const popularSearchesContainer = document.querySelector('.popular-searches');
    if (popularSearchesContainer) {
        new PopularSearches(popularSearchesContainer);
    }
});

// Export for use in other modules
window.SearchAutocomplete = SearchAutocomplete;
window.PopularSearches = PopularSearches;
