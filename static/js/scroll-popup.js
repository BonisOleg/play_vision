/**
 * Scroll Popup Component - SIMPLIFIED VERSION
 */

class ScrollPopup {
    constructor(element) {
        this.element = element;
        this.isShown = false;
        this.loading = false;
        this.setupCloseHandlers();
        this.checkIfShouldShow();
    }

    setupCloseHandlers() {
        // АГРЕСИВНЕ закриття - всі можливі варіанти
        const self = this;

        // 1. Клік на будь-що з класом popup-close
        document.addEventListener('click', function (e) {
            if (e.target.closest('.popup-close')) {
                console.log('CLOSE: button clicked');
                e.preventDefault();
                e.stopPropagation();
                self.forceClose();
                return false;
            }
        }, true);

        // 2. Клік на overlay
        const overlay = this.element.querySelector('.popup-overlay');
        if (overlay) {
            overlay.addEventListener('click', function (e) {
                if (e.target === overlay) {
                    console.log('CLOSE: overlay clicked');
                    self.forceClose();
                }
            });
        }

        // 3. Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && self.isShown) {
                console.log('CLOSE: escape pressed');
                self.forceClose();
            }
        });

        // 4. Форма
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

        // Скрол
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
        console.log('SHOW popup');
        this.isShown = true;
        this.element.classList.remove('is-hidden');
        this.element.classList.add('is-visible');
        document.body.classList.add('modal-open');
        localStorage.setItem('popup_shown', 'true');
    }

    forceClose() {
        console.log('FORCE CLOSE popup');
        this.isShown = false;

        // Видаляємо ВСІ класи і ховаємо
        this.element.classList.add('is-hidden');
        this.element.classList.remove('is-visible');
        this.element.style.display = 'none'; // Форсуємо приховування

        document.body.classList.remove('modal-open');
        document.body.style.overflow = ''; // Очищуємо

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
