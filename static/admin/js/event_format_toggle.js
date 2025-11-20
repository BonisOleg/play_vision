/**
 * Event Format Toggle - показує/ховає поля залежно від вибору онлайн/офлайн
 */
(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Знайти radio buttons для формату події
        const formatRadios = $('input[name="event_format"]');
        const locationField = $('.field-location');
        const onlineLinkField = $('.field-online_link');
        
        if (!formatRadios.length) {
            // Якщо поле event_format не знайдено, нічого не робимо
            return;
        }
        
        /**
         * Функція для показу/приховування полів
         */
        function toggleFields() {
            const selectedFormat = $('input[name="event_format"]:checked').val();
            
            if (selectedFormat === 'online') {
                // Онлайн подія - показати online_link, сховати location
                onlineLinkField.show();
                locationField.hide();
                
                // Встановити location = "Онлайн" автоматично (для зручності)
                const locationInput = $('input[name="location"]');
                if (locationInput.val() === '' || locationInput.val() === 'Онлайн') {
                    locationInput.val('Онлайн');
                }
                
                // Зробити online_link обов'язковим візуально
                onlineLinkField.addClass('required');
                locationField.removeClass('required');
                
            } else if (selectedFormat === 'offline') {
                // Офлайн подія - показати location, сховати online_link
                locationField.show();
                onlineLinkField.hide();
                
                // Очистити online_link
                const onlineLinkInput = $('input[name="online_link"]');
                onlineLinkInput.val('');
                
                // Зробити location обов'язковим візуально
                locationField.addClass('required');
                onlineLinkField.removeClass('required');
            }
        }
        
        // Виконати при завантаженні сторінки
        toggleFields();
        
        // Виконати при зміні вибору
        formatRadios.on('change', function() {
            toggleFields();
        });
        
        console.log('Event format toggle initialized');
    });
    
})(django.jQuery);

