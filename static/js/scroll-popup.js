/**
 * Scroll Popup Component
 * Показує popup при скролі до кінця сторінки
 */
function scrollPopup() {
    return {
        showPopup: false,
        loading: false,
        formData: {
            email: '',
            password: ''
        },

        init() {
            // Перевірити чи вже показували
            const shown = localStorage.getItem('popup_shown');
            const dismissed = sessionStorage.getItem('popup_dismissed');

            if (shown || dismissed) {
                return;
            }

            // Відстежувати скрол з debounce
            let scrollTimeout;
            window.addEventListener('scroll', () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => this.checkScroll(), 200);
            });
        },

        checkScroll() {
            const scrolled = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight;

            if (scrolled >= 0.8 && !this.showPopup) {
                this.openPopup();
            }
        },

        openPopup() {
            this.showPopup = true;
            document.body.style.overflow = 'hidden';
            localStorage.setItem('popup_shown', 'true');
        },

        closePopup() {
            this.showPopup = false;
            document.body.style.overflow = '';
            sessionStorage.setItem('popup_dismissed', 'true');
        },

        async handleRegister() {
            if (this.loading) return;

            this.loading = true;

            try {
                const response = await fetch('/api/v1/accounts/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({
                        email: this.formData.email,
                        password: this.formData.password,
                        source: 'scroll_popup',
                        promo_code: 'FIRST10'
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.href = data.redirect_url || '/';
                } else {
                    alert(data.message || 'Помилка реєстрації');
                }
            } catch (error) {
                console.error('Registration error:', error);
                alert('Помилка мережі. Спробуйте пізніше.');
            } finally {
                this.loading = false;
            }
        },

        getCsrfToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                document.querySelector('meta[name="csrf-token"]')?.content || '';
        }
    };
}

