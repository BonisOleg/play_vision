/**
 * API Utils - Безпечні утиліти для роботи з API
 * Обробляє помилки мережі та надає fallback механізми
 */
class APIUtils {
    constructor() {
        this.defaultTimeout = 10000; // 10 секунд
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 секунда
    }

    /**
     * Безпечний fetch з автоматичною обробкою помилок
     */
    static async safeFetch(url, options = {}) {
        const instance = new APIUtils();
        return instance.fetch(url, options);
    }

    /**
     * Основний метод для виконання HTTP запитів
     */
    async fetch(url, options = {}) {
        if (!url || typeof url !== 'string') {
            throw new Error('URL має бути валідним рядком');
        }

        const config = {
            timeout: options.timeout || this.defaultTimeout,
            retries: options.retries !== undefined ? options.retries : this.retryAttempts,
            ...options
        };

        // Видаляємо кастомні опції перед передачею в fetch
        const fetchOptions = { ...options };
        delete fetchOptions.timeout;
        delete fetchOptions.retries;

        // Додаємо CSRF токен якщо доступний
        if (!fetchOptions.headers) {
            fetchOptions.headers = {};
        }

        const csrfToken = this.getCSRFToken();
        if (csrfToken && (fetchOptions.method === 'POST' || fetchOptions.method === 'PUT' || fetchOptions.method === 'DELETE')) {
            fetchOptions.headers['X-CSRFToken'] = csrfToken;
        }

        // Встановлюємо Content-Type для JSON запитів
        if (fetchOptions.body && typeof fetchOptions.body === 'object') {
            fetchOptions.headers['Content-Type'] = 'application/json';
            fetchOptions.body = JSON.stringify(fetchOptions.body);
        }

        let lastError;

        for (let attempt = 0; attempt <= config.retries; attempt++) {
            try {
                const response = await this.fetchWithTimeout(url, fetchOptions, config.timeout);

                if (!response.ok) {
                    const error = await this.createErrorFromResponse(response);

                    // Не повторюємо спроби для клієнтських помилок (4xx)
                    if (response.status >= 400 && response.status < 500) {
                        throw error;
                    }

                    lastError = error;

                    // Повторюємо спробу тільки для серверних помилок (5xx)
                    if (attempt < config.retries) {
                        await this.delay(this.retryDelay * (attempt + 1));
                        continue;
                    }

                    throw error;
                }

                return await this.parseResponse(response);

            } catch (error) {
                lastError = error;

                // Не повторюємо спроби для помилок таймауту або мережевих помилок
                if (error.name === 'AbortError' || error.name === 'TypeError') {
                    if (attempt < config.retries) {
                        await this.delay(this.retryDelay * (attempt + 1));
                        continue;
                    }
                }

                throw error;
            }
        }

        throw lastError;
    }

    /**
     * Fetch з таймаутом
     */
    async fetchWithTimeout(url, options, timeout) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
                throw new Error(`Запит перевищив ліміт часу (${timeout}ms)`);
            }

            throw error;
        }
    }

    /**
     * Створення помилки з відповіді
     */
    async createErrorFromResponse(response) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

        try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                if (errorData.error) {
                    errorMessage = errorData.error;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } else {
                const textError = await response.text();
                if (textError) {
                    errorMessage = textError;
                }
            }
        } catch (parseError) {
            // Якщо не можемо розпарсити помилку, використовуємо базове повідомлення
            console.warn('Не вдалося розпарсити помилку відповіді:', parseError);
        }

        const error = new Error(errorMessage);
        error.status = response.status;
        error.statusText = response.statusText;
        return error;
    }

    /**
     * Розпарсити відповідь
     */
    async parseResponse(response) {
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }

        return await response.text();
    }

    /**
     * Затримка для retry логіки
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Отримання CSRF токена
     */
    getCSRFToken() {
        // Спробуємо отримати з meta тегу
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }

        // Спробуємо отримати з прихованого поля форми
        const hiddenToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (hiddenToken) {
            return hiddenToken.value;
        }

        // Спробуємо отримати з cookie (якщо використовується Django)
        return this.getCookie('csrftoken');
    }

    /**
     * Отримання cookie за ім'ям
     */
    getCookie(name) {
        if (!document.cookie) return null;

        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [cookieName, cookieValue] = cookie.trim().split('=');
            if (cookieName === name) {
                return decodeURIComponent(cookieValue);
            }
        }
        return null;
    }

    /**
     * Обробка помилок API з показом повідомлень користувачу
     */
    static handleAPIError(error, customMessage = null) {
        let userMessage = customMessage;

        if (!userMessage) {
            if (error.status === 401) {
                userMessage = 'Потрібна авторизація';
            } else if (error.status === 403) {
                userMessage = 'Доступ заборонений';
            } else if (error.status === 404) {
                userMessage = 'Ресурс не знайдений';
            } else if (error.status >= 500) {
                userMessage = 'Помилка сервера. Спробуйте пізніше';
            } else if (error.message && error.message.includes('таймауту')) {
                userMessage = 'Запит виконується занадто довго. Перевірте з\'єднання';
            } else {
                userMessage = 'Помилка мережі. Спробуйте пізніше';
            }
        }

        // Показуємо повідомлення користувачу
        if (window.PlayVision && window.PlayVision.showMessage) {
            window.PlayVision.showMessage(userMessage, 'error');
        } else {
            console.error('API Error:', error);
            // Fallback до alert якщо немає системи повідомлень
            if (typeof alert !== 'undefined') {
                alert(userMessage);
            }
        }

        // Логування для debug
        console.error('API Error Details:', {
            message: error.message,
            status: error.status,
            statusText: error.statusText,
            stack: error.stack
        });
    }

    /**
     * Швидкі методи для типових запитів
     */
    static async get(url, options = {}) {
        return this.safeFetch(url, { ...options, method: 'GET' });
    }

    static async post(url, data, options = {}) {
        return this.safeFetch(url, {
            ...options,
            method: 'POST',
            body: data
        });
    }

    static async put(url, data, options = {}) {
        return this.safeFetch(url, {
            ...options,
            method: 'PUT',
            body: data
        });
    }

    static async delete(url, options = {}) {
        return this.safeFetch(url, { ...options, method: 'DELETE' });
    }
}

// Створити глобальний доступ
if (typeof window !== 'undefined') {
    window.APIUtils = APIUtils;
}

// Export для можливого використання як модуль
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIUtils;
}
