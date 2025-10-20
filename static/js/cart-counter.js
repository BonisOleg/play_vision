/**
 * Лічильник товарів у кошику
 */

const updateCartCount = async () => {
    const cartCountEl = document.querySelector('[data-cart-count]');
    if (!cartCountEl) return;

    try {
        const response = await fetch('/api/v1/cart/count/');
        if (response.ok) {
            const data = await response.json();
            const count = data.count || 0;
            cartCountEl.textContent = count;

            if (count === 0) {
                cartCountEl.style.display = 'none';
            } else {
                cartCountEl.style.display = 'block';
            }
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

