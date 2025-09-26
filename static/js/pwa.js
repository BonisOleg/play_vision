/**
 * PWA FUNCTIONALITY FOR PLAY VISION
 * Повна реалізація PWA згідно MainPlan.mdc та tz.mdc
 */

class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        this.isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
            window.navigator.standalone === true;
        this.init();
    }

    init() {
        // Реєстрація Service Worker
        this.registerServiceWorker();

        // Налаштування install prompt
        this.setupInstallPrompt();

        // iOS специфічна обробка
        if (this.isIOS) {
            this.setupIOSPWA();
        }

        // Push notifications
        this.setupPushNotifications();

        // Offline/Online статуси
        this.setupNetworkHandling();
    }

    async registerServiceWorker() {
        // Service Worker DISABLED until registration issue is fixed
        if (false && 'serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js', {
                    scope: '/'
                });

                console.log('[PWA] Service Worker registered:', registration);

                // Обробка оновлень
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;

                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateAvailable();
                        }
                    });
                });

                // Повідомлення від Service Worker
                navigator.serviceWorker.addEventListener('message', this.handleSWMessage.bind(this));

            } catch (error) {
                console.error('[PWA] Service Worker registration failed:', error);
            }
        }
    }

    setupInstallPrompt() {
        // Стандартний install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('[PWA] Install prompt available');
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        // App installed event
        window.addEventListener('appinstalled', () => {
            console.log('[PWA] App installed successfully');
            this.hideInstallButton();
            this.trackPWAInstall();
        });
    }

    showInstallButton() {
        let installBtn = document.getElementById('pwa-install-button');

        if (!installBtn) {
            installBtn = this.createInstallButton();
            document.body.appendChild(installBtn);
        }

        installBtn.style.display = 'flex';
        installBtn.addEventListener('click', this.promptInstall.bind(this));
    }

    createInstallButton() {
        const button = document.createElement('button');
        button.id = 'pwa-install-button';
        button.className = 'pwa-install-btn';
        button.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7,10 12,15 17,10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Встановити додаток
        `;

        // Стилі кнопки
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: var(--color-primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            display: none;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            font-family: inherit;
        `;

        return button;
    }

    async promptInstall() {
        if (!this.deferredPrompt) return;

        // Показати системний prompt
        this.deferredPrompt.prompt();

        // Дочекатися вибору користувача
        const choiceResult = await this.deferredPrompt.userChoice;

        if (choiceResult.outcome === 'accepted') {
            console.log('[PWA] User accepted the install prompt');
            this.trackPWAInstall();
        } else {
            console.log('[PWA] User dismissed the install prompt');
        }

        this.deferredPrompt = null;
        this.hideInstallButton();
    }

    hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-button');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }

    setupIOSPWA() {
        // iOS PWA Helper згідно MainPlan.mdc
        if (!this.isStandalone) {
            // Показати інструкцію встановлення через 5 секунд
            setTimeout(() => {
                this.showIOSInstallPrompt();
            }, 5000);
        } else {
            // Увімкнути push notifications у standalone режимі
            this.enableIOSPushNotifications();
        }

        // Додати iOS meta теги якщо їх немає
        this.addIOSMetaTags();
    }

    showIOSInstallPrompt() {
        // Перевірити чи вже показували
        if (localStorage.getItem('ios-install-prompt-shown')) {
            return;
        }

        const prompt = document.createElement('div');
        prompt.className = 'ios-install-prompt';
        prompt.innerHTML = `
            <div class="ios-prompt-content">
                <div class="ios-prompt-header">
                    <h3>Встановіть Play Vision</h3>
                    <button class="ios-prompt-close" onclick="this.parentElement.parentElement.parentElement.remove()">&times;</button>
                </div>
                <p>Додайте Play Vision на домашній екран для кращого досвіду:</p>
                <ol class="ios-prompt-steps">
                    <li>
                        Натисніть кнопку "Поділитися" 
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
                            <polyline points="16,6 12,2 8,6"/>
                            <line x1="12" y1="2" x2="12" y2="15"/>
                        </svg>
                    </li>
                    <li>Виберіть "На екран «Домівка»"</li>
                    <li>Натисніть "Додати"</li>
                </ol>
                <button class="ios-prompt-dismiss" onclick="this.parentElement.parentElement.remove(); localStorage.setItem('ios-install-prompt-shown', 'true')">
                    Зрозуміло
                </button>
            </div>
        `;

        // Стилі промпту
        prompt.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            z-index: 10000;
            padding: 20px;
            color: white;
            animation: slideUpFade 0.3s ease;
        `;

        const style = document.createElement('style');
        style.textContent = `
            .ios-prompt-content {
                background: #1c1c1e;
                border-radius: 12px;
                padding: 20px;
                max-width: 400px;
                margin: 0 auto;
            }
            .ios-prompt-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }
            .ios-prompt-header h3 {
                color: white;
                font-size: 1.1rem;
                margin: 0;
            }
            .ios-prompt-close {
                background: none;
                border: none;
                color: #ff6b35;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
            }
            .ios-prompt-steps {
                text-align: left;
                margin: 16px 0;
                padding-left: 20px;
            }
            .ios-prompt-steps li {
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .ios-prompt-dismiss {
                background: #ff6b35;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                cursor: pointer;
                font-size: 1rem;
                width: 100%;
            }
            @keyframes slideUpFade {
                from { transform: translateY(100%); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(prompt);
    }

    addIOSMetaTags() {
        const metaTags = [
            { name: 'apple-mobile-web-app-capable', content: 'yes' },
            { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
            { name: 'apple-mobile-web-app-title', content: 'Play Vision' },
            { name: 'mobile-web-app-capable', content: 'yes' }
        ];

        metaTags.forEach(({ name, content }) => {
            if (!document.querySelector(`meta[name="${name}"]`)) {
                const meta = document.createElement('meta');
                meta.name = name;
                meta.content = content;
                document.head.appendChild(meta);
            }
        });

        // Apple touch icons
        const touchIconSizes = [57, 60, 72, 76, 114, 120, 144, 152, 180];
        touchIconSizes.forEach(size => {
            if (!document.querySelector(`link[rel="apple-touch-icon"][sizes="${size}x${size}"]`)) {
                const link = document.createElement('link');
                link.rel = 'apple-touch-icon';
                link.sizes = `${size}x${size}`;
                link.href = `/static/icons/apple-touch-icon-${size}x${size}.png`;
                document.head.appendChild(link);
            }
        });

        // Splash screens for iOS
        const splashScreens = [
            { media: '(device-width: 390px) and (device-height: 844px) and (-webkit-device-pixel-ratio: 3)', href: '/static/splash/iphone12.png' },
            { media: '(device-width: 428px) and (device-height: 926px) and (-webkit-device-pixel-ratio: 3)', href: '/static/splash/iphone12-pro-max.png' },
            { media: '(device-width: 768px) and (device-height: 1024px) and (-webkit-device-pixel-ratio: 2)', href: '/static/splash/ipad.png' }
        ];

        splashScreens.forEach(({ media, href }) => {
            const link = document.createElement('link');
            link.rel = 'apple-touch-startup-image';
            link.media = media;
            link.href = href;
            document.head.appendChild(link);
        });
    }

    enableIOSPushNotifications() {
        // Push працює тільки в standalone режимі на iOS 16.4+
        if ('Notification' in window && 'serviceWorker' in navigator) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.subscribeToPush();
                }
            });
        }
    }

    async setupPushNotifications() {
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            console.log('[PWA] Push notifications not supported');
            return;
        }

        // Запитати дозвіл
        const permission = await Notification.requestPermission();

        if (permission === 'granted') {
            await this.subscribeToPush();
        }
    }

    async subscribeToPush() {
        try {
            const registration = await navigator.serviceWorker.ready;

            // Спробувати отримати VAPID ключ з сервера
            let vapidPublicKey;
            try {
                const vapidResponse = await fetch('/api/v1/notifications/vapid-key/');
                const vapidData = await vapidResponse.json();
                vapidPublicKey = vapidData.public_key;
            } catch (e) {
                console.warn('[PWA] Could not get VAPID key from server, using default');
                // Mock ключ для тестування (треба замінити в production)
                vapidPublicKey = 'BEl62iUYgUivxIkv69yViEuiBIa40HI80NqIXyv0Q0UgbC4JgvKxTpppDTyHJY6eY8g8UmGm_7d4BqVHlTKJf5A';
            }

            if (!vapidPublicKey) {
                throw new Error('VAPID public key not available');
            }

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(vapidPublicKey)
            });

            // Відправити підписку на сервер
            const response = await fetch('/api/v1/notifications/push/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    subscription: subscription.toJSON()
                })
            });

            const result = await response.json();

            if (result.success) {
                console.log('[PWA] Push subscription successful');
                this.showSuccessMessage('Push-сповіщення увімкнені!');

                // Зберегти статус підписки
                localStorage.setItem('push_subscribed', 'true');
            } else {
                throw new Error(result.error || 'Subscription failed');
            }

        } catch (error) {
            console.error('[PWA] Push subscription failed:', error);
            this.showErrorMessage('Не вдалося увімкнути сповіщення');
        }
    }

    setupNetworkHandling() {
        // Online/Offline статуси
        window.addEventListener('online', () => {
            console.log('[PWA] Connection restored');
            this.showNetworkStatus('Підключення відновлено', 'success');
            this.syncPendingData();
        });

        window.addEventListener('offline', () => {
            console.log('[PWA] Connection lost');
            this.showNetworkStatus('Немає підключення до інтернету', 'warning');
        });
    }

    async syncPendingData() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            const registration = await navigator.serviceWorker.ready;

            // Синхронізувати різні типи даних
            await registration.sync.register('cart-sync');
            await registration.sync.register('progress-sync');
            await registration.sync.register('ai-query-sync');
        }
    }

    showNetworkStatus(message, type) {
        const existing = document.querySelector('.network-status');
        if (existing) existing.remove();

        const status = document.createElement('div');
        status.className = `network-status network-status--${type}`;
        status.textContent = message;

        status.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'success' ? '#4caf50' : '#ff9800'};
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            z-index: 10000;
            font-size: 14px;
            animation: slideDown 0.3s ease;
        `;

        document.body.appendChild(status);

        // Автовидалення
        setTimeout(() => status.remove(), 3000);
    }

    showUpdateAvailable() {
        const updatePrompt = document.createElement('div');
        updatePrompt.className = 'pwa-update-prompt';
        updatePrompt.innerHTML = `
            <div class="update-content">
                <h4>Доступне оновлення</h4>
                <p>Нова версія Play Vision готова до встановлення</p>
                <div class="update-actions">
                    <button class="update-btn" onclick="this.parentElement.parentElement.parentElement.parentElement.updateAndReload()">
                        Оновити
                    </button>
                    <button class="update-dismiss" onclick="this.parentElement.parentElement.parentElement.parentElement.remove()">
                        Пізніше
                    </button>
                </div>
            </div>
        `;

        updatePrompt.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            max-width: 300px;
            border: 2px solid var(--color-primary);
        `;

        updatePrompt.updateAndReload = () => {
            navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
            window.location.reload();
        };

        document.body.appendChild(updatePrompt);
    }

    handleSWMessage(event) {
        const { data } = event;

        switch (data.type) {
            case 'AI_RESPONSE_SYNCED':
                // Оновити AI чат з синхронізованою відповіддю
                if (window.aiChat) {
                    window.aiChat.handleSyncedResponse(data.queryId, data.response);
                }
                break;

            case 'CART_SYNCED':
                // Оновити UI кошика
                if (window.cartHeader) {
                    window.cartHeader.updateCounter(data.cartCount);
                }
                break;
        }
    }

    trackPWAInstall() {
        // Google Analytics event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'pwa_install', {
                event_category: 'PWA',
                event_label: 'App Installed'
            });
        }

        // Meta Pixel event
        if (typeof fbq !== 'undefined') {
            fbq('track', 'CompleteRegistration', {
                content_name: 'PWA Install',
                status: 'completed'
            });
        }
    }

    // Utility methods
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    showSuccessMessage(message) {
        this.showToast(message, 'success');
    }

    showErrorMessage(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        const existing = document.querySelectorAll('.pwa-toast');
        existing.forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `pwa-toast pwa-toast--${type}`;
        toast.innerHTML = `
            <div class="pwa-toast-content">
                <span>${message}</span>
                <button class="pwa-toast-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;

        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            z-index: 10000;
            font-size: 14px;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(toast);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    // Public API для інших модулів
    async storePendingCartAction(action) {
        const pending = JSON.parse(localStorage.getItem('pendingCartActions') || '[]');
        pending.push({
            id: Date.now(),
            timestamp: Date.now(),
            ...action
        });
        localStorage.setItem('pendingCartActions', JSON.stringify(pending));
    }

    async storePendingAIQuery(query) {
        const pending = JSON.parse(localStorage.getItem('pendingAIQueries') || '[]');
        pending.push({
            id: Date.now(),
            timestamp: Date.now(),
            text: query,
            csrfToken: this.getCSRFToken()
        });
        localStorage.setItem('pendingAIQueries', JSON.stringify(pending));
    }

    isOnline() {
        return navigator.onLine;
    }

    isPWAInstalled() {
        return this.isStandalone;
    }

    getInstallStatus() {
        return {
            canInstall: !!this.deferredPrompt,
            isInstalled: this.isStandalone,
            isIOS: this.isIOS,
            supportsServiceWorker: 'serviceWorker' in navigator,
            supportsPushNotifications: 'Notification' in window && 'PushManager' in window
        };
    }
}

// CSS для PWA компонентів
const PWA_STYLES = `
    .pwa-install-btn:hover {
        background: #e55a2b;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }
    
    .update-content {
        text-align: center;
    }
    
    .update-content h4 {
        color: var(--color-primary);
        margin-bottom: 8px;
        font-size: 1rem;
    }
    
    .update-content p {
        color: #666;
        margin-bottom: 16px;
        font-size: 0.875rem;
        line-height: 1.4;
    }
    
    .update-actions {
        display: flex;
        gap: 8px;
    }
    
    .update-btn, .update-dismiss {
        flex: 1;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .update-btn {
        background: var(--color-primary);
        color: white;
    }
    
    .update-dismiss {
        background: #f5f5f5;
        color: #666;
    }
    
    .pwa-toast-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }
    
    .pwa-toast-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.8;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .pwa-toast-close:hover {
        opacity: 1;
    }
    
    @keyframes slideDown {
        from { transform: translate(-50%, -100%); opacity: 0; }
        to { transform: translate(-50%, 0); opacity: 1; }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;

// Додати стилі до сторінки
const style = document.createElement('style');
style.textContent = PWA_STYLES;
document.head.appendChild(style);

// Ініціалізація PWA
document.addEventListener('DOMContentLoaded', () => {
    window.pwaManager = new PWAManager();
    console.log('[PWA] PWA Manager initialized');
});

// Експорт для використання в інших модулях
window.PWAManager = PWAManager;
