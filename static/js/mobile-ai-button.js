/**
 * Кнопка AI чата в мобільному нижньому меню
 * Відкриває AI Chat Dialog при натисканні
 */

(function () {
    'use strict';

    /**
     * Ініціалізація кнопки AI чата
     */
    function initMobileAIButton() {
        const aiButton = document.querySelector('[data-ai-open]');
        const aiDialog = document.querySelector('[data-ai-chat-dialog]');

        if (!aiButton || !aiDialog) return;

        // Обробник кліку на кнопку AI
        aiButton.addEventListener('click', function (e) {
            e.preventDefault();
            openAIDialog();
        });

        // Обробник для touch пристроїв
        aiButton.addEventListener('touchend', function (e) {
            e.preventDefault();
            openAIDialog();
        });
    }

    /**
     * Відкриття AI Chat Dialog
     */
    function openAIDialog() {
        const aiDialog = document.querySelector('[data-ai-chat-dialog]');
        const aiDialogInput = document.querySelector('[data-ai-dialog-input]');

        if (!aiDialog) return;

        // Показуємо діалог
        aiDialog.setAttribute('aria-hidden', 'false');
        aiDialog.classList.add('dialog-open');

        // Фокусуємо інпут після відкриття
        setTimeout(() => {
            if (aiDialogInput) {
                aiDialogInput.focus();
            }
        }, 300);

        // Блокуємо скролл body
        document.body.style.overflow = 'hidden';
    }

    // Ініціалізація при завантаженні DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileAIButton);
    } else {
        initMobileAIButton();
    }
})();

