document.addEventListener('DOMContentLoaded', function () {
    initializeHTMX();
    initializePWA();
    initializeCart();
    initializeMessages();
    initializeProgressBars();
});

function initializeHTMX() {
    document.body.addEventListener('htmx:configRequest', function (event) {
        const csrfToken = getCookie('csrftoken');
        if (csrfToken) {
            event.detail.headers['X-CSRFToken'] = csrfToken;
        }
    });

    document.body.addEventListener('htmx:responseError', function (event) {
        console.error('HTMX Error:', event.detail);
        showMessage('Помилка завантаження. Спробуйте пізніше.', 'error');
    });

    document.body.addEventListener('htmx:afterSwap', function (event) {
        if (event.detail.target.classList.contains('cart-icon')) {
            const cartCount = event.detail.target.querySelector('.cart-count');
            if (cartCount) {
                cartCount.classList.add('pulse');
                setTimeout(() => cartCount.classList.remove('pulse'), 600);
            }
        }
    });
}

function initializePWA() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => console.log('Service Worker registered'))
            .catch(error => console.error('Service Worker registration failed:', error));
    }

    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;

        const installButton = document.getElementById('pwa-install-button');
        if (installButton) {
            installButton.style.display = 'block';
            installButton.addEventListener('click', () => {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('User accepted PWA install');
                    }
                    deferredPrompt = null;
                });
            });
        }
    });

    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;

    if (isIOS && !isStandalone) {
        setTimeout(() => {
            showIOSInstallPrompt();
        }, 5000);
    }
}

function initializeCart() {
    htmx.trigger(document.querySelector('.cart-icon'), 'load');

    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('add-to-cart')) {
            e.preventDefault();
            const button = e.target;
            const itemType = button.dataset.itemType;
            const itemId = button.dataset.itemId;

            button.disabled = true;
            button.textContent = 'Додаємо...';

            fetch('/api/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    item_type: itemType,
                    item_id: itemId
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showMessage(data.message, 'success');
                        htmx.trigger(document.body, 'cartUpdated');
                    } else {
                        showMessage(data.error || 'Помилка додавання в кошик', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('Помилка з\'єднання', 'error');
                })
                .finally(() => {
                    button.disabled = false;
                    button.textContent = 'В кошик';
                });
        }
    });
}

function initializeMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
}

function showMessage(text, type = 'info') {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();

    const message = document.createElement('div');
    message.className = `message message-${type}`;
    message.innerHTML = `
        ${text}
        <button class="message-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    messagesContainer.appendChild(message);

    setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => message.remove(), 300);
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    document.body.appendChild(container);
    return container;
}

function showIOSInstallPrompt() {
    const existingPrompt = document.getElementById('ios-install-prompt');
    if (existingPrompt) return;

    const prompt = document.createElement('div');
    prompt.id = 'ios-install-prompt';
    prompt.className = 'ios-install-prompt';
    prompt.innerHTML = `
        <div class="ios-install-content">
            <h3>Встановіть Play Vision</h3>
            <p>Додайте додаток на домашній екран для кращого досвіду:</p>
            <ol>
                <li>Натисніть кнопку "Поділитись" <span class="ios-share-icon">⬆</span></li>
                <li>Виберіть "На екран Домівка"</li>
            </ol>
            <button onclick="this.parentElement.parentElement.remove()" class="btn btn-outline">Закрити</button>
        </div>
    `;

    document.body.appendChild(prompt);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function initializeProgressBars() {
    const progressFills = document.querySelectorAll('.progress-fill[data-progress]');
    progressFills.forEach(fill => {
        const progress = fill.getAttribute('data-progress');
        if (progress) {
            fill.style.width = progress + '%';
        }
    });
}

window.PlayVision = {
    showMessage,
    getCookie,
    initializeProgressBars
};
