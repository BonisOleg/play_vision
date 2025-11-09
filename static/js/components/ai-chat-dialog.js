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
    let dialogContainer = null;
    let dialogHeader = null;
    let overlay = null;
    let closeButtons = null;
    let messagesContainer = null;
    let form = null;
    let input = null;
    let sendBtn = null;
    let charCounter = null;

    // Drag & Drop state
    let isDragging = false;
    let currentX = 0;
    let currentY = 0;
    let initialX = 0;
    let initialY = 0;
    let xOffset = 0;
    let yOffset = 0;

    /**
     * Ініціалізація компонента
     */
    function init() {
        // Отримати елементи DOM
        toggleBtn = document.querySelector('[data-ai-chat-toggle]');
        dialog = document.querySelector('[data-ai-chat-dialog]');
        dialogContainer = document.querySelector('.ai-dialog-container');
        dialogHeader = document.querySelector('.ai-dialog-header');
        overlay = document.querySelector('[data-ai-dialog-overlay]');
        closeButtons = document.querySelectorAll('[data-ai-dialog-close]');
        messagesContainer = document.querySelector('[data-ai-dialog-messages]');
        form = document.querySelector('[data-ai-dialog-form]');
        input = document.querySelector('[data-ai-dialog-input]');
        sendBtn = document.querySelector('[data-ai-dialog-send]');
        charCounter = document.querySelector('[data-ai-char-counter]');

        if (!toggleBtn || !dialog || !dialogContainer) {
            return;
        }

        // Встановити event listeners
        toggleBtn.addEventListener('click', toggleDialog);
        
        closeButtons.forEach(function (btn) {
            btn.addEventListener('click', closeDialog);
        });

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

        // Drag & Drop functionality
        initDragAndDrop();

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
        // Скинути позицію перед відкриттям
        resetPosition();
        
        dialog.classList.add(CLASS_DIALOG_OPEN);
        dialog.setAttribute('aria-hidden', 'false');
        
        // Focus на input
        if (input) {
            setTimeout(function () {
                input.focus();
            }, 300);
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
        input.style.height = Math.min(input.scrollHeight, 118) + 'px';
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
     * Ініціалізація Drag & Drop
     */
    function initDragAndDrop() {
        if (!dialogHeader || !dialogContainer) {
            return;
        }

        // Mouse events
        dialogHeader.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        // Touch events для мобільних
        dialogHeader.addEventListener('touchstart', dragStart, { passive: false });
        document.addEventListener('touchmove', drag, { passive: false });
        document.addEventListener('touchend', dragEnd);
    }

    /**
     * Початок перетягування
     */
    function dragStart(e) {
        if (e.type === 'touchstart') {
            initialX = e.touches[0].clientX - xOffset;
            initialY = e.touches[0].clientY - yOffset;
        } else {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
        }

        // Не починати drag якщо клікнули на кнопку закриття
        if (e.target.closest('[data-ai-dialog-close]')) {
            return;
        }

        isDragging = true;
    }

    /**
     * Процес перетягування
     */
    function drag(e) {
        if (!isDragging) {
            return;
        }

        e.preventDefault();

        if (e.type === 'touchmove') {
            currentX = e.touches[0].clientX - initialX;
            currentY = e.touches[0].clientY - initialY;
        } else {
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
        }

        xOffset = currentX;
        yOffset = currentY;

        setTranslate(currentX, currentY);
    }

    /**
     * Кінець перетягування
     */
    function dragEnd(e) {
        if (!isDragging) {
            return;
        }

        initialX = currentX;
        initialY = currentY;
        isDragging = false;
    }

    /**
     * Встановити position через transform
     */
    function setTranslate(xPos, yPos) {
        if (!dialogContainer) {
            return;
        }

        dialogContainer.style.transform = 'translate(' + xPos + 'px, ' + yPos + 'px)';
    }

    /**
     * Скинути позицію при відкритті
     */
    function resetPosition() {
        xOffset = 0;
        yOffset = 0;
        currentX = 0;
        currentY = 0;
        
        if (dialogContainer) {
            dialogContainer.style.transform = 'translate(0, 0)';
        }
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

