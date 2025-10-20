/**
 * iOS Safari viewport height fix
 * Виправляє проблему з 100vh на мобільних пристроях
 */

const setVhProperty = () => {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
};

// Встановити при завантаженні
setVhProperty();

// Оновлювати при зміні розміру (але з debounce для performance)
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(setVhProperty, 100);
});

// Оновити при зміні орієнтації
window.addEventListener('orientationchange', () => {
    setTimeout(setVhProperty, 100);
});

