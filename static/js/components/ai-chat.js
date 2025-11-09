/**
 * AI CHAT FUNCTIONALITY
 * Повний функціонал AI помічника для Play Vision
 */

class AIChat {
    constructor(container = document) {
        this.container = container;
        this.messagesContainer = container.querySelector('#ai-messages') || container.querySelector('.ai-widget-messages');
        this.form = container.querySelector('#ai-form') || container.querySelector('[data-widget-form]');
        this.input = container.querySelector('#ai-input') || container.querySelector('[data-widget-input]');
        this.sendBtn = container.querySelector('#ai-send') || container.querySelector('[data-widget-send]');
        this.charCounter = container.querySelector('#char-counter');

        this.init();
    }

    init() {
        if (!this.form || !this.input) return;

        // Event listeners
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.input.addEventListener('input', this.handleInput.bind(this));
        this.input.addEventListener('keydown', this.handleKeyDown.bind(this));

        // Suggested questions
        this.container.addEventListener('click', this.handleSuggestionClick.bind(this));

        // Recent queries
        this.container.addEventListener('click', this.handleRecentQueryClick.bind(this));

        // Auto-resize textarea
        this.setupAutoResize();
    }

    handleSubmit(e) {
        e.preventDefault();

        const query = this.input.value.trim();
        if (!query) return;

        if (query.length > 500) {
            this.showError('Запит занадто довгий (максимум 500 символів)');
            return;
        }

        this.sendMessage(query);
    }

    handleInput(e) {
        if (this.charCounter) {
            this.charCounter.textContent = e.target.value.length;
        }

        // Enable/disable send button
        if (this.sendBtn) {
            this.sendBtn.disabled = !e.target.value.trim();
        }
    }

    handleKeyDown(e) {
        // Send on Ctrl+Enter or Cmd+Enter
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            this.form.dispatchEvent(new Event('submit'));
        }
    }

    handleSuggestionClick(e) {
        const suggestionBtn = e.target.closest('.ai-suggestion-btn, .ai-widget-suggestion');
        if (suggestionBtn) {
            const question = suggestionBtn.dataset.question || suggestionBtn.dataset.suggestion;
            if (question) {
                this.input.value = question;
                this.sendMessage(question);
            }
        }
    }

    handleRecentQueryClick(e) {
        const recentBtn = e.target.closest('.ai-recent-query');
        if (recentBtn) {
            const query = recentBtn.dataset.query;
            if (query) {
                this.input.value = query;
                this.input.focus();
            }
        }
    }

    async sendMessage(query) {
        try {
            // Show user message
            this.addMessage(query, 'user');

            // Clear input and show loading
            this.input.value = '';
            if (this.charCounter) this.charCounter.textContent = '0';
            this.showTypingIndicator();
            this.setLoading(true);

            // Send request to AI API
            const response = await this.apiRequest('/ai/ask/', {
                method: 'POST',
                body: JSON.stringify({ query })
            });

            // Hide typing indicator
            this.hideTypingIndicator();

            if (response.success) {
                // Show AI response
                this.addMessage(response.response, 'bot', {
                    queryId: response.query_id,
                    sources: response.sources,
                    responseTime: response.response_time
                });
            } else {
                this.showError(response.message || 'Помилка отримання відповіді');
            }

        } catch (error) {
            this.hideTypingIndicator();
            this.showError('Помилка з\'єднання з сервером');
        } finally {
            this.setLoading(false);
        }
    }

    addMessage(content, sender, metadata = {}) {
        const messageEl = document.createElement('div');
        messageEl.className = `ai-message ai-message--${sender}`;

        const avatarEl = document.createElement('div');
        avatarEl.className = 'ai-message-avatar';
        avatarEl.textContent = sender === 'bot' ? '🤖' : '👤';

        const contentEl = document.createElement('div');
        contentEl.className = 'ai-message-content';
        contentEl.innerHTML = this.formatMessage(content);

        messageEl.appendChild(avatarEl);
        messageEl.appendChild(contentEl);

        // Add metadata and rating for bot messages
        if (sender === 'bot' && metadata.queryId) {
            const metaEl = this.createMessageMeta(metadata);
            contentEl.appendChild(metaEl);
        }

        this.messagesContainer.appendChild(messageEl);
        this.scrollToBottom();
    }

    createMessageMeta(metadata) {
        const metaEl = document.createElement('div');
        metaEl.className = 'ai-message-meta';

        const infoEl = document.createElement('div');
        if (metadata.responseTime) {
            infoEl.innerHTML = `<small>Відповідь за ${metadata.responseTime}мс</small>`;
        }

        const actionsEl = document.createElement('div');
        actionsEl.className = 'ai-message-actions';
        actionsEl.innerHTML = `
            <button class="ai-rate-btn positive" data-action="rate" data-query-id="${metadata.queryId}" data-rating="5" title="Корисна відповідь">
                👍
            </button>
            <button class="ai-rate-btn negative" data-action="rate" data-query-id="${metadata.queryId}" data-rating="1" title="Некорисна відповідь">
                👎
            </button>
        `;

        // Add event listeners for rating
        actionsEl.addEventListener('click', this.handleRating.bind(this));

        metaEl.appendChild(infoEl);
        metaEl.appendChild(actionsEl);

        return metaEl;
    }

    async handleRating(e) {
        const rateBtn = e.target.closest('.ai-rate-btn');
        if (!rateBtn) return;

        const queryId = rateBtn.dataset.queryId;
        const rating = parseInt(rateBtn.dataset.rating);

        try {
            const response = await this.apiRequest(`/ai/rate/${queryId}/`, {
                method: 'POST',
                body: JSON.stringify({ rating })
            });

            if (response.success) {
                // Visual feedback
                rateBtn.classList.add('active');
                rateBtn.style.opacity = '1';

                // Disable other rating buttons
                const allRateBtns = rateBtn.parentElement.querySelectorAll('.ai-rate-btn');
                allRateBtns.forEach(btn => {
                    if (btn !== rateBtn) {
                        btn.disabled = true;
                        btn.style.opacity = '0.3';
                    }
                });

                this.showSuccessToast(response.message);
            }
        } catch (error) {
            this.showError('Помилка відправки оцінки');
        }
    }

    formatMessage(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'ai-typing-indicator';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <div class="ai-message-avatar">🤖</div>
            <div class="ai-message-content">
                <span>AI друкує</span>
                <div class="ai-typing-dots">
                    <span class="ai-typing-dot"></span>
                    <span class="ai-typing-dot"></span>
                    <span class="ai-typing-dot"></span>
                </div>
            </div>
        `;

        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = this.messagesContainer.querySelector('#typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    setLoading(loading) {
        if (this.sendBtn) {
            this.sendBtn.disabled = loading;
        }
        if (this.input) {
            this.input.disabled = loading;
        }
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    setupAutoResize() {
        if (!this.input || this.input.tagName !== 'TEXTAREA') return;

        this.input.addEventListener('input', () => {
            this.input.style.height = 'auto';
            this.input.style.height = Math.min(this.input.scrollHeight, 118) + 'px';
        });
    }

    showError(message) {
        this.addMessage(`❌ ${message}`, 'bot');
    }

    showSuccessToast(message) {
        const toast = document.createElement('div');
        toast.className = 'ai-success-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--color-success);
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            z-index: 1100;
            font-size: 14px;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    async apiRequest(endpoint, options = {}) {
        const url = endpoint.startsWith('/') ? endpoint : `/ai/${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            credentials: 'same-origin',
        };

        const requestOptions = { ...defaultOptions, ...options };

        const response = await fetch(url, requestOptions);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
}


/**
 * AI WIDGET CONTROLLER
 * Контролер для AI віджетів на сторінках
 */
class AIWidget {
    constructor(element) {
        this.element = element;
        this.widgetType = element.dataset.widgetId;
        this.isMinimized = false;
        this.chat = new AIChat(element);

        this.init();
    }

    init() {
        // Toggle functionality
        const toggle = this.element.querySelector('[data-widget-toggle]');
        if (toggle) {
            toggle.addEventListener('click', this.toggle.bind(this));
        }

        // Header click to toggle
        const header = this.element.querySelector('.ai-widget-header');
        if (header) {
            header.addEventListener('click', this.toggle.bind(this));
        }

        // Load widget state from localStorage
        this.loadState();
    }

    toggle() {
        this.isMinimized = !this.isMinimized;
        this.element.classList.toggle('minimized', this.isMinimized);

        // Update toggle icon
        const toggleIcon = this.element.querySelector('[data-widget-toggle] svg');
        if (toggleIcon) {
            toggleIcon.style.transform = this.isMinimized ? 'rotate(180deg)' : 'rotate(0deg)';
        }

        // Save state
        this.saveState();
    }

    saveState() {
        localStorage.setItem(`aiWidget_${this.widgetType}_minimized`, this.isMinimized);
    }

    loadState() {
        const saved = localStorage.getItem(`aiWidget_${this.widgetType}_minimized`);
        if (saved === 'true') {
            this.isMinimized = true;
            this.element.classList.add('minimized');
        }
    }
}


/**
 * AI UTILS
 * Утилітарні функції для AI
 */
class AIUtils {
    static formatTime(milliseconds) {
        if (milliseconds < 1000) {
            return `${milliseconds}мс`;
        }
        return `${(milliseconds / 1000).toFixed(1)}с`;
    }

    static truncateText(text, maxLength = 100) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}


// GLOBAL INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main chat page
    const chatContainer = document.querySelector('.ai-chat-container');
    if (chatContainer) {
        window.aiChat = new AIChat(chatContainer);
        console.log('AI Chat initialized');
    }

    // Initialize AI widgets
    const widgets = document.querySelectorAll('[data-ai-widget]');
    widgets.forEach(widget => {
        new AIWidget(widget);
    });

    console.log(`Initialized ${widgets.length} AI widgets`);
});

// Export for use in other modules
window.AIChat = AIChat;
window.AIWidget = AIWidget;
window.AIUtils = AIUtils;
