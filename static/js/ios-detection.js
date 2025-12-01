/**
 * iOS Detection Utility
 * Єдина функція для визначення iOS пристроїв
 * Використовується як глобальний модуль (не ES6 модуль)
 */

(function() {
    'use strict';

    /**
     * Перевірка чи це iOS пристрій (включаючи Safari та Chrome на iOS)
     * @returns {boolean}
     */
    function isIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    }

    /**
     * Перевірка чи це iOS Safari (виключає Chrome на iOS)
     * @returns {boolean}
     */
    function isIOSSafari() {
        const ua = navigator.userAgent;
        const iOS = /iPad|iPhone|iPod/.test(ua);
        const webkit = /WebKit/.test(ua);
        const notChrome = !/CriOS|Chrome/.test(ua);
        return iOS && webkit && notChrome;
    }

    /**
     * Додати клас ios-safari до documentElement якщо це iOS пристрій
     * Використовується для застосування iOS-специфічних стилів
     */
    function addIOSClass() {
        if (isIOS()) {
            document.documentElement.classList.add('ios-safari');
        }
    }

    // Експорт в глобальний scope
    window.iOSDetection = {
        isIOS: isIOS,
        isIOSSafari: isIOSSafari,
        addIOSClass: addIOSClass
    };

    // Також експортуємо окремі функції для зручності
    window.isIOS = isIOS;
    window.isIOSSafari = isIOSSafari;
    window.addIOSClass = addIOSClass;
})();

