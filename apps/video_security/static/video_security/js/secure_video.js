// Secure Video Player - Play Vision
// Безконфліктний модуль для роботи з захищеними відео

(function () {
    'use strict';

    // Namespace для уникнення конфліктів
    window.SecureVideo = window.SecureVideo || {};

    const SecureVideo = {
        // Конфігурація
        config: {
            apiEndpoint: '/video-security/api/secure-url/',
            retryAttempts: 3,
            retryDelay: 1000
        },

        // Ініціалізація при завантаженні DOM
        init: function () {
            document.addEventListener('DOMContentLoaded', function () {
                SecureVideo.initializeSecureContainers();
                SecureVideo.setupGlobalSecurity();
            });
        },

        // Ініціалізація всіх контейнерів з захищеним відео
        initializeSecureContainers: function () {
            const containers = document.querySelectorAll('.secure-video-container');

            containers.forEach(container => {
                const materialId = container.dataset.materialId;
                const hasAccess = container.dataset.hasAccess === 'true';

                if (hasAccess && materialId) {
                    SecureVideo.loadSecureVideo(container, materialId);
                } else {
                    SecureVideo.setupPreviewMode(container);
                }
            });
        },

        // Завантаження захищеного відео
        loadSecureVideo: function (container, materialId) {
            const video = container.querySelector('.secure-video');
            if (!video) return;

            // Показуємо індикатор завантаження
            SecureVideo.showLoadingIndicator(container);

            // Отримуємо захищений URL
            SecureVideo.fetchSecureUrl(materialId)
                .then(data => {
                    if (data.video_url) {
                        SecureVideo.setupVideoPlayer(video, data.video_url, materialId);
                        SecureVideo.hideLoadingIndicator(container);
                    } else {
                        SecureVideo.showVideoError(container, 'URL не отримано');
                    }
                })
                .catch(error => {
                    console.error('Secure video loading error:', error);
                    SecureVideo.showVideoError(container, 'Помилка завантаження відео');
                });
        },

        // API запит для отримання захищеного URL
        fetchSecureUrl: function (materialId, attempt = 1) {
            return fetch(`${SecureVideo.config.apiEndpoint}${materialId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': SecureVideo.getCsrfToken(),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 429 && attempt < SecureVideo.config.retryAttempts) {
                            // Retry з експоненційною затримкою при rate limiting
                            const delay = SecureVideo.config.retryDelay * Math.pow(2, attempt - 1);
                            return new Promise(resolve => {
                                setTimeout(() => {
                                    resolve(SecureVideo.fetchSecureUrl(materialId, attempt + 1));
                                }, delay);
                            });
                        }
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                });
        },

        // Налаштування відео плеєра з захистом
        setupVideoPlayer: function (video, videoUrl, materialId) {
            // Встановлюємо URL
            video.src = videoUrl;

            // Додаємо захист
            SecureVideo.addVideoSecurity(video, materialId);

            // Event listeners для контролю доступу
            video.addEventListener('loadstart', () => {
                SecureVideo.logVideoEvent(materialId, 'load_started');
            });

            video.addEventListener('play', () => {
                SecureVideo.logVideoEvent(materialId, 'play_started');
            });

            video.addEventListener('ended', () => {
                SecureVideo.logVideoEvent(materialId, 'play_completed');
            });

            video.addEventListener('error', (e) => {
                SecureVideo.logVideoEvent(materialId, 'playback_error', {
                    error: e.target.error
                });
            });

            // Показуємо відео
            video.style.display = 'block';
        },

        // Додавання захисту до відео
        addVideoSecurity: function (video, materialId) {
            // Захист від правого кліку
            video.addEventListener('contextmenu', e => {
                e.preventDefault();
                SecureVideo.logSecurityEvent(materialId, 'right_click_blocked');
                return false;
            });

            // Захист від drag & drop
            video.addEventListener('dragstart', e => {
                e.preventDefault();
                SecureVideo.logSecurityEvent(materialId, 'drag_blocked');
                return false;
            });

            // Захист від вибору
            video.addEventListener('selectstart', e => {
                e.preventDefault();
                return false;
            });

            // Захист від деяких клавіш
            video.addEventListener('keydown', e => {
                const blockedKeys = ['F12', 'F1'];
                const blockedCombos = [
                    { ctrl: true, shift: true, key: 'I' }, // DevTools
                    { ctrl: true, shift: true, key: 'J' }, // Console
                    { ctrl: true, key: 'U' }, // View Source
                    { ctrl: true, key: 'S' }, // Save
                ];

                if (blockedKeys.includes(e.key)) {
                    e.preventDefault();
                    SecureVideo.logSecurityEvent(materialId, 'key_blocked', { key: e.key });
                    return false;
                }

                for (let combo of blockedCombos) {
                    if (combo.ctrl === e.ctrlKey &&
                        combo.shift === (combo.shift || false) === e.shiftKey &&
                        combo.key === e.key) {
                        e.preventDefault();
                        SecureVideo.logSecurityEvent(materialId, 'combo_blocked', combo);
                        return false;
                    }
                }
            });

            // Додаємо watermark
            SecureVideo.addWatermark(video.parentElement, materialId);

            // Захист від screenshots (обмежений)
            video.addEventListener('focus', () => {
                if (document.visibilityState === 'hidden') {
                    video.pause();
                    SecureVideo.logSecurityEvent(materialId, 'tab_hidden_pause');
                }
            });

            // Блокування Print Screen
            document.addEventListener('keyup', e => {
                if (e.key === 'PrintScreen') {
                    SecureVideo.logSecurityEvent(materialId, 'print_screen_attempt');
                    SecureVideo.showSecurityWarning('Знімки екрану заборонені');
                }
            });
        },

        // Додавання watermark
        addWatermark: function (container, materialId) {
            const userEmail = document.body.dataset.userEmail || 'User';
            const timestamp = new Date().toLocaleString('uk-UA');

            const watermark = document.createElement('div');
            watermark.className = 'secure-video-watermark';
            watermark.innerHTML = `${userEmail} • ${timestamp}`;

            // Стилі watermark
            watermark.style.cssText = `
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-family: monospace;
                pointer-events: none;
                z-index: 1000;
                user-select: none;
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
            `;

            container.style.position = 'relative';
            container.appendChild(watermark);

            // Рухомий watermark (ускладнює видалення)
            SecureVideo.animateWatermark(watermark);
        },

        // Анімація watermark
        animateWatermark: function (watermark) {
            let x = 20, y = 20;
            let dx = 0.5, dy = 0.3;

            setInterval(() => {
                x += dx;
                y += dy;

                // Відскок від країв
                if (x > 200 || x < 20) dx = -dx;
                if (y > 100 || y < 20) dy = -dy;

                watermark.style.top = y + 'px';
                watermark.style.right = x + 'px';
            }, 100);
        },

        // Режим превью
        setupPreviewMode: function (container) {
            const video = container.querySelector('.preview-video');
            if (!video) return;

            const previewSeconds = parseInt(video.dataset.previewSeconds) || 20;

            video.addEventListener('timeupdate', function () {
                if (video.currentTime >= previewSeconds) {
                    video.pause();
                    SecureVideo.showUpgradeModal(container);
                }
            });

            // Додаємо превью watermark
            SecureVideo.addPreviewWatermark(container, previewSeconds);
        },

        // Превью watermark
        addPreviewWatermark: function (container, seconds) {
            const watermark = document.createElement('div');
            watermark.className = 'preview-watermark';
            watermark.innerHTML = `ПРЕВЬЮ ${seconds}с • Потрібна підписка`;

            watermark.style.cssText = `
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(255, 107, 53, 0.9);
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                pointer-events: none;
                z-index: 1000;
            `;

            container.style.position = 'relative';
            container.appendChild(watermark);
        },

        // Модальне вікно для upgrade
        showUpgradeModal: function (container) {
            const modal = document.createElement('div');
            modal.className = 'secure-video-modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <h3>Превью закінчилося</h3>
                    <p>Оформи підписку для повного доступу до всіх курсів</p>
                    <div class="modal-buttons">
                        <a href="/pricing/" class="btn btn-primary">Вибрати план</a>
                        <button class="btn btn-outline close-modal">Закрити</button>
                    </div>
                </div>
            `;

            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            `;

            modal.querySelector('.modal-content').style.cssText = `
                background: white;
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                max-width: 400px;
                margin: 20px;
            `;

            modal.querySelector('.close-modal').addEventListener('click', () => {
                modal.remove();
            });

            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });

            document.body.appendChild(modal);
        },

        // Глобальний захист
        setupGlobalSecurity: function () {
            // Виявлення DevTools
            let devtools = {
                open: false,
                orientation: null
            };

            const threshold = 160;

            setInterval(() => {
                if (window.outerHeight - window.innerHeight > threshold ||
                    window.outerWidth - window.innerWidth > threshold) {
                    if (!devtools.open) {
                        devtools.open = true;
                        SecureVideo.handleDevToolsDetected();
                    }
                } else {
                    devtools.open = false;
                }
            }, 500);

            // Захист від copy/paste
            document.addEventListener('copy', e => {
                if (e.target.tagName === 'VIDEO') {
                    e.preventDefault();
                    SecureVideo.showSecurityWarning('Копіювання відео заборонене');
                }
            });
        },

        // Обробка виявлення DevTools
        handleDevToolsDetected: function () {
            console.clear();
            console.log('%cЗУПИНІТЬСЯ!', 'color: red; font-size: 50px; font-weight: bold;');
            console.log('%cЦе функція браузера призначена для розробників. Якщо хтось попросив вас скопіювати та вставити сюди щось, це шахрайство.', 'color: red; font-size: 16px;');

            // Логування
            SecureVideo.logSecurityEvent('global', 'devtools_detected');
        },

        // Попередження про безпеку
        showSecurityWarning: function (message) {
            // Використовуємо існуючу функцію якщо доступна
            if (window.PlayVision && window.PlayVision.showMessage) {
                window.PlayVision.showMessage(message, 'warning');
            } else {
                alert(message);
            }
        },

        // Індикатор завантаження
        showLoadingIndicator: function (container) {
            const indicator = document.createElement('div');
            indicator.className = 'secure-video-loading';
            indicator.innerHTML = `
                <div class="loading-spinner"></div>
                <p>Завантаження захищеного відео...</p>
            `;

            indicator.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                z-index: 100;
            `;

            container.appendChild(indicator);
        },

        hideLoadingIndicator: function (container) {
            const indicator = container.querySelector('.secure-video-loading');
            if (indicator) {
                indicator.remove();
            }
        },

        // Показ помилки відео
        showVideoError: function (container, message) {
            SecureVideo.hideLoadingIndicator(container);

            const errorDiv = document.createElement('div');
            errorDiv.className = 'secure-video-error';
            errorDiv.innerHTML = `
                <p class="error-message">❌ ${message}</p>
                <button class="btn btn-outline retry-button">Спробувати знову</button>
            `;

            errorDiv.style.cssText = `
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            `;

            const retryButton = errorDiv.querySelector('.retry-button');
            retryButton.addEventListener('click', () => {
                errorDiv.remove();
                const materialId = container.dataset.materialId;
                if (materialId) {
                    SecureVideo.loadSecureVideo(container, materialId);
                }
            });

            container.appendChild(errorDiv);
        },

        // Логування подій відео
        logVideoEvent: function (materialId, eventType, data = {}) {
            // Відправляємо аналітику (якщо потрібно)
            console.log(`Video Event [${materialId}]:`, eventType, data);
        },

        // Логування подій безпеки
        logSecurityEvent: function (materialId, eventType, data = {}) {
            console.warn(`Security Event [${materialId}]:`, eventType, data);

            // Можна відправити на сервер для аналізу
            try {
                fetch('/video-security/log-security-event/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': SecureVideo.getCsrfToken()
                    },
                    body: JSON.stringify({
                        material_id: materialId,
                        event_type: eventType,
                        data: data,
                        timestamp: Date.now()
                    })
                }).catch(err => {
                    // Тихо ігноруємо помилки логування
                });
            } catch (e) {
                // Тихо ігноруємо помилки
            }
        },

        // Отримання CSRF токену
        getCsrfToken: function () {
            // Спочатку пробуємо існуючу функцію
            if (window.PlayVision && window.PlayVision.getCookie) {
                return window.PlayVision.getCookie('csrftoken');
            }

            // Fallback реалізація
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    return decodeURIComponent(value);
                }
            }
            return '';
        }
    };

    // Автоматична ініціалізація
    SecureVideo.init();

    // Експорт в глобальний namespace
    window.SecureVideo = SecureVideo;

})();
