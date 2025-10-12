/**
 * КОШИК PLAY VISION
 * Інтерактивність кошика згідно дизайну
 */

class Cart {
    constructor() {
        this.init();
        this.apiBaseUrl = '/api/v1/cart/';
    }

    init() {
        // Обробники подій
        document.addEventListener('click', this.handleClick.bind(this));

        // Промокод
        const applyCouponBtn = document.getElementById('apply-coupon');
        if (applyCouponBtn) {
            applyCouponBtn.addEventListener('click', this.applyCoupon.bind(this));
        }

        // Enter на промокод
        const couponInput = document.getElementById('coupon-input');
        if (couponInput) {
            couponInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.applyCoupon();
                }
            });
        }
    }

    handleClick(e) {
        const action = e.target.dataset.action;
        const itemId = e.target.dataset.itemId;

        switch (action) {
            case 'increase':
                this.updateQuantity(itemId, 1);
                break;
            case 'decrease':
                this.updateQuantity(itemId, -1);
                break;
            case 'remove':
                this.removeItem(itemId);
                break;
            case 'add-recommendation':
                this.addRecommendation(e.target.dataset.courseId, e.target.dataset.courseTitle);
                break;
            case 'remove-coupon':
                this.removeCoupon();
                break;
        }
    }

    async updateQuantity(itemId, change) {
        try {
            this.setItemLoading(itemId, true);

            const currentQuantity = this.getCurrentQuantity(itemId);
            const newQuantity = currentQuantity + change;

            if (newQuantity <= 0) {
                await this.removeItem(itemId);
                return;
            }

            const response = await this.apiRequest('update/', {
                method: 'POST',
                body: JSON.stringify({
                    item_id: itemId,
                    quantity: newQuantity
                })
            });

            if (response.success) {
                this.updateQuantityDisplay(itemId, newQuantity);
                this.updateSummary(response);
                this.showToast(response.message, 'success');
            } else {
                this.showToast(response.message || 'Помилка оновлення кількості', 'error');
            }
        } catch (error) {
            this.showToast('Помилка оновлення кошика', 'error');
        } finally {
            this.setItemLoading(itemId, false);
        }
    }

    async removeItem(itemId) {
        try {
            this.setItemLoading(itemId, true);

            const response = await this.apiRequest('remove/', {
                method: 'POST',
                body: JSON.stringify({
                    item_id: itemId
                })
            });

            if (response.success) {
                // Видалити елемент з DOM з анімацією
                const item = document.querySelector(`[data-item-id="${itemId}"]`);
                if (item) {
                    item.classList.add('cart-item-removing');

                    setTimeout(() => {
                        item.remove();
                        this.checkEmptyCart();
                    }, 300);
                }

                this.updateSummary(response);
                this.showToast(response.message, 'success');
            } else {
                this.showToast(response.message || 'Помилка видалення товару', 'error');
            }
        } catch (error) {
            this.showToast('Помилка видалення товару', 'error');
        } finally {
            this.setItemLoading(itemId, false);
        }
    }

    async addRecommendation(courseId, courseTitle) {
        try {
            const response = await this.apiRequest('add/', {
                method: 'POST',
                body: JSON.stringify({
                    item_type: 'course',
                    item_id: courseId,
                    quantity: 1
                })
            });

            if (response.success) {
                this.showToast(`"${courseTitle}" додано в кошик`, 'success');
                // Оновити сторінку для показу нового товару
                setTimeout(() => window.location.reload(), 1000);
            } else {
                this.showToast(response.message || 'Помилка додавання товару', 'error');
            }
        } catch (error) {
            this.showToast('Помилка додавання товару', 'error');
        }
    }

    async applyCoupon() {
        const couponInput = document.getElementById('coupon-input');
        const code = couponInput.value.trim();

        if (!code) {
            this.showToast('Введіть промокод', 'error');
            couponInput.focus();
            return;
        }

        try {
            this.setCouponLoading(true);

            const response = await this.apiRequest('apply-coupon/', {
                method: 'POST',
                body: JSON.stringify({ code })
            });

            if (response.success) {
                this.updateSummary(response);
                this.showToast(response.message, 'success');
                couponInput.value = '';
                couponInput.disabled = true;
                document.getElementById('apply-coupon').textContent = 'Застосовано';
                document.getElementById('apply-coupon').disabled = true;

                // Показати кнопку скасування
                this.showCouponRemoveButton(code);
            } else {
                this.showToast(response.message || 'Помилка застосування промокоду', 'error');
            }
        } catch (error) {
            this.showToast('Помилка застосування промокоду', 'error');
        } finally {
            this.setCouponLoading(false);
        }
    }

    async removeCoupon() {
        try {
            // Скидання купону через backend
            const response = await fetch('/cart/apply-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ code: '' }) // Порожній код скасовує купон
            });

            const data = await response.json();

            if (data.success || response.ok) {
                // Оновити UI
                const couponInput = document.getElementById('coupon-input');
                const applyBtn = document.getElementById('apply-coupon');

                couponInput.value = '';
                couponInput.disabled = false;
                applyBtn.textContent = 'Застосувати';
                applyBtn.disabled = false;

                // Оновити підсумок
                this.updateSummary({
                    subtotal: data.subtotal || parseFloat(document.querySelector('[data-subtotal]').textContent.replace('$', '')),
                    discount: 0,
                    total: data.total || data.subtotal
                });

                this.showToast('Промокод скасовано', 'success');

                // Видалити блок застосованого купону
                const appliedBlock = document.querySelector('.cart-coupon-applied');
                if (appliedBlock) {
                    appliedBlock.remove();
                }
            }
        } catch (error) {
            this.showToast('Помилка скасування промокоду', 'error');
        }
    }

    showCouponRemoveButton(code) {
        const couponContainer = document.querySelector('.cart-coupon');
        const removeButton = document.createElement('div');
        removeButton.className = 'cart-coupon-applied';
        removeButton.innerHTML = `
            <span>Промокод "${code}" застосовано</span>
            <button class="cart-coupon-remove" data-action="remove-coupon">Скасувати</button>
        `;
        couponContainer.parentNode.insertBefore(removeButton, couponContainer.nextSibling);
    }

    getCurrentQuantity(itemId) {
        const quantityInput = document.querySelector(`[data-item-id="${itemId}"] .cart-quantity-input`);
        return parseInt(quantityInput.value) || 1;
    }

    updateQuantityDisplay(itemId, quantity) {
        const quantityInput = document.querySelector(`[data-item-id="${itemId}"] .cart-quantity-input`);
        if (quantityInput) {
            quantityInput.value = quantity;
        }

        // Оновити ціну товару
        const item = document.querySelector(`[data-item-id="${itemId}"]`);
        if (item) {
            const priceElement = item.querySelector('.cart-item-price');
            const itemObject = this.getItemFromDOM(item);
            if (priceElement && itemObject) {
                const unitPrice = parseFloat(itemObject.price);
                priceElement.textContent = `$${(unitPrice * quantity).toFixed(2)}`;
            }
        }
    }

    updateSummary(data) {
        const elements = {
            subtotal: document.querySelector('[data-subtotal]'),
            discount: document.querySelector('[data-discount]'),
            tips: document.querySelector('[data-tips]'),
            total: document.querySelector('[data-total]')
        };

        if (data.subtotal !== undefined && elements.subtotal) {
            elements.subtotal.textContent = `$${parseFloat(data.subtotal).toFixed(2)}`;
        }
        if (data.discount !== undefined && elements.discount) {
            elements.discount.textContent = `-$${parseFloat(data.discount).toFixed(2)}`;
        }
        if (data.tips !== undefined && elements.tips) {
            elements.tips.textContent = `$${parseFloat(data.tips).toFixed(2)}`;
        }
        if (data.total !== undefined && elements.total) {
            elements.total.textContent = `$${parseFloat(data.total).toFixed(2)}`;
        }

        // Оновити лічильник в хедері
        this.updateCartCounter(data.cart_count);
    }

    updateCartCounter(count) {
        const counter = document.querySelector('[data-cart-count]');
        if (counter) {
            counter.textContent = count || 0;
            counter.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    checkEmptyCart() {
        const items = document.querySelectorAll('.cart-item');
        if (items.length === 0) {
            // Показати повідомлення про порожній кошик
            setTimeout(() => window.location.reload(), 500);
        }
    }

    setItemLoading(itemId, loading) {
        const item = document.querySelector(`[data-item-id="${itemId}"]`);
        if (item) {
            item.classList.toggle('cart-item-loading', loading);

            // Відключити кнопки під час завантаження
            const buttons = item.querySelectorAll('button');
            buttons.forEach(btn => {
                btn.disabled = loading;
            });
        }
    }

    setCouponLoading(loading) {
        const btn = document.getElementById('apply-coupon');
        if (btn) {
            btn.disabled = loading;
            btn.textContent = loading ? 'Застосування...' : 'Застосувати';
        }
    }

    showToast(message, type = 'info') {
        // Використовуємо нову централізовану систему якщо доступна
        if (window.notify && typeof window.notify.show === 'function') {
            return window.notify.show(message, type);
        }

        // Fallback на стару систему (для сумісності)
        const existingToasts = document.querySelectorAll('.cart-toast');
        existingToasts.forEach(toast => toast.remove());

        // Створити новий тост
        const toast = document.createElement('div');
        toast.className = `cart-toast ${type}`;
        toast.innerHTML = `
            <div class="cart-toast-content">
                <span>${message}</span>
                <button class="cart-toast-close" aria-label="Закрити">&times;</button>
            </div>
        `;

        document.body.appendChild(toast);

        // Автовидалення
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);

        // Видалення по кліку
        toast.querySelector('.cart-toast-close').addEventListener('click', () => {
            toast.remove();
        });
    }

    async apiRequest(endpoint, options = {}) {
        const url = this.apiBaseUrl + endpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            credentials: 'same-origin',
        };

        const requestOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, requestOptions);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Cart API request failed:', error);
            throw error;
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    getItemFromDOM(itemElement) {
        // Отримати дані товару з DOM для розрахунків
        return {
            id: itemElement.dataset.itemId,
            name: itemElement.querySelector('.cart-item-title')?.textContent || '',
            price: this.extractPrice(itemElement.querySelector('.cart-item-price')?.textContent || '0')
        };
    }

    extractPrice(priceText) {
        // Витягти числове значення з тексту ціни
        const match = priceText.match(/[\d.,]+/);
        return match ? parseFloat(match[0].replace(',', '.')) : 0;
    }
}

/**
 * АНІМАЦІЇ КОШИКА
 */
class CartAnimations {
    static addToCartAnimation(button) {
        // Анімація додавання в кошик (літаюча іконка)
        const icon = document.createElement('div');
        icon.className = 'flying-cart-icon';
        icon.innerHTML = '🛒';

        // Позиція кнопки (динамічна через CSS variables)
        const buttonRect = button.getBoundingClientRect();
        icon.style.setProperty('--start-x', buttonRect.left + 'px');
        icon.style.setProperty('--start-y', buttonRect.top + 'px');

        document.body.appendChild(icon);

        // Анімація до кошика в хедері
        const cartIcon = document.querySelector('.cart-icon');
        if (cartIcon) {
            const cartRect = cartIcon.getBoundingClientRect();

            requestAnimationFrame(() => {
                icon.style.setProperty('--end-x', cartRect.left + 'px');
                icon.style.setProperty('--end-y', cartRect.top + 'px');
                icon.classList.add('flying');
            });
        }

        // Видалити після анімації
        setTimeout(() => {
            if (icon.parentNode) {
                icon.remove();
            }
        }, 650);
    }
}

/**
 * UTILITY ФУНКЦІЇ
 */
class CartUtils {
    static formatPrice(amount) {
        return `$${parseFloat(amount).toFixed(2)}`;
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Ініціалізація кошика
document.addEventListener('DOMContentLoaded', () => {
    // Ініціалізувати тільки на сторінці кошика
    if (document.querySelector('.cart-container')) {
        window.cart = new Cart();
        console.log('Cart initialized');
    }
});

// Експорт для використання в інших модулях
window.Cart = Cart;
window.CartAnimations = CartAnimations;
window.CartUtils = CartUtils;
