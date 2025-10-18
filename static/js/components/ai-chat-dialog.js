/**
 * AI Chat Dialog Component
 * Керування розгортуванням та роботою AI чату в header
 * БЕЗ globals, БЕЗ eval, зовнішній модульний JS
 */

(function () {
    'use strict';

    // Константи
    const CLASS_DIALOG_OPEN = 'dialog-open';
    const STORAGE_KEY = 'ai-chat-history';
    const API_URL = '/ai/ask/';
    const MAX_HISTORY_MESSAGES = 20;

    // Елементи DOM
    let toggleBtn = null;
    let dialog = null;
    let overlay = null;
    let closeButtons = null;
    let messagesContainer = null;
    let form = null;
    let input = null;
    let sendBtn = null;
    let charCounter = null;

    /**
     * Ініціалізація компонента
     */
    function init() {
        // Отримати елементи DOM
        toggleBtn = document.querySelector('[data-ai-chat-toggle]');
        dialog = document.querySelector('[data-ai-chat-dialog]');
        overlay = document.querySelector('[data-ai-dialog-overlay]');
        closeButtons = document.querySelectorAll('[data-ai-dialog-close]');
        messagesContainer = document.querySelector('[data-ai-dialog-messages]');
        form = document.querySelector('[data-ai-dialog-form]');
        input = document.querySelector('[data-ai-dialog-input]');
        sendBtn = document.querySelector('[data-ai-dialog-send]');
        charCounter = document.querySelector('[data-ai-char-counter]');

        if (!toggleBtn || !dialog) {
            return;
        }

        // Встановити event listeners
        toggleBtn.addEventListener('click', toggleDialog);
        
        closeButtons.forEach(function (btn) {
            btn.addEventListener('click', closeDialog);
        });

        if (overlay) {
            overlay.addEventListener('click', closeDialog);
        }

        if (form) {
            form.addEventListener('submit', handleSubmit);
        }

        if (input) {
            input.addEventListener('input', handleInputChange);
            input.addEventListener('keydown', handleKeyDown);
        }

        // Закрити на Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && dialog.classList.contains(CLASS_DIALOG_OPEN)) {
                closeDialog();
            }
        });

        // Завантажити історію чату
        loadChatHistory();
    }

    /**
     * Toggle dialog відкрито/закрито
     */
    function toggleDialog() {
        if (dialog.classList.contains(CLASS_DIALOG_OPEN)) {
            closeDialog();
        } else {
            openDialog();
        }
    }

    /**
     * Відкрити dialog
     */
    function openDialog() {
        dialog.classList.add(CLASS_DIALOG_OPEN);
        dialog.setAttribute('aria-hidden', 'false');
        
        // Focus на input
        if (input) {
            setTimeout(function () {
                input.focus();
            }, 100);
        }

        // Scroll до низу повідомлень
        scrollToBottom();
    }

    /**
     * Закрити dialog
     */
    function closeDialog() {
        dialog.classList.remove(CLASS_DIALOG_OPEN);
        dialog.setAttribute('aria-hidden', 'true');
        
        // Focus назад на toggle button
        if (toggleBtn) {
            toggleBtn.focus();
        }
    }

    /**
     * Обробка submit форми
     */
    function handleSubmit(e) {
        e.preventDefault();

        if (!input) {
            return;
        }

        const query = input.value.trim();

        if (!query) {
            return;
        }

        if (query.length > 500) {
            showError('Запит занадто довгий (максимум 500 символів)');
            return;
        }

        // Відобразити повідомлення користувача
        displayMessage(query, 'user');

        // Очистити input
        input.value = '';
        updateCharCounter();
        autoResizeTextarea();

        // Показати індикатор завантаження
        showLoading();

        // Відправити запит до API
        sendQuery(query);
    }

    /**
     * Відправити запит до AI API
     */
    function sendQuery(query) {
        const csrfToken = getCSRFToken();

        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ query: query })
        })
        .then(function (response) {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(function (data) {
            hideLoading();

            if (data.success && data.response) {
                displayMessage(data.response, 'bot');
                saveChatHistory();
            } else {
                showError(data.message || 'Помилка отримання відповіді');
            }
        })
        .catch(function (error) {
            hideLoading();
            console.error('AI Chat Error:', error);
            showError('Не вдалося отримати відповідь. Спробуйте пізніше.');
        });
    }

    /**
     * Відобразити повідомлення в чаті
     */
    function displayMessage(text, type) {
        if (!messagesContainer) {
            return;
        }

        const messageEl = document.createElement('div');
        messageEl.className = 'ai-message ai-message--' + type;

        const avatarEl = document.createElement('div');
        avatarEl.className = 'ai-message-avatar';
        avatarEl.textContent = type === 'bot' ? '🤖' : '👤';

        const contentEl = document.createElement('div');
        contentEl.className = 'ai-message-content';
        
        const p = document.createElement('p');
        p.textContent = text;
        contentEl.appendChild(p);

        messageEl.appendChild(avatarEl);
        messageEl.appendChild(contentEl);

        messagesContainer.appendChild(messageEl);

        scrollToBottom();
    }

    /**
     * Показати індикатор завантаження
     */
    function showLoading() {
        if (!messagesContainer) {
            return;
        }

        const loadingEl = document.createElement('div');
        loadingEl.className = 'ai-message ai-message--bot';
        loadingEl.setAttribute('data-loading', 'true');

        const avatarEl = document.createElement('div');
        avatarEl.className = 'ai-message-avatar';
        avatarEl.textContent = '🤖';

        const contentEl = document.createElement('div');
        contentEl.className = 'ai-message-content';
        
        const loadingDots = document.createElement('div');
        loadingDots.className = 'ai-message-loading';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            dot.className = 'ai-loading-dot';
            loadingDots.appendChild(dot);
        }
        contentEl.appendChild(loadingDots);

        loadingEl.appendChild(avatarEl);
        loadingEl.appendChild(contentEl);

        messagesContainer.appendChild(loadingEl);
        scrollToBottom();

        // Disable send button
        if (sendBtn) {
            sendBtn.disabled = true;
        }
    }

    /**
     * Приховати індикатор завантаження
     */
    function hideLoading() {
        if (!messagesContainer) {
            return;
        }

        const loadingEl = messagesContainer.querySelector('[data-loading="true"]');
        if (loadingEl) {
            loadingEl.remove();
        }

        // Enable send button
        if (sendBtn) {
            sendBtn.disabled = false;
        }
    }

    /**
     * Показати помилку
     */
    function showError(message) {
        if (!messagesContainer) {
            return;
        }

        const errorEl = document.createElement('div');
        errorEl.className = 'ai-message-error';
        errorEl.textContent = '⚠️ ' + message;

        messagesContainer.appendChild(errorEl);
        scrollToBottom();
    }

    /**
     * Scroll до низу повідомлень
     */
    function scrollToBottom() {
        if (!messagesContainer) {
            return;
        }

        setTimeout(function () {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 50);
    }

    /**
     * Обробка зміни input
     */
    function handleInputChange() {
        updateCharCounter();
        autoResizeTextarea();
    }

    /**
     * Оновити лічильник символів
     */
    function updateCharCounter() {
        if (!input || !charCounter) {
            return;
        }

        const length = input.value.length;
        charCounter.textContent = length;
    }

    /**
     * Автоматична зміна розміру textarea
     */
    function autoResizeTextarea() {
        if (!input) {
            return;
        }

        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    }

    /**
     * Обробка натискання клавіш
     */
    function handleKeyDown(e) {
        // Enter без Shift - відправити
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (form) {
                form.dispatchEvent(new Event('submit', { cancelable: true }));
            }
        }
    }

    /**
     * Отримати CSRF токен
     */
    function getCSRFToken() {
        const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }

        // Fallback - з cookie
        const cookieValue = document.cookie
            .split('; ')
            .find(function (row) { return row.startsWith('csrftoken='); });
        
        return cookieValue ? cookieValue.split('=')[1] : '';
    }

    /**
     * Завантажити історію чату з sessionStorage
     */
    function loadChatHistory() {
        try {
            const history = sessionStorage.getItem(STORAGE_KEY);
            if (!history) {
                return;
            }

            const messages = JSON.parse(history);
            if (!Array.isArray(messages)) {
                return;
            }

            // Відобразити збережені повідомлення (крім привітального)
            messages.forEach(function (msg) {
                if (msg.text && msg.type) {
                    displayMessage(msg.text, msg.type);
                }
            });
        } catch (e) {
            console.warn('Failed to load chat history:', e);
        }
    }

    /**
     * Зберегти історію чату в sessionStorage
     */
    function saveChatHistory() {
        if (!messagesContainer) {
            return;
        }

        try {
            const messages = [];
            const messageElements = messagesContainer.querySelectorAll('.ai-message:not([data-loading])');

            // Пропустити перше привітальне повідомлення
            for (let i = 1; i < messageElements.length && i <= MAX_HISTORY_MESSAGES; i++) {
                const msgEl = messageElements[i];
                const isUser = msgEl.classList.contains('ai-message--user');
                const contentEl = msgEl.querySelector('.ai-message-content p');
                
                if (contentEl) {
                    messages.push({
                        text: contentEl.textContent,
                        type: isUser ? 'user' : 'bot'
                    });
                }
            }

            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
        } catch (e) {
            console.warn('Failed to save chat history:', e);
        }
    }

    // Ініціалізація при завантаженні DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

