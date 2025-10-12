/**
 * Theme Manager - Керування світлою та темною темою
 * Оптимізовано для запобігання мерехтінь та підтримки iOS Safari
 */

const ThemeManager = (() => {
    const THEME_KEY = 'playvision-theme';
    const THEME_ATTR = 'data-theme';
    const TRANSITION_CLASS = 'theme-transition-disabled';
    const VALID_THEMES = ['light', 'dark', 'auto'];

    let currentTheme = 'light';
    let systemThemeQuery = null;

    /**
     * Ініціалізація менеджера тем
     */
    function init() {
        currentTheme = getSavedTheme();
        applyTheme(currentTheme, false);
        watchSystemTheme();

        // iOS Safari specific fix
        if (isIOSSafari()) {
            document.documentElement.classList.add('ios-safari');
        }
    }

    /**
     * Отримати збережену тему з localStorage
     */
    function getSavedTheme() {
        try {
            const saved = localStorage.getItem(THEME_KEY);
            return VALID_THEMES.includes(saved) ? saved : 'light';
        } catch (e) {
            console.warn('LocalStorage недоступний:', e);
            return 'light';
        }
    }

    /**
     * Застосувати тему
     * @param {string} theme - назва теми
     * @param {boolean} animated - чи використовувати анімацію
     */
    function applyTheme(theme, animated = true) {
        const html = document.documentElement;

        // Вимкнути transitions при миттєвій зміні
        if (!animated) {
            html.classList.add(TRANSITION_CLASS);
        }

        html.setAttribute(THEME_ATTR, theme);
        currentTheme = theme;

        // Update meta theme-color for mobile browsers
        updateMetaThemeColor(theme);

        if (!animated) {
            // Force reflow
            void html.offsetHeight;

            // Re-enable transitions
            requestAnimationFrame(() => {
                setTimeout(() => {
                    html.classList.remove(TRANSITION_CLASS);
                }, 10);
            });
        }
    }

    /**
     * Встановити нову тему
     */
    function setTheme(theme) {
        if (!VALID_THEMES.includes(theme)) {
            console.warn('Невірна тема:', theme);
            return;
        }

        try {
            localStorage.setItem(THEME_KEY, theme);
        } catch (e) {
            console.warn('Не вдалось зберегти тему:', e);
        }

        applyTheme(theme, true);
    }

    /**
     * Переключити між світлою та темною темою
     */
    function toggleTheme() {
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    }

    /**
     * Отримати поточну тему
     */
    function getTheme() {
        return currentTheme;
    }

    /**
     * Відстежувати зміни системної теми
     */
    function watchSystemTheme() {
        if (!window.matchMedia) return;

        try {
            systemThemeQuery = window.matchMedia('(prefers-color-scheme: dark)');

            const handleChange = () => {
                if (currentTheme === 'auto') {
                    applyTheme('auto', true);
                }
            };

            // Modern API
            if (systemThemeQuery.addEventListener) {
                systemThemeQuery.addEventListener('change', handleChange);
            }
            // Legacy Safari
            else if (systemThemeQuery.addListener) {
                systemThemeQuery.addListener(handleChange);
            }
        } catch (e) {
            console.warn('Не вдалось відстежити системну тему:', e);
        }
    }

    /**
     * Оновити meta theme-color для mobile browsers
     */
    function updateMetaThemeColor(theme) {
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) return;

        let color = '#ff6b35'; // default primary color

        if (theme === 'dark' || (theme === 'auto' && systemThemeQuery?.matches)) {
            color = '#1a1a1a'; // dark bg color
        }

        metaThemeColor.setAttribute('content', color);
    }

    /**
     * Перевірка чи це iOS Safari
     */
    function isIOSSafari() {
        const ua = navigator.userAgent;
        const iOS = /iPad|iPhone|iPod/.test(ua);
        const webkit = /WebKit/.test(ua);
        const notChrome = !/CriOS|Chrome/.test(ua);
        return iOS && webkit && notChrome;
    }

    return {
        init,
        setTheme,
        toggleTheme,
        getTheme
    };
})();

// Ініціалізація при завантаженні
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
    ThemeManager.init();
}

// Експорт в глобальний scope
if (typeof window !== 'undefined') {
    window.ThemeManager = ThemeManager;
}

