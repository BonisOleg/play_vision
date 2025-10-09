/**
 * PLAY VISION SERVICE WORKER
 * Повна реалізація PWA функціоналу згідно MainPlan.mdc та tz.mdc
 */

const CACHE_NAME = 'playvision-v1.3';
const STATIC_CACHE = 'playvision-static-v1.3';
const DYNAMIC_CACHE = 'playvision-dynamic-v1.3';

// Публічні ресурси для кешування (згідно MainPlan.mdc)
const CACHEABLE_PATHS = [
    '/',
    '/about/',
    '/contacts/',
    '/hub/',
    '/events/',
    '/ai/chat/',
    '/pricing/',
    '/static/css/main.css',
    '/static/css/components/cart.css',
    '/static/css/components/ai-chat.css',
    '/static/css/components/pricing.css',
    '/static/js/main.js',
    '/static/js/components/cart.js',
    '/static/js/components/ai-chat.js',
    '/static/js/core/cart-header.js',
    '/static/manifest.json',
    '/static/icons/',
    '/pwa/offline/'
];

// Приватні патерни що НІКОЛИ не кешуються (згідно MainPlan.mdc)
const PRIVATE_PATTERNS = [
    /\/account\//,
    /\/admin\//,
    /\/api\//,
    /\/media\/protected\//,
    /\/payments\//,
    /\/video-security\//,
    /\.m3u8$/,
    /\.ts$/,
    /\/hls\//,
    /\/htmx\//,
    /\/auth\//
];

// Push notification handling (згідно MainPlan.mdc)
self.addEventListener('push', event => {
    console.log('[Service Worker] Push notification received');

    if (!event.data) return;

    const data = event.data.json();
    const options = {
        body: data.body,
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        image: data.image,
        data: data.data,
        actions: [
            {
                action: 'open',
                title: 'Відкрити',
                icon: '/static/icons/action-open.png'
            },
            {
                action: 'close',
                title: 'Закрити',
                icon: '/static/icons/action-close.png'
            }
        ],
        vibrate: [200, 100, 200],
        requireInteraction: data.requireInteraction || false,
        tag: data.tag || 'playvision-notification',
        silent: false,
        renotify: true
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('[Service Worker] Notification clicked');
    event.notification.close();

    const action = event.action;
    const notificationData = event.notification.data;

    if (action === 'open' || !action) {
        const urlToOpen = notificationData?.url || '/';

        event.waitUntil(
            clients.matchAll({ type: 'window' }).then(clientList => {
                // Спробувати знайти існуюче вікно
                for (const client of clientList) {
                    if (client.url.includes(urlToOpen) && 'focus' in client) {
                        return client.focus();
                    }
                }

                // Відкрити нове вікно
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
        );
    }
});

// Install event - кешування критичних ресурсів
self.addEventListener('install', event => {
    console.log('[Service Worker] Installing...');

    event.waitUntil(
        caches.open(STATIC_CACHE).then(cache => {
            console.log('[Service Worker] Pre-caching critical resources');
            return cache.addAll([
                '/',
                '/static/css/main.css',
                '/static/css/utilities.css',
                '/static/css/animations.css',
                '/static/css/accessibility.css',
                '/static/css/components/notifications.css',
                '/static/js/main.js',
                '/static/js/shared/notifications.js',
                '/static/manifest.json',
                '/pwa/offline/',
                '/static/icons/icon-192x192.png'
            ]);
        }).catch(error => {
            console.error('[Service Worker] Pre-caching failed:', error);
        })
    );

    // Активувати одразу
    self.skipWaiting();
});

// Activate event - очищення старих кешів
self.addEventListener('activate', event => {
    console.log('[Service Worker] Activating...');

    event.waitUntil(
        Promise.all([
            // Очистити старі кеші
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE &&
                            cacheName !== DYNAMIC_CACHE &&
                            cacheName !== CACHE_NAME) {
                            console.log('[Service Worker] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),

            // Взяти контроль над всіма вікнами
            self.clients.claim()
        ])
    );
});

// Fetch event - основна логіка кешування
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Пропустити non-GET запити
    if (request.method !== 'GET') {
        return;
    }

    // Пропустити cross-origin запити (окрім CDN)
    if (url.origin !== location.origin && !url.hostname.includes('cdn')) {
        return;
    }

    // НІКОЛИ не кешувати приватний контент (згідно MainPlan.mdc)
    if (PRIVATE_PATTERNS.some(pattern => pattern.test(url.pathname))) {
        event.respondWith(
            fetch(request, {
                cache: 'no-store',
                credentials: 'include'
            })
        );
        return;
    }

    // Стратегії кешування згідно ТЗ
    if (url.pathname.startsWith('/static/')) {
        // Cache-First для статичних ресурсів
        event.respondWith(cacheFirst(request));
    } else if (url.pathname === '/' ||
        url.pathname.startsWith('/about') ||
        url.pathname.startsWith('/contacts') ||
        url.pathname.startsWith('/hub') ||
        url.pathname.startsWith('/events') ||
        url.pathname.startsWith('/ai/chat')) {
        // Network-First для публічного контенту
        event.respondWith(networkFirst(request));
    } else {
        // Network-Only для всього іншого
        event.respondWith(fetch(request));
    }
});

// Cache-First стратегія для статики
async function cacheFirst(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            console.log('[Service Worker] Serving from cache:', request.url);
            return cachedResponse;
        }

        // Завантажити з мережі та закешувати
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;

    } catch (error) {
        console.error('[Service Worker] Cache-first failed for:', request.url, error);
        return new Response('Resource unavailable offline', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Network-First стратегія для динамічного контенту
async function networkFirst(request) {
    try {
        // Спочатку спробувати мережу
        const networkResponse = await fetch(request);

        // Закешувати успішні відповіді
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;

    } catch (error) {
        console.log('[Service Worker] Network failed, trying cache for:', request.url);

        // Fallback до кешу
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        // Для навігаційних запитів показати offline сторінку
        if (request.mode === 'navigate') {
            const offlinePage = await caches.match('/pwa/offline/');
            if (offlinePage) {
                return offlinePage;
            }

            // Fallback offline HTML
            return new Response(createOfflineHTML(), {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'text/html; charset=utf-8' }
            });
        }

        // Generic offline відповідь
        return new Response('Offline', { status: 503 });
    }
}

// Background sync для критичних дій (згідно MainPlan.mdc)
self.addEventListener('sync', event => {
    console.log('[Service Worker] Background sync triggered:', event.tag);

    if (event.tag === 'cart-sync') {
        event.waitUntil(syncCart());
    } else if (event.tag === 'progress-sync') {
        event.waitUntil(syncProgress());
    } else if (event.tag === 'ai-query-sync') {
        event.waitUntil(syncAIQueries());
    }
});

// Синхронізація кошика
async function syncCart() {
    try {
        const pendingActions = await getPendingCartActions();

        for (const action of pendingActions) {
            const response = await fetch(action.url, {
                method: action.method,
                headers: action.headers,
                body: action.body
            });

            if (response.ok) {
                await removePendingAction(action.id);
            }
        }

        console.log('[Service Worker] Cart sync completed');
    } catch (error) {
        console.error('[Service Worker] Cart sync failed:', error);
    }
}

// Синхронізація прогресу навчання
async function syncProgress() {
    try {
        const pendingProgress = await getPendingProgress();

        for (const progress of pendingProgress) {
            const response = await fetch('/api/v1/content/progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': progress.csrfToken
                },
                body: JSON.stringify(progress.data)
            });

            if (response.ok) {
                await removePendingProgress(progress.id);
            }
        }

        console.log('[Service Worker] Progress sync completed');
    } catch (error) {
        console.error('[Service Worker] Progress sync failed:', error);
    }
}

// Синхронізація AI запитів
async function syncAIQueries() {
    try {
        const pendingQueries = await getPendingAIQueries();

        for (const query of pendingQueries) {
            const response = await fetch('/ai/ask/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': query.csrfToken
                },
                body: JSON.stringify({ query: query.text })
            });

            if (response.ok) {
                await removePendingAIQuery(query.id);

                // Спочатку отримуємо JSON дані
                const responseData = await response.json();

                // Повідомити головний thread про відповідь
                const clients = await self.clients.matchAll();
                clients.forEach(client => {
                    client.postMessage({
                        type: 'AI_RESPONSE_SYNCED',
                        queryId: query.id,
                        response: responseData
                    });
                });
            }
        }

        console.log('[Service Worker] AI queries sync completed');
    } catch (error) {
        console.error('[Service Worker] AI queries sync failed:', error);
    }
}

// Message handling для комунікації з main thread
self.addEventListener('message', event => {
    console.log('[Service Worker] Received message:', event.data);

    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data && event.data.type === 'CACHE_UPDATE') {
        event.waitUntil(updateCache(event.data.url));
    }

    if (event.data && event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(clearAllCaches());
    }
});

// Helper functions для LocalStorage (спрощена версія IndexedDB)
async function getPendingCartActions() {
    return JSON.parse(localStorage.getItem('pendingCartActions') || '[]');
}

async function removePendingAction(id) {
    const actions = await getPendingCartActions();
    const filtered = actions.filter(a => a.id !== id);
    localStorage.setItem('pendingCartActions', JSON.stringify(filtered));
}

async function getPendingProgress() {
    return JSON.parse(localStorage.getItem('pendingProgress') || '[]');
}

async function removePendingProgress(id) {
    const progress = await getPendingProgress();
    const filtered = progress.filter(p => p.id !== id);
    localStorage.setItem('pendingProgress', JSON.stringify(filtered));
}

async function getPendingAIQueries() {
    return JSON.parse(localStorage.getItem('pendingAIQueries') || '[]');
}

async function removePendingAIQuery(id) {
    const queries = await getPendingAIQueries();
    const filtered = queries.filter(q => q.id !== id);
    localStorage.setItem('pendingAIQueries', JSON.stringify(filtered));
}

async function updateCache(url) {
    try {
        const response = await fetch(url);
        if (response.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put(url, response);
            console.log('[Service Worker] Cache updated for:', url);
        }
    } catch (error) {
        console.error('[Service Worker] Cache update failed for:', url, error);
    }
}

async function clearAllCaches() {
    const cacheNames = await caches.keys();
    await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
    );
    console.log('[Service Worker] All caches cleared');
}

// Створення offline HTML сторінки
function createOfflineHTML() {
    return `
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Офлайн - Play Vision</title>
        <meta name="theme-color" content="#ff6b35">
        <style>
            :root {
                --color-primary: #ff6b35;
                --color-text: #333;
                --color-bg: #ffffff;
                --spacing-md: 1rem;
                --spacing-lg: 1.5rem;
                --spacing-xl: 2rem;
            }
            
            * { box-sizing: border-box; margin: 0; padding: 0; }
            
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--color-bg);
                color: var(--color-text);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: var(--spacing-md);
            }
            
            .offline-container {
                text-align: center;
                max-width: 500px;
                padding: var(--spacing-xl);
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }
            
            .offline-icon { 
                font-size: 4rem; 
                margin-bottom: var(--spacing-lg);
                display: block;
            }
            
            .offline-title { 
                color: var(--color-primary); 
                margin-bottom: var(--spacing-md);
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .offline-description {
                margin-bottom: var(--spacing-lg);
                line-height: 1.6;
                color: #666;
            }
            
            .offline-actions {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-md);
                align-items: center;
            }
            
            .btn {
                background: var(--color-primary);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 1rem;
                text-decoration: none;
                display: inline-block;
                transition: opacity 0.2s ease;
            }
            
            .btn:hover { opacity: 0.9; }
            
            .btn-outline {
                background: white;
                color: var(--color-primary);
                border: 2px solid var(--color-primary);
            }
            
            @media (max-width: 480px) {
                .offline-container { padding: var(--spacing-lg); }
                .offline-icon { font-size: 3rem; }
                .offline-title { font-size: 1.25rem; }
            }
        </style>
    </head>
    <body>
        <div class="offline-container">
            <div class="offline-icon">📡</div>
            <h1 class="offline-title">Немає з'єднання з інтернетом</h1>
            <p class="offline-description">
                Ця сторінка потребує інтернет з'єднання. Перевірте ваше підключення та спробуйте знову.
            </p>
            <div class="offline-actions">
                <button class="btn" onclick="window.location.reload()">
                    Спробувати знову
                </button>
                <a href="/" class="btn btn-outline">
                    На головну
                </a>
            </div>
        </div>
        
        <script>
            // Автоматична перевірка з'єднання
            window.addEventListener('online', () => {
                console.log('Connection restored');
                window.location.reload();
            });
            
            // Періодична перевірка (кожні 30 секунд)
            setInterval(() => {
                if (navigator.onLine) {
                    fetch('/', { method: 'HEAD', cache: 'no-cache' })
                        .then(() => window.location.reload())
                        .catch(() => console.log('Still offline'));
                }
            }, 30000);
        </script>
    </body>
    </html>
    `;
}