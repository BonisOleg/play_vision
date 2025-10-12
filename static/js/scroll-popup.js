/**
 * Scroll Popup - ULTRA SIMPLE VERSION
 * Глобальна функція для гарантованого закриття
 */

// Глобальна функція закриття
window.closeScrollPopup = function () {
    console.log('🔴 CLOSING POPUP');
    const popup = document.getElementById('scroll-popup');
    if (popup) {
        popup.classList.add('is-hidden');
        popup.classList.remove('is-visible');
        popup.style.display = 'none';
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        sessionStorage.setItem('popup_dismissed', 'true');
    }
};

class ScrollPopup {
    constructor(element) {
        this.element = element;
        this.isShown = false;
        this.setupHandlers();
        this.checkIfShouldShow();
    }

    setupHandlers() {
        const self = this;

        // Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && self.isShown) {
                window.closeScrollPopup();
            }
        });

        // Overlay click
        const overlay = this.element.querySelector('.popup-overlay');
        if (overlay) {
            overlay.addEventListener('click', function (e) {
                if (e.target === overlay) {
                    window.closeScrollPopup();
                }
            });
        }

        // Form submit
        const form = this.element.querySelector('#scroll-popup-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleRegister(e));
        }
    }

    checkIfShouldShow() {
        const shown = localStorage.getItem('popup_shown');
        const dismissed = sessionStorage.getItem('popup_dismissed');

        if (shown || dismissed) {
            return;
        }

        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                if (!this.isShown) {
                    const scrolled = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight;
                    if (scrolled >= 0.8) {
                        this.show();
                    }
                }
            }, 200);
        });
    }

    show() {
        console.log('🟢 SHOWING POPUP');
        this.isShown = true;
        this.element.classList.remove('is-hidden');
        this.element.classList.add('is-visible');
        document.body.classList.add('modal-open');
        localStorage.setItem('popup_shown', 'true');
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

// Ініціалізація
document.addEventListener('DOMContentLoaded', () => {
    const popup = document.getElementById('scroll-popup');
    if (popup) {
        window.scrollPopupInstance = new ScrollPopup(popup);
    }
});
