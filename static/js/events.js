/**
 * Events Page JavaScript
 * Vanilla JS implementation - замість Alpine.js
 */

class EventCalendar {
    constructor(element) {
        this.element = element;
        this.selectedType = 'all';
        this.selectedFormat = 'all';
        this.currentDate = new Date();
        this.visibleDays = [];

        this.typeSelect = element.querySelector('select[name="event_type"]');
        this.formatSelect = element.querySelector('select[name="event_format"]');
        this.resetBtn = element.querySelector('[data-action="reset-filters"]');
        this.prevBtn = element.querySelector('[data-action="prev-week"]');
        this.nextBtn = element.querySelector('[data-action="next-week"]');
        this.todayBtn = element.querySelector('[data-action="go-today"]');
        this.periodText = element.querySelector('.current-period');

        this.init();
    }

    init() {
        // Event listeners
        if (this.typeSelect) {
            this.typeSelect.addEventListener('change', () => this.filterEvents());
        }

        if (this.formatSelect) {
            this.formatSelect.addEventListener('change', () => this.filterEvents());
        }

        if (this.resetBtn) {
            this.resetBtn.addEventListener('click', () => this.resetFilters());
        }

        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.previousWeek());
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextWeek());
        }

        if (this.todayBtn) {
            this.todayBtn.addEventListener('click', () => this.goToToday());
        }

        this.updatePeriodText();
        this.updateResetButtonVisibility();
    }

    filterEvents() {
        this.selectedType = this.typeSelect?.value || 'all';
        this.selectedFormat = this.formatSelect?.value || 'all';

        // Тут можна додати AJAX запит для фільтрації
        // Або перезавантажити сторінку з параметрами
        const url = new URL(window.location);
        if (this.selectedType !== 'all') {
            url.searchParams.set('type', this.selectedType);
        } else {
            url.searchParams.delete('type');
        }

        if (this.selectedFormat !== 'all') {
            url.searchParams.set('format', this.selectedFormat);
        } else {
            url.searchParams.delete('format');
        }

        window.location.href = url.toString();
    }

    resetFilters() {
        if (this.typeSelect) this.typeSelect.value = 'all';
        if (this.formatSelect) this.formatSelect.value = 'all';

        // Очищаємо URL параметри
        window.location.href = window.location.pathname;
    }

    previousWeek() {
        this.currentDate.setDate(this.currentDate.getDate() - 7);
        this.updatePeriodText();
    }

    nextWeek() {
        this.currentDate.setDate(this.currentDate.getDate() + 7);
        this.updatePeriodText();
    }

    goToToday() {
        this.currentDate = new Date();
        this.updatePeriodText();
    }

    updatePeriodText() {
        if (this.periodText) {
            const options = { month: 'long', year: 'numeric' };
            this.periodText.textContent = this.currentDate.toLocaleDateString('uk-UA', options);
        }
    }

    updateResetButtonVisibility() {
        if (this.resetBtn) {
            const hasFilters = this.selectedType !== 'all' || this.selectedFormat !== 'all';
            if (hasFilters) {
                this.resetBtn.classList.remove('is-hidden');
            } else {
                this.resetBtn.classList.add('is-hidden');
            }
        }
    }
}

// Ініціалізація
document.addEventListener('DOMContentLoaded', () => {
    const calendar = document.querySelector('.event-calendar');
    if (calendar) {
        new EventCalendar(calendar);
    }
});
