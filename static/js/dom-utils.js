/**
 * DOM Utils - Безпечні утиліти для роботи з DOM
 * Запобігає XSS атакам та null pointer помилкам
 */
class DOMUtils {
    /**
     * Безпечна санітизація HTML контенту
     */
    static sanitizeHTML(str) {
        if (!str || typeof str !== 'string') return '';

        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * Безпечна установка innerHTML з санітизацією
     */
    static safeInnerHTML(element, html) {
        if (!element || !element.innerHTML !== undefined) {
            console.warn('safeInnerHTML: недійсний елемент');
            return false;
        }

        if (!html) {
            element.innerHTML = '';
            return true;
        }

        // Використовуємо DOMPurify якщо доступний, інакше базову санітизацію
        try {
            if (typeof DOMPurify !== 'undefined') {
                element.innerHTML = DOMPurify.sanitize(html);
            } else {
                element.innerHTML = this.sanitizeHTML(html);
            }
            return true;
        } catch (error) {
            console.error('safeInnerHTML помилка:', error);
            element.innerHTML = '';
            return false;
        }
    }

    /**
     * Безпечна робота з classList
     */
    static safeClassList(element, action, className) {
        if (!element || !element.classList) {
            console.warn('safeClassList: недійсний елемент або відсутній classList');
            return false;
        }

        if (!className || typeof className !== 'string') {
            console.warn('safeClassList: недійсне ім\'я класу');
            return false;
        }

        try {
            switch (action) {
                case 'add':
                    element.classList.add(className);
                    break;
                case 'remove':
                    element.classList.remove(className);
                    break;
                case 'toggle':
                    return element.classList.toggle(className);
                case 'contains':
                    return element.classList.contains(className);
                default:
                    console.warn('safeClassList: невідома дія', action);
                    return false;
            }
            return true;
        } catch (error) {
            console.error('safeClassList помилка:', error);
            return false;
        }
    }

    /**
     * Безпечний querySelector з перевіркою
     */
    static safeQuerySelector(selector, context = document) {
        if (!selector || typeof selector !== 'string') {
            console.warn('safeQuerySelector: недійсний селектор');
            return null;
        }

        try {
            return context.querySelector(selector);
        } catch (error) {
            console.error('safeQuerySelector помилка:', error);
            return null;
        }
    }

    /**
     * Безпечний querySelectorAll з перевіркою
     */
    static safeQuerySelectorAll(selector, context = document) {
        if (!selector || typeof selector !== 'string') {
            console.warn('safeQuerySelectorAll: недійсний селектор');
            return [];
        }

        try {
            return Array.from(context.querySelectorAll(selector));
        } catch (error) {
            console.error('safeQuerySelectorAll помилка:', error);
            return [];
        }
    }

    /**
     * Безпечна установка style властивостей
     */
    static safeSetStyle(element, property, value) {
        if (!element || !element.style) {
            console.warn('safeSetStyle: недійсний елемент');
            return false;
        }

        if (!property || typeof property !== 'string') {
            console.warn('safeSetStyle: недійсна властивість');
            return false;
        }

        try {
            element.style[property] = value || '';
            return true;
        } catch (error) {
            console.error('safeSetStyle помилка:', error);
            return false;
        }
    }

    /**
     * Безпечне додавання event listener з автоматичним cleanup
     */
    static safeAddEventListener(element, event, handler, options = {}) {
        if (!element || !element.addEventListener) {
            console.warn('safeAddEventListener: недійсний елемент');
            return null;
        }

        if (!event || typeof event !== 'string') {
            console.warn('safeAddEventListener: недійсний тип події');
            return null;
        }

        if (!handler || typeof handler !== 'function') {
            console.warn('safeAddEventListener: недійсний обробник');
            return null;
        }

        try {
            element.addEventListener(event, handler, options);

            // Повертаємо функцію для cleanup
            return () => {
                try {
                    element.removeEventListener(event, handler, options);
                } catch (cleanupError) {
                    console.error('Помилка cleanup event listener:', cleanupError);
                }
            };
        } catch (error) {
            console.error('safeAddEventListener помилка:', error);
            return null;
        }
    }

    /**
     * Створення елемента з безпечними атрибутами
     */
    static createElement(tagName, attributes = {}, textContent = '') {
        if (!tagName || typeof tagName !== 'string') {
            console.warn('createElement: недійсний тег');
            return null;
        }

        try {
            const element = document.createElement(tagName);

            // Встановлюємо атрибути
            Object.entries(attributes).forEach(([key, value]) => {
                if (key === 'className') {
                    element.className = value;
                } else if (key === 'innerHTML') {
                    this.safeInnerHTML(element, value);
                } else if (key.startsWith('data-') || key.match(/^(id|role|aria-|alt|title|href|src|type)$/)) {
                    element.setAttribute(key, value);
                } else {
                    console.warn('createElement: пропущений небезпечний атрибут', key);
                }
            });

            // Встановлюємо текстовий контент
            if (textContent) {
                element.textContent = textContent;
            }

            return element;
        } catch (error) {
            console.error('createElement помилка:', error);
            return null;
        }
    }

    /**
     * Безпечне видалення елемента з DOM
     */
    static safeRemoveElement(element) {
        if (!element) return false;

        try {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
                return true;
            }
            return false;
        } catch (error) {
            console.error('safeRemoveElement помилка:', error);
            return false;
        }
    }

    /**
     * Перевірка чи елемент видимий
     */
    static isVisible(element) {
        if (!element) return false;

        try {
            const rect = element.getBoundingClientRect();
            const style = window.getComputedStyle(element);

            return rect.width > 0 &&
                rect.height > 0 &&
                style.visibility !== 'hidden' &&
                style.display !== 'none' &&
                parseFloat(style.opacity) > 0;
        } catch (error) {
            console.error('isVisible помилка:', error);
            return false;
        }
    }

    /**
     * Отримати безпечні размеры елемента
     */
    static getElementSize(element) {
        if (!element) {
            return { width: 0, height: 0, top: 0, left: 0 };
        }

        try {
            const rect = element.getBoundingClientRect();
            return {
                width: rect.width,
                height: rect.height,
                top: rect.top,
                left: rect.left
            };
        } catch (error) {
            console.error('getElementSize помилка:', error);
            return { width: 0, height: 0, top: 0, left: 0 };
        }
    }
}

// Створити глобальний доступ
if (typeof window !== 'undefined') {
    window.DOMUtils = DOMUtils;
}

// Export для можливого використання як модуль
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DOMUtils;
}
