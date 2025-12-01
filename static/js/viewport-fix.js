/**
 * iOS Safari viewport height fix
 * Виправляє проблему з 100vh на мобільних пристроях
 */

const setVhProperty = () => {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
};

setVhProperty();

let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(setVhProperty, 100);
});

window.addEventListener('orientationchange', () => {
    setTimeout(setVhProperty, 100);
});

// Використовуємо єдину функцію для додавання класу (якщо ios-detection.js вже завантажений)
// Якщо ні, використовуємо fallback
(function() {
    if (typeof window.isIOS === 'function') {
        if (window.isIOS()) {
            window.addIOSClass();
        }
    } else {
        // Fallback якщо ios-detection.js ще не завантажений
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        if (isIOS) {
            document.documentElement.classList.add('ios-safari');
        }
    }
})();
    
    const header = document.querySelector('.main-header');
    if (header) {
        let lastScrollTop = 0;
        let ticking = false;
        
        const updateHeader = () => {
            const st = window.pageYOffset || document.documentElement.scrollTop;
            if ((st > lastScrollTop) !== (lastScrollTop > st)) {
                header.style.transform = 'translateZ(0)';
                requestAnimationFrame(() => {
                    header.style.transform = '';
                });
            }
            lastScrollTop = st <= 0 ? 0 : st;
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(updateHeader);
                ticking = true;
            }
        }, { passive: true });
    }
}

