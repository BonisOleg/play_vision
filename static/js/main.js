// Play Vision Main JavaScript

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function () {
    // Initialize HTMX
    initializeHTMX();

    // Initialize PWA
    initializePWA();

    // Initialize cart updates
    initializeCart();

    // Initialize message auto-hide
    initializeMessages();

    // Initialize progress bars
    initializeProgressBars();
});

// HTMX Configuration
function initializeHTMX() {
    // Configure HTMX
    document.body.addEventListener('htmx:configRequest', function (event) {
        // Add CSRF token to all requests
        const csrfToken = getCookie('csrftoken');
        if (csrfToken) {
            event.detail.headers['X-CSRFToken'] = csrfToken;
        }
    });

    // Handle HTMX errors
    document.body.addEventListener('htmx:responseError', function (event) {
        console.error('HTMX Error:', event.detail);
        showMessage('Помилка завантаження. Спробуйте пізніше.', 'error');
    });

    // Handle cart updates
    document.body.addEventListener('htmx:afterSwap', function (event) {
        if (event.detail.target.classList.contains('cart-icon')) {
            // Animate cart count update
            const cartCount = event.detail.target.querySelector('.cart-count');
            if (cartCount) {
                cartCount.classList.add('pulse');
                setTimeout(() => cartCount.classList.remove('pulse'), 600);
            }
        }
    });
}

// PWA Installation
function initializePWA() {
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => console.log('Service Worker registered'))
            .catch(error => console.error('Service Worker registration failed:', error));
    }

    // PWA install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;

        // Show install button
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

    // iOS PWA detection
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;

    if (isIOS && !isStandalone) {
        // Show iOS install instructions
        setTimeout(() => {
            showIOSInstallPrompt();
        }, 5000);
    }
}

// Cart functionality
function initializeCart() {
    // Trigger cart count update on page load
    htmx.trigger(document.querySelector('.cart-icon'), 'load');

    // Add to cart buttons
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('add-to-cart')) {
            e.preventDefault();
            const button = e.target;
            const itemType = button.dataset.itemType;
            const itemId = button.dataset.itemId;

            // Add loading state
            button.disabled = true;
            button.textContent = 'Додаємо...';

            // Make AJAX request
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
                        // Trigger cart update
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

// Messages
function initializeMessages() {
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
}

// Show message function
function showMessage(text, type = 'info') {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();

    const message = document.createElement('div');
    message.className = `message message-${type}`;
    message.innerHTML = `
        ${text}
        <button class="message-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    messagesContainer.appendChild(message);

    // Auto-hide after 5 seconds
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

// iOS Install Prompt
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

// Utility: Get cookie value
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

// Progress bars initialization
function initializeProgressBars() {
    // Set width for progress bars based on data-progress attribute
    const progressFills = document.querySelectorAll('.progress-fill[data-progress]');
    progressFills.forEach(fill => {
        const progress = fill.getAttribute('data-progress');
        if (progress) {
            fill.style.width = progress + '%';
        }
    });
}

// Export functions for use in other scripts
window.PlayVision = {
    showMessage,
    getCookie,
    initializeProgressBars
};
