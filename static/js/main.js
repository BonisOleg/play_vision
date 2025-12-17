// Видалити ВСІ текстові вузли перед header
function removeMetaDescriptionText() {
    const body = document.body;
    if (!body) return;
    
    const header = document.querySelector('header.main-header');
    if (!header) return;
    
    // Видаляємо всі текстові вузли перед header
    let node = body.firstChild;
    while (node && node !== header) {
        if (node.nodeType === 3) {
            // Це текстовий вузол - видаляємо його незалежно від вмісту
            const nextSibling = node.nextSibling;
            body.removeChild(node);
            node = nextSibling;
            continue;
        }
        node = node.nextSibling;
    }
}

// Викликаємо одразу, якщо DOM вже завантажений
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', removeMetaDescriptionText);
} else {
    // DOM вже завантажений
    removeMetaDescriptionText();
}

document.addEventListener('DOMContentLoaded', function () {
    // Видалити текстовий вузол перед header - на випадок, якщо він з'явився пізніше
    removeMetaDescriptionText();
    
    // Відстежуємо зміни в DOM для видалення тексту, який може з'явитися пізніше
    const observer = new MutationObserver(function(mutations) {
        removeMetaDescriptionText();
    });
    
    // Спостерігаємо за змінами в body
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: false
        });
    }
    
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
        // Видалити текст перед header після HTMX завантаження
        removeMetaDescriptionText();
    });

    // Захист навігації від HTMX
    document.body.addEventListener('htmx:beforeSwap', function (event) {
        if (event.detail.target.closest('.header') ||
            event.detail.target.classList.contains('mobile-menu')) {
            event.preventDefault();
            return false;
        }
    });
}

function initializePWA() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => console.log('Service Worker registered'))
            .catch(error => console.error('Service Worker registration failed:', error));
    }

    // PWA Install - DISABLED per client request
    // let deferredPrompt;
    // window.addEventListener('beforeinstallprompt', (e) => {
    //     e.preventDefault();
    //     deferredPrompt = e;
    // });
}

function initializeCart() {
    // Ініціалізуємо корзину тільки якщо вона існує
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        htmx.trigger(cartIcon, 'load');
    }

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
                        // Тригеримо тільки корзину, не весь body
                        htmx.trigger(document.querySelector('.cart-icon'), 'cartUpdated');
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
        // Додаємо обробник кнопки закриття
        const closeBtn = message.querySelector('.message-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                message.classList.add('message-fade-out');
                setTimeout(() => message.remove(), 300);
            });
        }

        // Автоматичне закриття через 5 секунд
        setTimeout(() => {
            if (message.parentElement) {
                message.classList.add('message-fade-out');
                setTimeout(() => {
                    if (message.parentElement) {
                        message.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

function showMessage(text, type = 'info') {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();

    const message = document.createElement('div');
    message.className = `message message-${type}`;

    const textNode = document.createTextNode(text);
    message.appendChild(textNode);

    const closeBtn = document.createElement('button');
    closeBtn.className = 'message-close';
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', () => {
        message.classList.add('message-fade-out');
        setTimeout(() => message.remove(), 300);
    });
    message.appendChild(closeBtn);

    messagesContainer.appendChild(message);

    setTimeout(() => {
        if (message.parentElement) {
            message.classList.add('message-fade-out');
            setTimeout(() => {
                if (message.parentElement) {
                    message.remove();
                }
            }, 300);
        }
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    document.body.appendChild(container);
    return container;
}

// PWA Install Prompt - DISABLED per client request
// function showIOSInstallPrompt() {
//     const existingPrompt = document.getElementById('ios-install-prompt');
//     if (existingPrompt) return;
//     const prompt = document.createElement('div');
//     prompt.id = 'ios-install-prompt';
//     document.body.appendChild(prompt);
// }

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
    const progressFills = document.querySelectorAll('.progress-fill');
    progressFills.forEach(fill => {
        const progress = fill.dataset.progress || fill.textContent.trim();
        if (progress) {
            const value = parseFloat(progress);
            if (!isNaN(value) && value >= 0 && value <= 100) {
                fill.style.setProperty('--progress-width', value + '%');
            }
        }
    });
}


window.PlayVision = {
    showMessage,
    getCookie,
    initializeProgressBars
};
