/**
 * Theme Manager - Керування світлою та темною темою
 * Запобігає мерехтінню при завантаженні та зміні теми
 */

const ThemeManager = (function () {
    const THEME_KEY = 'playvision-theme';
    const THEME_ATTR = 'data-theme';
    const TRANSITION_CLASS = 'theme-transition-disabled';

    let currentTheme = 'light';

    function init() {
        // Отримуємо збережену тему або системну
        currentTheme = getSavedTheme();

        // Застосовуємо тему без анімації при завантаженні
        applyTheme(currentTheme, false);

        // Слухаємо зміни системної теми
        watchSystemTheme();
    }

    function getSavedTheme() {
        const saved = localStorage.getItem(THEME_KEY);
        if (saved && (saved === 'light' || saved === 'dark' || saved === 'auto')) {
            return saved;
        }
        return 'light';
    }

    function applyTheme(theme, animated = true) {
        const html = document.documentElement;

        if (!animated) {
            html.classList.add(TRANSITION_CLASS);
        }

        html.setAttribute(THEME_ATTR, theme);
        currentTheme = theme;

        if (!animated) {
            // Примусово викликаємо reflow для застосування класу
            html.offsetHeight;

            // Видаляємо клас після короткої затримки
            setTimeout(() => {
                html.classList.remove(TRANSITION_CLASS);
            }, 50);
        }
    }

    function setTheme(theme) {
        if (theme !== 'light' && theme !== 'dark' && theme !== 'auto') {
            console.warn('Invalid theme:', theme);
            return;
        }

        localStorage.setItem(THEME_KEY, theme);
        applyTheme(theme, true);
    }

    function toggleTheme() {
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    }

    function getTheme() {
        return currentTheme;
    }

    function watchSystemTheme() {
        if (!window.matchMedia) return;

        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

        const handleChange = (e) => {
            if (currentTheme === 'auto') {
                // Якщо режим авто, оновлюємо згідно системи
                applyTheme('auto', true);
            }
        };

        if (darkModeQuery.addEventListener) {
            darkModeQuery.addEventListener('change', handleChange);
        } else if (darkModeQuery.addListener) {
            darkModeQuery.addListener(handleChange);
        }
    }

    return {
        init,
        setTheme,
        toggleTheme,
        getTheme
    };
})();

// Ініціалізуємо тему якомога раніше
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
    ThemeManager.init();
}

// Експортуємо в глобальний об'єкт
window.ThemeManager = ThemeManager;

