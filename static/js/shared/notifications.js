/**
 * ЦЕНТРАЛІЗОВАНА СИСТЕМА ПОВІДОМЛЕНЬ
 * Замінює всі showMessage/showToast/showNotification
 * Сумісна з існуючим кодом через fallback
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.queue = [];
        this.maxVisible = 5;
        this.init();
    }

    init() {
        // Створюємо контейнер при першому виклику
        document.addEventListener('DOMContentLoaded', () => {
            this.createContainer();
        });

        // Якщо DOM вже завантажений
        if (document.readyState !== 'loading') {
            this.createContainer();
        }
    }

    createContainer() {
        if (this.container) return;

        let container = document.getElementById('app-notifications');
        if (!container) {
            container = document.createElement('div');
            container.id = 'app-notifications';
            container.className = 'app-notifications';
            container.setAttribute('aria-live', 'polite');
            container.setAttribute('aria-atomic', 'true');
            document.body.appendChild(container);
        }
        this.container = container;
    }

    show(message, type = 'info', duration = 5000) {
        if (!message) return null;

        // Перевіряємо чи існує контейнер
        if (!this.container) {
            this.createContainer();
        }

        // Fallback на стару систему якщо потрібно
        if (typeof showMessage === 'function' && window.__USE_OLD_NOTIFICATIONS__) {
            return showMessage(message, type);
        }

        const notification = this.createNotification(message, type);
        this.container.appendChild(notification);

        // Обмеження кількості видимих
        this.limitVisibleNotifications();

        // Auto-remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    createNotification(message, type) {
        const notif = document.createElement('div');
        notif.className = `notification notification--${type}`;
        notif.setAttribute('role', 'status');

        // Escape HTML для безпеки
        const safeMessage = this.escapeHTML(message);

        notif.innerHTML = `
            <span class="notification__message">${safeMessage}</span>
            <button class="notification__close" aria-label="Закрити" type="button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        `;

        // Close button handler
        const closeBtn = notif.querySelector('.notification__close');
        closeBtn.addEventListener('click', () => {
            this.remove(notif);
        });

        return notif;
    }

    remove(notification) {
        if (!notification || !notification.parentNode) return;

        notification.classList.add('notification--removing');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    limitVisibleNotifications() {
        if (!this.container) return;

        const notifications = this.container.querySelectorAll('.notification:not(.notification--removing)');
        if (notifications.length > this.maxVisible) {
            // Видалити найстаріші
            for (let i = 0; i < notifications.length - this.maxVisible; i++) {
                this.remove(notifications[i]);
            }
        }
    }

    escapeHTML(str) {
        if (typeof str !== 'string') return '';

        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // Alias methods для зручності
    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    // Compatibility aliases
    toast(message, type, duration) {
        return this.show(message, type, duration);
    }

    message(message, type, duration) {
        return this.show(message, type, duration);
    }
}

// Глобальна ініціалізація
window.notify = new NotificationSystem();

// Експорт для модулів
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationSystem;
}

// Debug info
console.log('[Notifications] Централізована система завантажена');

