/**
 * AI HEADER SEARCH
 * Компактний AI чат в header
 * Vanilla JS, ES6+, згідно ~ правил
 */

(function () {
    'use strict';

    let form = null;
    let input = null;
    let submitBtn = null;
    let resultsContainer = null;
    let isProcessing = false;
    let currentAbortController = null;

    /**
     * Ініціалізація компоненту
     */
    function init() {
        form = document.getElementById('ai-header-form');
        input = document.getElementById('ai-header-input');
        submitBtn = form?.querySelector('.ai-search-btn');
        resultsContainer = document.getElementById('ai-search-results');

        if (!form || !input || !submitBtn || !resultsContainer) {
            return;
        }

        bindEvents();
    }

    /**
     * Прив'язка подій
     */
    function bindEvents() {
        form.addEventListener('submit', handleSubmit);
        input.addEventListener('input', handleInput);
        input.addEventListener('focus', handleFocus);

        // Закриття по кліку поза елементом
        document.addEventListener('click', handleClickOutside);

        // Закриття по ESC
        document.addEventListener('keydown', handleEscKey);
    }

    /**
     * Обробка submit форми
     */
    async function handleSubmit(e) {
        e.preventDefault();

        const query = input.value.trim();

        if (!query) {
            return;
        }

        if (query.length > 500) {
            showError('Запит занадто довгий (максимум 500 символів)');
            return;
        }

        if (isProcessing) {
            return;
        }

        await sendQuery(query);
    }

    /**
     * Обробка введення тексту
     */
    function handleInput() {
        const hasValue = input.value.trim().length > 0;
        submitBtn.disabled = !hasValue;
    }

    /**
     * Обробка фокусу на input
     */
    function handleFocus() {
        // Можна показати швидкі підказки або історію
    }

    /**
     * Обробка кліку поза елементом
     */
    function handleClickOutside(e) {
        if (!resultsContainer.contains(e.target) &&
            !form.contains(e.target)) {
            hideResults();
        }
    }

    /**
     * Обробка натискання ESC
     */
    function handleEscKey(e) {
        if (e.key === 'Escape') {
            hideResults();
            input.blur();
        }
    }

    /**
     * Відправка запиту до AI
     */
    async function sendQuery(query) {
        try {
            isProcessing = true;
            submitBtn.disabled = true;

            showLoading();

            // Скасувати попередній запит якщо є
            if (currentAbortController) {
                currentAbortController.abort();
            }

            currentAbortController = new AbortController();

            const response = await fetch('/ai/ask/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ query }),
                credentials: 'same-origin',
                signal: currentAbortController.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                showResult(data);
            } else {
                showError(data.message || 'Помилка отримання відповіді');
            }

        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            showError('Помилка з\'єднання з сервером');
        } finally {
            isProcessing = false;
            submitBtn.disabled = false;
            currentAbortController = null;
        }
    }

    /**
     * Показати loading
     */
    function showLoading() {
        resultsContainer.innerHTML = `
            <div class="ai-search-loading">
                <div class="ai-loading-dots">
                    <div class="ai-loading-dot"></div>
                    <div class="ai-loading-dot"></div>
                    <div class="ai-loading-dot"></div>
                </div>
                <span>AI обробляє запит...</span>
            </div>
        `;
        resultsContainer.classList.add('visible');
    }

    /**
     * Показати результат
     */
    function showResult(data) {
        const responseText = escapeHtml(data.response);
        const formattedResponse = formatMessage(responseText);

        resultsContainer.innerHTML = `
            <div class="ai-result-message">
                <div class="ai-result-header">
                    <div class="ai-result-avatar">🤖</div>
                    <div class="ai-result-title">AI Помічник</div>
                </div>
                <div class="ai-result-content">
                    ${formattedResponse}
                </div>
            </div>
            <div class="ai-result-actions">
                <div class="ai-result-meta">
                    ${data.response_time ? `Відповідь за ${data.response_time}мс` : ''}
                </div>
                <a href="/ai/chat/" class="ai-view-full-chat">
                    Повний чат
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                        <polyline points="12 5 19 12 12 19"></polyline>
                    </svg>
                </a>
            </div>
        `;

        resultsContainer.classList.add('visible');
    }

    /**
     * Показати помилку
     */
    function showError(message) {
        resultsContainer.innerHTML = `
            <div class="ai-search-error">
                <div class="ai-error-icon">❌</div>
                <div class="ai-error-message">${escapeHtml(message)}</div>
            </div>
        `;
        resultsContainer.classList.add('visible');
    }

    /**
     * Сховати результати
     */
    function hideResults() {
        resultsContainer.classList.remove('visible');
    }

    /**
     * Форматування повідомлення (базовий markdown)
     */
    function formatMessage(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    /**
     * Escape HTML для безпеки
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Отримати CSRF токен
     */
    function getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');

        return csrfInput?.value || csrfMeta?.getAttribute('content') || '';
    }

    /**
     * Глобальна ініціалізація
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    /**
     * Експорт для використання в інших модулях
     */
    window.AIHeaderSearch = {
        hideResults
    };

})();

