/**
 * Interval Manager - Безпечне управління таймерами та інтервалами
 * Вирішує проблеми memory leaks та накопичення інтервалів
 */
class IntervalManager {
    constructor() {
        this.intervals = new Map();
        this.timeouts = new Map();
        this.isDestroyed = false;

        // Bind methods для правильного this контексту
        this.cleanup = this.cleanup.bind(this);
        this.pauseAll = this.pauseAll.bind(this);
        this.resumeAll = this.resumeAll.bind(this);

        // Auto-cleanup при закритті сторінки
        if (typeof window !== 'undefined') {
            window.addEventListener('beforeunload', this.cleanup);

            // Pause/resume при зміні видимості вкладки
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.pauseAll();
                } else {
                    this.resumeAll();
                }
            });
        }
    }

    /**
     * Створити безпечний інтервал з автоматичним cleanup
     */
    setInterval(callback, delay, id = null) {
        if (this.isDestroyed) {
            console.warn('IntervalManager вже знищений');
            return null;
        }

        if (typeof callback !== 'function') {
            console.error('Callback має бути функцією');
            return null;
        }

        const key = id || `int_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Видалити існуючий інтервал з таким же ключем
        if (this.intervals.has(key)) {
            this.clearInterval(key);
        }

        const intervalId = setInterval(callback, delay);

        this.intervals.set(key, {
            id: intervalId,
            callback: callback,
            delay: delay,
            paused: false,
            created: Date.now()
        });

        return key;
    }

    /**
     * Створити безпечний timeout з автоматичним cleanup
     */
    setTimeout(callback, delay, id = null) {
        if (this.isDestroyed) {
            console.warn('IntervalManager вже знищений');
            return null;
        }

        if (typeof callback !== 'function') {
            console.error('Callback має бути функцією');
            return null;
        }

        const key = id || `timeout_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Видалити існуючий timeout з таким же ключем
        if (this.timeouts.has(key)) {
            this.clearTimeout(key);
        }

        const timeoutId = setTimeout(() => {
            callback();
            // Автоматично видалити після виконання
            this.timeouts.delete(key);
        }, delay);

        this.timeouts.set(key, {
            id: timeoutId,
            callback: callback,
            delay: delay,
            created: Date.now()
        });

        return key;
    }

    /**
     * Видалити інтервал за ключем
     */
    clearInterval(key) {
        const interval = this.intervals.get(key);
        if (interval) {
            clearInterval(interval.id);
            this.intervals.delete(key);
            return true;
        }
        return false;
    }

    /**
     * Видалити timeout за ключем
     */
    clearTimeout(key) {
        const timeout = this.timeouts.get(key);
        if (timeout) {
            clearTimeout(timeout.id);
            this.timeouts.delete(key);
            return true;
        }
        return false;
    }

    /**
     * Призупинити всі інтервали (але не timeout'и)
     */
    pauseAll() {
        this.intervals.forEach((interval, key) => {
            if (!interval.paused) {
                clearInterval(interval.id);
                interval.paused = true;
            }
        });
    }

    /**
     * Відновити всі призупинені інтервали
     */
    resumeAll() {
        this.intervals.forEach((interval, key) => {
            if (interval.paused) {
                interval.id = setInterval(interval.callback, interval.delay);
                interval.paused = false;
            }
        });
    }

    /**
     * Повний cleanup всіх таймерів
     */
    cleanup() {
        // Очистити всі інтервали
        this.intervals.forEach(interval => {
            if (!interval.paused) {
                clearInterval(interval.id);
            }
        });

        // Очистити всі timeout'и
        this.timeouts.forEach(timeout => {
            clearTimeout(timeout.id);
        });

        // Очистити колекції
        this.intervals.clear();
        this.timeouts.clear();

        this.isDestroyed = true;
    }

    /**
     * Отримати статистику активних таймерів
     */
    getStats() {
        const activeIntervals = Array.from(this.intervals.values()).filter(i => !i.paused).length;
        const pausedIntervals = Array.from(this.intervals.values()).filter(i => i.paused).length;
        const activeTimeouts = this.timeouts.size;

        return {
            activeIntervals,
            pausedIntervals,
            activeTimeouts,
            totalIntervals: this.intervals.size,
            totalTimeouts: this.timeouts.size
        };
    }

    /**
     * Перевірка чи існує таймер з певним ключем
     */
    has(key) {
        return this.intervals.has(key) || this.timeouts.has(key);
    }
}

// Створити глобальний instance
if (typeof window !== 'undefined') {
    window.intervalManager = new IntervalManager();

    // Debug інформація в development mode
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.intervalManager.debug = () => {
            console.log('Interval Manager Stats:', window.intervalManager.getStats());
            console.log('Active intervals:', Array.from(window.intervalManager.intervals.keys()));
            console.log('Active timeouts:', Array.from(window.intervalManager.timeouts.keys()));
        };
    }
}

// Export для можливого використання як модуль
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IntervalManager;
}
