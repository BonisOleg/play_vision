/**
 * FOOTER NEWSLETTER FORM
 * Обробка форми підписки на новини
 * БЕЗ inline JS (згідно правил §0.2)
 */

(function() {
    const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function initNewsletterForm() {
        const form = document.getElementById('newsletterForm');
        if (!form) return;

        form.addEventListener('submit', handleSubmit);
    }

    function handleSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const submitButton = form.querySelector('.newsletter-button');
        const messageContainer = form.querySelector('.form-message');
        const emailInput = form.querySelector('input[name="email"]');

        const formData = new FormData(form);
        const email = formData.get('email')?.trim();

        if (!email) {
            showMessage(messageContainer, 'error', 'Будь ласка, вкажіть ваш email');
            return;
        }

        if (!EMAIL_REGEX.test(email)) {
            showMessage(messageContainer, 'error', 'Будь ласка, вкажіть коректний email');
            return;
        }

        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'відправка...';

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
            console.error('Newsletter subscription error:', error);
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
                element.style.opacity = '';
            }
        }, 30);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNewsletterForm);
    } else {
        initNewsletterForm();
    }
})();

