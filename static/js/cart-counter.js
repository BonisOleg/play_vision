/**
 * Лічильник товарів у кошику
 * Оновлено: динамічний показ/приховування іконки кошика
 */

const updateCartCount = async () => {
    const cartCountEls = document.querySelectorAll('[data-cart-count]');
    const cartIconEls = document.querySelectorAll('[data-cart-icon]');

    if (cartCountEls.length === 0 && cartIconEls.length === 0) return;

    try {
        const response = await fetch('/api/v1/cart/count/');
        if (response.ok) {
            const data = await response.json();
            const count = data.count || 0;

            // Оновлюємо всі лічильники
            cartCountEls.forEach(el => {
                el.textContent = count;
                if (count === 0) {
                    el.style.display = 'none';
                } else {
                    el.style.display = 'flex';
                }
            });

            // Показуємо/ховаємо іконку кошика залежно від кількості товарів
            cartIconEls.forEach(el => {
                if (count === 0) {
                    el.style.display = 'none';
                } else {
                    el.style.display = 'flex';
                }
            });
        }
    } catch (error) {
        console.error('Error updating cart count:', error);
    }
};

// Оновлення при завантаженні сторінки
document.addEventListener('DOMContentLoaded', updateCartCount);

// Оновлення при custom події
document.addEventListener('cartUpdated', updateCartCount);

// Глобальна функція для оновлення з інших скриптів
window.updateCartCount = updateCartCount;

