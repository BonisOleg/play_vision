/**
 * FOOTER SUBSCRIBE FORM
 * Обробка форм підписки в десктопному та мобільному футері
 * Оновлено: тільки email, без поля "ім'я"
 */

(function () {
    const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function initSubscribeForms() {
        const desktopForm = document.getElementById('desktopSubscribeForm');
        const mobileForm = document.getElementById('mobileSubscribeForm');

        if (desktopForm) {
            desktopForm.addEventListener('submit', handleSubscribe);
        }

        if (mobileForm) {
            mobileForm.addEventListener('submit', handleSubscribe);
        }
    }

    function handleSubscribe(e) {
        e.preventDefault();

        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const messageContainer = form.querySelector('.form-message');

        // Отримання даних форми
        const formData = new FormData(form);
        const email = formData.get('email')?.trim();

        // Валідація
        if (!email) {
            showMessage(messageContainer, 'error', 'Будь ласка, вкажіть ваш email');
            return;
        }

        if (!EMAIL_REGEX.test(email)) {
            showMessage(messageContainer, 'error', 'Будь ласка, вкажіть коректний email');
            return;
        }

        // Показати стан завантаження
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'відправка...';

        // Відправка на сервер
        const csrfToken = formData.get('csrfmiddlewaretoken');

        fetch('/api/v1/notifications/newsletter/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                name: 'User',
                email: email
            })
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Помилка підписки');
                    });
                }
                return response.json();
            })
            .then(data => {
                showMessage(messageContainer, 'success', data.message || 'Дякуємо за підписку!');
                form.reset();
            })
            .catch(error => {
                console.error('Subscribe error:', error);
                showMessage(messageContainer, 'error', error.message || 'Виникла помилка. Спробуйте пізніше.');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            });
    }

    function showMessage(container, type, text) {
        if (!container) return;

        container.className = 'form-message';
        container.classList.add(type);
        container.textContent = text;

        // Анімація появи
        container.style.display = 'block';

        // Автоматично приховати через 5 секунд
        setTimeout(() => {
            fadeOut(container);
        }, 5000);
    }

    function fadeOut(element) {
        element.style.opacity = '1';

        const fade = setInterval(() => {
            const opacity = parseFloat(element.style.opacity);
            if (opacity > 0) {
                element.style.opacity = (opacity - 0.1).toString();
            } else {
                clearInterval(fade);
                element.style.display = 'none';
                element.className = 'form-message';
            }
        }, 30);
    }

    // Ініціалізація при завантаженні сторінки
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSubscribeForms);
    } else {
        initSubscribeForms();
    }
})();

