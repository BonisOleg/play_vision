/**
 * INLINE AI CHAT IN HEADER
 * Повна логіка роботи чату в хедері з можливістю відкріплення
 */

(function () {
    'use strict';

    // ========================================
    // CONFIGURATION
    // ========================================

    const CONFIG = {
        maxHeight: '50vh',  // Максимальна висота чату
        animationDuration: 300,
        detachedModalWidth: 400,
        detachedModalMinHeight: 200,
        detachedModalDefaultHeight: 500,
        resizeMinHeight: 200,
        resizeMaxHeight: null  // Буде встановлено динамічно (50% від висоти екрану)
    };

    // ========================================
    // STATE
    // ========================================

    let state = {
        isDetached: false,
        hasMessages: false,
        chatHistory: [],
        modal: null,
        modalPosition: { x: 100, y: 100 },
        modalHeight: CONFIG.detachedModalDefaultHeight,
        isDragging: false,
        isResizing: false,
        dragOffset: { x: 0, y: 0 }
    };

    // ========================================
    // DOM ELEMENTS
    // ========================================

    const elements = {
        inline: document.querySelector('[data-ai-chat-inline]'),
        messages: document.querySelector('[data-ai-messages]'),
        input: document.querySelector('[data-ai-input]'),
        sendBtn: document.querySelector('[data-ai-send]'),
        detachBtn: document.querySelector('[data-ai-detach]')
    };

    // ========================================
    // INITIALIZATION
    // ========================================

    function init() {
        if (!elements.inline) return;

        // Встановлюємо максимальну висоту для resize
        CONFIG.resizeMaxHeight = window.innerHeight * 0.5;

        // Прив'язуємо обробники подій
        bindEvents();

        console.log('✅ AI Chat Inline initialized');
    }

    // ========================================
    // EVENT HANDLERS
    // ========================================

    function bindEvents() {
        // Відправка повідомлення
        if (elements.sendBtn) {
            elements.sendBtn.addEventListener('click', handleSendMessage);
        }

        if (elements.input) {
            elements.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                }
            });
        }

        // Відкріплення чату
        if (elements.detachBtn) {
            elements.detachBtn.addEventListener('click', handleDetachChat);
        }

        // Оновлення максимальної висоти при зміні розміру вікна
        window.addEventListener('resize', handleWindowResize);
    }

    // ========================================
    // MESSAGE HANDLING
    // ========================================

    function handleSendMessage() {
        const message = elements.input.value.trim();

        if (!message) return;

        console.log('📨 Sending message:', message);

        // Показуємо історію чату ПЕРЕД додаванням повідомлення
        if (!state.hasMessages) {
            showChatHistory();
        }

        // Додаємо повідомлення користувача
        addMessage(message, 'user');

        // Очищаємо input
        elements.input.value = '';

        // Показуємо кнопку відкріплення
        if (elements.detachBtn) {
            elements.detachBtn.style.display = 'flex';
        }

        // Симулюємо відповідь AI (замість реального API)
        setTimeout(() => {
            const aiResponse = 'Дякую за ваше запитання! Я AI помічник Play Vision. Наразі працюю в демонстраційному режимі.';
            addMessage(aiResponse, 'bot');
        }, 1000);
    }

    function addMessage(text, sender) {
        const messageEl = document.createElement('div');
        messageEl.className = `ai-message ai-message--${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'ai-message-avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = 'ai-message-content';
        const p = document.createElement('p');
        p.textContent = text;
        content.appendChild(p);

        messageEl.appendChild(avatar);
        messageEl.appendChild(content);

        // Додаємо до history
        state.chatHistory.push({ text, sender, element: messageEl });

        // Додаємо до DOM
        const container = state.isDetached
            ? document.querySelector('.ai-chat-modal-messages')
            : elements.messages;

        if (container) {
            console.log('✅ Adding message to container', container);
            container.appendChild(messageEl);
            // Прокручуємо вниз
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 10);
        } else {
            console.error('❌ Container not found!');
        }

        state.hasMessages = true;
    }

    function showChatHistory() {
        if (!elements.messages) return;

        elements.messages.style.display = 'flex';

        // Плавна анімація появи ВГОРУ
        requestAnimationFrame(() => {
            elements.messages.style.opacity = '0';
            elements.messages.style.transform = 'translateY(10px)';

            requestAnimationFrame(() => {
                elements.messages.style.transition = `opacity ${CONFIG.animationDuration}ms ease, transform ${CONFIG.animationDuration}ms ease`;
                elements.messages.style.opacity = '1';
                elements.messages.style.transform = 'translateY(0)';
            });
        });
    }

    function hideChatHistory() {
        if (!elements.messages) return;

        elements.messages.style.opacity = '0';
        elements.messages.style.transform = 'translateY(10px)';

        setTimeout(() => {
            elements.messages.style.display = 'none';
            elements.messages.style.transform = 'translateY(0)';
        }, CONFIG.animationDuration);
    }

    // ========================================
    // DETACH/ATTACH LOGIC
    // ========================================

    function handleDetachChat() {
        if (state.isDetached) {
            attachChat();
        } else {
            detachChat();
        }
    }

    function detachChat() {
        state.isDetached = true;

        // Створюємо модальне вікно
        createModal();

        // Приховуємо весь inline чат контейнер
        if (elements.inline) {
            elements.inline.style.display = 'none';
        }

        // Переміщаємо повідомлення в модалку
        transferMessagesToModal();

        console.log('🔓 Chat detached');
    }

    function attachChat() {
        state.isDetached = false;

        // Переміщаємо повідомлення назад в inline
        transferMessagesToInline();

        // Видаляємо модалку
        if (state.modal) {
            state.modal.remove();
            state.modal = null;
        }

        // Показуємо весь inline чат контейнер
        if (elements.inline) {
            elements.inline.style.display = 'flex';
        }

        // Показуємо історію чату якщо є повідомлення
        if (elements.messages && state.hasMessages) {
            elements.messages.style.display = 'flex';
        }

        console.log('📌 Chat attached');
    }

    // ========================================
    // MODAL CREATION
    // ========================================

    function createModal() {
        // Створюємо модальне вікно
        const modal = document.createElement('div');
        modal.className = 'ai-chat-modal';
        modal.style.left = `${state.modalPosition.x}px`;
        modal.style.top = `${state.modalPosition.y}px`;
        modal.style.width = `${CONFIG.detachedModalWidth}px`;
        modal.style.height = `${state.modalHeight}px`;
        modal.style.maxHeight = CONFIG.maxHeight;

        // Header з drag handle
        const header = document.createElement('div');
        header.className = 'ai-chat-modal-header';

        const title = document.createElement('h3');
        title.className = 'ai-chat-modal-title';
        title.textContent = 'AI Помічник';

        const closeBtn = document.createElement('button');
        closeBtn.className = 'ai-chat-modal-close';
        closeBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
        `;
        closeBtn.addEventListener('click', () => attachChat());

        header.appendChild(title);
        header.appendChild(closeBtn);

        // Messages container
        const messagesContainer = document.createElement('div');
        messagesContainer.className = 'ai-chat-modal-messages';

        // Input wrapper
        const inputWrapper = document.createElement('div');
        inputWrapper.className = 'ai-chat-modal-input-wrapper';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'ai-chat-modal-input';
        input.placeholder = 'Запитайте AI помічника...';

        const sendBtn = document.createElement('button');
        sendBtn.className = 'ai-chat-modal-send';
        sendBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22,2 15,22 11,13 2,9" />
            </svg>
        `;

        inputWrapper.appendChild(input);
        inputWrapper.appendChild(sendBtn);

        // Resize handle
        const resizeHandle = document.createElement('div');
        resizeHandle.className = 'ai-chat-modal-resize';

        // Складаємо модалку
        modal.appendChild(header);
        modal.appendChild(messagesContainer);
        modal.appendChild(inputWrapper);
        modal.appendChild(resizeHandle);

        // Додаємо в DOM
        document.body.appendChild(modal);
        state.modal = modal;

        // Прив'язуємо обробники
        bindModalEvents(modal, header, input, sendBtn, resizeHandle);
    }

    function bindModalEvents(modal, header, input, sendBtn, resizeHandle) {
        // Drag
        header.addEventListener('mousedown', (e) => startDrag(e, modal));

        // Send message
        sendBtn.addEventListener('click', () => {
            handleModalSendMessage(input);
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleModalSendMessage(input);
            }
        });

        // Resize
        resizeHandle.addEventListener('mousedown', (e) => startResize(e, modal));
    }

    function handleModalSendMessage(input) {
        const message = input.value.trim();

        if (!message) return;

        addMessage(message, 'user');
        input.value = '';

        // Симулюємо відповідь
        setTimeout(() => {
            const aiResponse = 'Дякую за ваше запитання! Я AI помічник Play Vision.';
            addMessage(aiResponse, 'bot');
        }, 1000);
    }

    // ========================================
    // DRAG AND DROP
    // ========================================

    function startDrag(e, modal) {
        if (e.target.closest('.ai-chat-modal-close')) return;

        state.isDragging = true;
        state.dragOffset.x = e.clientX - state.modalPosition.x;
        state.dragOffset.y = e.clientY - state.modalPosition.y;

        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', stopDrag);

        modal.style.cursor = 'grabbing';
        e.preventDefault();
    }

    function drag(e) {
        if (!state.isDragging) return;

        state.modalPosition.x = e.clientX - state.dragOffset.x;
        state.modalPosition.y = e.clientY - state.dragOffset.y;

        // Обмежуємо в межах вікна
        state.modalPosition.x = Math.max(0, Math.min(state.modalPosition.x, window.innerWidth - CONFIG.detachedModalWidth));
        state.modalPosition.y = Math.max(0, Math.min(state.modalPosition.y, window.innerHeight - 100));

        if (state.modal) {
            state.modal.style.left = `${state.modalPosition.x}px`;
            state.modal.style.top = `${state.modalPosition.y}px`;
        }
    }

    function stopDrag() {
        state.isDragging = false;
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('mouseup', stopDrag);

        if (state.modal) {
            state.modal.style.cursor = '';
        }
    }

    // ========================================
    // RESIZE
    // ========================================

    function startResize(e, modal) {
        state.isResizing = true;
        state.initialHeight = modal.offsetHeight;
        state.initialY = e.clientY;

        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);

        e.preventDefault();
    }

    function resize(e) {
        if (!state.isResizing) return;

        const deltaY = e.clientY - state.initialY;
        let newHeight = state.initialHeight + deltaY;

        // Обмежуємо висоту
        newHeight = Math.max(CONFIG.resizeMinHeight, newHeight);
        newHeight = Math.min(CONFIG.resizeMaxHeight, newHeight);

        state.modalHeight = newHeight;

        if (state.modal) {
            state.modal.style.height = `${newHeight}px`;
        }
    }

    function stopResize() {
        state.isResizing = false;
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
    }

    // ========================================
    // MESSAGE TRANSFER
    // ========================================

    function transferMessagesToModal() {
        if (!state.modal) return;

        const modalMessages = state.modal.querySelector('.ai-chat-modal-messages');
        if (!modalMessages) return;

        // Очищаємо модальні повідомлення
        modalMessages.innerHTML = '';

        // Переносимо всі повідомлення
        state.chatHistory.forEach(msg => {
            const clone = msg.element.cloneNode(true);
            modalMessages.appendChild(clone);
        });

        // Прокручуємо вниз
        modalMessages.scrollTop = modalMessages.scrollHeight;
    }

    function transferMessagesToInline() {
        if (!elements.messages) return;

        // Очищаємо inline повідомлення
        elements.messages.innerHTML = '';

        // Переносимо всі повідомлення назад
        state.chatHistory.forEach(msg => {
            const clone = msg.element.cloneNode(true);
            elements.messages.appendChild(clone);
        });

        // Прокручуємо вниз
        elements.messages.scrollTop = elements.messages.scrollHeight;
    }

    // ========================================
    // WINDOW RESIZE
    // ========================================

    function handleWindowResize() {
        // Оновлюємо максимальну висоту
        CONFIG.resizeMaxHeight = window.innerHeight * 0.5;

        // Коригуємо позицію модалки якщо вона виходить за межі
        if (state.isDetached && state.modal) {
            state.modalPosition.x = Math.max(0, Math.min(state.modalPosition.x, window.innerWidth - CONFIG.detachedModalWidth));
            state.modalPosition.y = Math.max(0, Math.min(state.modalPosition.y, window.innerHeight - 100));

            state.modal.style.left = `${state.modalPosition.x}px`;
            state.modal.style.top = `${state.modalPosition.y}px`;

            // Коригуємо висоту якщо потрібно
            if (state.modalHeight > CONFIG.resizeMaxHeight) {
                state.modalHeight = CONFIG.resizeMaxHeight;
                state.modal.style.height = `${state.modalHeight}px`;
            }
        }
    }

    // ========================================
    // START
    // ========================================

    // Ініціалізація при завантаженні DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

