/**
 * КОШИК В ХЕДЕРІ
 * Глобальний функціонал кошика для всіх сторінок
 */

class CartHeader {
    constructor() {
        this.cartCounter = document.querySelector('[data-cart-count]');
        this.cartIcon = document.querySelector('.cart-icon');
        this.init();
    }

    init() {
        // Підписка на події оновлення кошика
        document.addEventListener('cartUpdated', this.handleCartUpdate.bind(this));

        // Ініціальне завантаження лічильника
        this.loadCartCount();
    }

    async loadCartCount() {
        try {
            const response = await fetch('/api/v1/cart/count/', {
                credentials: 'same-origin'
            });

            if (response.ok) {
                const data = await response.json();
                this.updateCounter(data.count);
            }
        } catch (error) {
            console.warn('Failed to load cart count:', error);
        }
    }

    updateCounter(count) {
        if (this.cartCounter) {
            this.cartCounter.textContent = count || 0;
            this.cartCounter.setAttribute('data-cart-count', count || 0);

            // Анімація при зміні
            if (count > 0) {
                this.cartCounter.style.display = 'inline';
                this.animateCounter();
            } else {
                this.cartCounter.style.display = 'none';
            }
        }
    }

    animateCounter() {
        if (this.cartCounter && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.cartCounter.style.transform = 'scale(1.3)';
            this.cartCounter.style.transition = 'transform 0.2s ease';

            setTimeout(() => {
                this.cartCounter.style.transform = 'scale(1)';
            }, 200);
        }
    }

    handleCartUpdate(event) {
        if (event.detail && event.detail.count !== undefined) {
            this.updateCounter(event.detail.count);
        }
    }

    // Метод для додавання товару з інших сторінок
    static async addToCart(itemType, itemId, itemTitle) {
        try {
            const response = await fetch('/api/v1/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CartHeader.getCSRFToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    item_type: itemType,
                    item_id: itemId,
                    quantity: 1
                })
            });

            const data = await response.json();

            if (data.success) {
                // Тригер події оновлення
                document.dispatchEvent(new CustomEvent('cartUpdated', {
                    detail: { count: data.cart_count }
                }));

                // Показати повідомлення
                CartHeader.showMessage(data.message, 'success');

                // Анімація додавання
                const button = event.target;
                if (button) {
                    window.CartAnimations?.addToCartAnimation(button);
                }
            } else {
                CartHeader.showMessage(data.error || 'Помилка додавання товару', 'error');
            }
        } catch (error) {
            CartHeader.showMessage('Помилка додавання товару', 'error');
        }
    }

    static showMessage(message, type = 'info') {
        // Спрощена система повідомлень
        const existing = document.querySelector('.cart-header-message');
        if (existing) existing.remove();

        const messageEl = document.createElement('div');
        messageEl.className = `cart-header-message cart-header-message--${type}`;
        messageEl.textContent = message;

        messageEl.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: ${type === 'error' ? '#f44336' : '#4caf50'};
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            z-index: 1000;
            font-size: 14px;
            max-width: 300px;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(messageEl);

        setTimeout(() => messageEl.remove(), 3000);
    }

    static getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
}

// Ініціалізація на всіх сторінках
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.cart-icon')) {
        window.cartHeader = new CartHeader();
    }
});

// Експорт для використання в інших модулях
window.CartHeader = CartHeader;
