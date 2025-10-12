/**
 * Scroll Popup Component
 * Vanilla JS implementation without Alpine.js
 */

class ScrollPopup {
    constructor(element) {
        this.element = element;
        this.isShown = false;
        this.loading = false;
        this.init();
    }

    init() {
        console.log('ScrollPopup initialized'); // Debug

        // Перевіряємо чи вже показували
        const shown = localStorage.getItem('popup_shown');
        const dismissed = sessionStorage.getItem('popup_dismissed');

        if (shown || dismissed) {
            console.log('Popup already shown or dismissed'); // Debug
            return;
        }

        // Відстежуємо скрол з debounce
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => this.checkScroll(), 200);
        });

        // Закриття popup - метод 1: прямий listener на кнопку
        const closeBtn = this.element.querySelector('.popup-close');
        const overlay = this.element.querySelector('.popup-overlay');

        console.log('Close button found:', !!closeBtn); // Debug
        console.log('Overlay found:', !!overlay); // Debug

        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                console.log('Close button clicked', e.target); // Debug
                e.preventDefault();
                e.stopPropagation();
                this.close();
            });
        }

        // Метод 2: делегування подій на весь popup
        this.element.addEventListener('click', (e) => {
            const target = e.target;
            const closeButton = target.closest('.popup-close');

            if (closeButton) {
                console.log('Close via delegation'); // Debug
                e.preventDefault();
                e.stopPropagation();
                this.close();
            }
        });

        if (overlay) {
            overlay.addEventListener('click', (e) => {
                // Закриваємо тільки якщо клік по overlay, а не по його дітям
                if (e.target === overlay) {
                    console.log('Overlay clicked'); // Debug
                    e.preventDefault();
                    this.close();
                }
            });
        }

        // Закриття по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isShown) {
                console.log('Escape pressed'); // Debug
                this.close();
            }
        });

        // Форма реєстрації (якщо є)
        const form = this.element.querySelector('#scroll-popup-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleRegister(e));
        }
    }

    checkScroll() {
        if (this.isShown) return;

        const scrolled = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight;

        if (scrolled >= 0.8) {
            this.show();
        }
    }

    show() {
        console.log('Showing popup'); // Debug
        this.isShown = true;
        this.element.classList.remove('is-hidden');
        this.element.classList.add('is-visible');
        document.body.classList.add('modal-open');
        localStorage.setItem('popup_shown', 'true');
    }

    close() {
        console.log('Closing popup'); // Debug
        this.isShown = false;
        this.element.classList.add('is-hidden');
        this.element.classList.remove('is-visible');
        document.body.classList.remove('modal-open');
        sessionStorage.setItem('popup_dismissed', 'true');
    }

    async handleRegister(e) {
        e.preventDefault();

        if (this.loading) return;

        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        this.loading = true;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Завантаження...';

        const formData = new FormData(form);
        const data = {
            email: formData.get('email'),
            password: formData.get('password'),
            source: 'scroll_popup',
            promo_code: 'FIRST10'
        };

        try {
            const response = await fetch('/api/v1/accounts/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                window.location.href = result.redirect_url || '/';
            } else {
                if (window.PlayVision && window.PlayVision.showMessage) {
                    window.PlayVision.showMessage(result.message || 'Помилка реєстрації', 'error');
                } else {
                    alert(result.message || 'Помилка реєстрації');
                }
            }
        } catch (error) {
            console.error('Registration error:', error);
            if (window.PlayVision && window.PlayVision.showMessage) {
                window.PlayVision.showMessage('Помилка мережі. Спробуйте пізніше.', 'error');
            } else {
                alert('Помилка мережі. Спробуйте пізніше.');
            }
        } finally {
            this.loading = false;
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }
}

// Ініціалізація при завантаженні
document.addEventListener('DOMContentLoaded', () => {
    const popup = document.getElementById('scroll-popup');
    if (popup) {
        new ScrollPopup(popup);
    }
});
