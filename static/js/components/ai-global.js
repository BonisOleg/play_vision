/**
 * AI Global Widget - Floating button and mini chat
 * Доступний на всіх сторінках для всіх користувачів
 */

(function () {
    'use strict';

    // Елементи
    const fabBtn = document.getElementById('ai-fab-btn');
    const miniChat = document.getElementById('ai-mini-chat');
    const closeChatBtn = document.getElementById('ai-mini-chat-close');
    const sendBtn = document.getElementById('ai-mini-send');
    const input = document.getElementById('ai-mini-input');
    const messagesContainer = document.getElementById('ai-mini-chat-messages');

    if (!fabBtn || !miniChat) {
        console.warn('AI global widget elements not found');
        return;
    }

    // Відкрити/закрити міні-чат
    function toggleMiniChat() {
        miniChat.classList.toggle('active');

        if (miniChat.classList.contains('active')) {
            // Фокус на input при відкритті
            setTimeout(() => input.focus(), 100);

            // Зберегти стан
            localStorage.setItem('ai-mini-chat-opened', 'true');
        } else {
            localStorage.setItem('ai-mini-chat-opened', 'false');
        }
    }

    // Відкрити при кліку на FAB
    fabBtn.addEventListener('click', toggleMiniChat);

    // Закрити при кліку на кнопку закриття
    if (closeChatBtn) {
        closeChatBtn.addEventListener('click', toggleMiniChat);
    }

    // Надіслати повідомлення
    async function sendMessage() {
        const query = input.value.trim();

        if (!query) return;

        // Додати повідомлення користувача
        addMessage(query, 'user');
        input.value = '';

        // Показати typing indicator
        showTyping();

        try {
            // AJAX запит до AI
            const response = await fetch('/ai/ask/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            // Видалити typing
            hideTyping();

            if (data.success) {
                // Додати відповідь AI
                addMessage(data.response, 'bot', data.query_id);
            } else {
                addMessage(data.message || 'Помилка обробки запиту', 'bot');
            }

        } catch (error) {
            hideTyping();
            addMessage('Помилка з\'єднання. Спробуйте пізніше.', 'bot');
            console.error('AI request error:', error);
        }
    }

    // Додати повідомлення в чат
    function addMessage(text, type, queryId = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-mini-message ai-mini-message--${type}`;

        // Форматування markdown (базове)
        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        messageDiv.innerHTML = formattedText;

        // Додати кнопки оцінки для bot повідомлень
        if (type === 'bot' && queryId) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'ai-mini-actions';
            actionsDiv.innerHTML = `
                <button class="ai-mini-rate" data-query-id="${queryId}" data-rating="5" title="Корисно">👍</button>
                <button class="ai-mini-rate" data-query-id="${queryId}" data-rating="1" title="Не корисно">👎</button>
            `;
            messageDiv.appendChild(actionsDiv);

            // Event listeners для оцінок
            actionsDiv.querySelectorAll('.ai-mini-rate').forEach(btn => {
                btn.addEventListener('click', function () {
                    rateResponse(this.dataset.queryId, this.dataset.rating);
                    this.classList.add('rated');
                    this.disabled = true;
                });
            });
        }

        messagesContainer.appendChild(messageDiv);

        // Scroll до нового повідомлення
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Показати typing indicator
    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'ai-mini-message--typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <span class="ai-typing-dot"></span>
            <span class="ai-typing-dot"></span>
            <span class="ai-typing-dot"></span>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Сховати typing indicator
    function hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) {
            typing.remove();
        }
    }

    // Оцінити відповідь
    async function rateResponse(queryId, rating) {
        try {
            await fetch(`/ai/rate/${queryId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ rating: parseInt(rating) })
            });
        } catch (error) {
            console.error('Rating error:', error);
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Відновити стан при завантаженні
    const wasOpened = localStorage.getItem('ai-mini-chat-opened');
    if (wasOpened === 'true') {
        // Не відкривати автоматично - користувач сам вирішує
        // miniChat.classList.add('active');
    }

    // Helper: Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

})();

