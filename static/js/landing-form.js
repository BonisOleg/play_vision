/**
 * LANDING FORM - Валідація та AJAX відправка
 * Форматування телефону, валідація полів, відправка без перезавантаження
 * CSP-compliant (немає inline JS)
 */

(function() {
    'use strict';
    
    // Елементи DOM
    const form = document.getElementById('leadForm');
    const submitBtn = document.getElementById('submitBtn');
    const formMessage = document.getElementById('formMessage');
    
    const firstNameInput = document.getElementById('id_first_name');
    const phoneInput = document.getElementById('id_phone');
    const emailInput = document.getElementById('id_email');
    
    const firstNameError = document.getElementById('error_first_name');
    const phoneError = document.getElementById('error_phone');
    const emailError = document.getElementById('error_email');
    
    if (!form) return;
    
    /**
     * Форматування українського номера телефону
     */
    function formatPhoneNumber(value) {
        // Видалити всі символи крім цифр
        const numbers = value.replace(/\D/g, '');
        
        // Якщо починається з 0, замінити на 380
        let formatted = numbers;
        if (formatted.startsWith('0')) {
            formatted = '380' + formatted.substring(1);
        } else if (!formatted.startsWith('380')) {
            formatted = '380' + formatted;
        }
        
        // Обмежити до 12 цифр (380 + 9 цифр)
        formatted = formatted.substring(0, 12);
        
        // Форматувати у вигляді +380(XX)XXX-XX-XX
        if (formatted.length >= 3) {
            let result = '+380';
            const rest = formatted.substring(3);
            
            if (rest.length > 0) {
                result += '(' + rest.substring(0, 2);
                if (rest.length >= 2) {
                    result += ')';
                    if (rest.length > 2) {
                        result += ' ' + rest.substring(2, 5);
                        if (rest.length > 5) {
                            result += '-' + rest.substring(5, 7);
                            if (rest.length > 7) {
                                result += '-' + rest.substring(7, 9);
                            }
                        }
                    }
                }
            }
            
            return result;
        }
        
        return '+' + formatted;
    }
    
    /**
     * Обробка введення номера телефону з форматуванням в реальному часі
     */
    if (phoneInput) {
        // Під час введення - форматувати одразу з дужками
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length === 0) {
                e.target.value = '+380';
                return;
            }
            
            // Переконатися що починається з 380
            if (!value.startsWith('380')) {
                if (value.startsWith('0')) {
                    value = '380' + value.substring(1);
                } else {
                    value = '380' + value;
                }
            }
            
            // Обмежити до 12 цифр
            value = value.substring(0, 12);
            
            // Форматувати одразу як +380(XX) XXX-XX-XX
            if (value.length >= 3) {
                let formatted = '+380';
                const rest = value.substring(3);
                
                if (rest.length > 0) {
                    formatted += '(' + rest.substring(0, 2);
                    if (rest.length >= 2) {
                        formatted += ')';
                        if (rest.length > 2) {
                            formatted += ' ' + rest.substring(2, 5);
                            if (rest.length > 5) {
                                formatted += '-' + rest.substring(5, 7);
                                if (rest.length > 7) {
                                    formatted += '-' + rest.substring(7, 9);
                                }
                            }
                        }
                    }
                }
                
                e.target.value = formatted;
            } else {
                e.target.value = '+' + value;
            }
        });
        
        // При focus - встановити +380 якщо порожньо
        phoneInput.addEventListener('focus', function(e) {
            if (!e.target.value || e.target.value === '+' || e.target.value === '+3') {
                e.target.value = '+380';
                // Встановити курсор в кінець
                setTimeout(() => {
                    e.target.setSelectionRange(4, 4);
                }, 0);
            }
        });
    }
    
    /**
     * Валідація імені
     */
    function validateFirstName(value) {
        if (!value || value.trim().length < 2) {
            return 'Введіть ваше ім\'я';
        }
        
        const nameRegex = /^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]+$/;
        if (!nameRegex.test(value)) {
            return 'Ім\'я може містити лише літери';
        }
        
        return null;
    }
    
    /**
     * Валідація телефону
     */
    function validatePhone(value) {
        const phoneRegex = /^\+380\d{9}$/;
        const cleanPhone = value.replace(/\D/g, '');
        
        if (cleanPhone.length < 12) {
            return 'Введіть повний номер телефону';
        }
        
        const formattedPhone = '+' + cleanPhone.substring(0, 12);
        if (!phoneRegex.test(formattedPhone)) {
            return 'Введіть коректний український номер';
        }
        
        return null;
    }
    
    /**
     * Валідація email
     */
    function validateEmail(value) {
        if (!value || value.trim().length === 0) {
            return 'Будь ласка, вкажіть вашу email адресу';
        }
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            return 'Введіть коректну email адресу';
        }
        
        return null;
    }
    
    /**
     * Показати помилку поля
     */
    function showError(input, errorElement, message) {
        if (input && message) {
            input.classList.add('error');
            input.setAttribute('placeholder', message);
        }
    }
    
    /**
     * Очистити помилку поля
     */
    function clearError(input, errorElement) {
        if (input) {
            input.classList.remove('error');
            // Відновити оригінальний placeholder
            const originalPlaceholders = {
                'id_first_name': 'Ваше ім\'я',
                'id_phone': '+380(__) ___-__-__',
                'id_email': 'Ваш email'
            };
            if (originalPlaceholders[input.id]) {
                input.setAttribute('placeholder', originalPlaceholders[input.id]);
            }
        }
    }
    
    /**
     * Показати повідомлення форми
     */
    function showMessage(message, type) {
        formMessage.textContent = message;
        formMessage.className = 'form-message ' + type;
        formMessage.style.display = 'block';
        
        // Автоматично приховати через 10 секунд
        setTimeout(() => {
            formMessage.style.display = 'none';
        }, 10000);
    }
    
    /**
     * Валідація форми перед відправкою
     */
    function validateForm() {
        let isValid = true;
        
        // Валідація імені
        const nameError = validateFirstName(firstNameInput.value);
        if (nameError) {
            showError(firstNameInput, firstNameError, nameError);
            isValid = false;
        } else {
            clearError(firstNameInput, firstNameError);
        }
        
        // Валідація телефону
        const phoneError = validatePhone(phoneInput.value);
        if (phoneError) {
            showError(phoneInput, phoneError, phoneError);
            isValid = false;
        } else {
            clearError(phoneInput, phoneError);
        }
        
        // Валідація email
        const emailError = validateEmail(emailInput.value);
        if (emailError) {
            showError(emailInput, emailError, emailError);
            isValid = false;
        } else {
            clearError(emailInput, emailError);
        }
        
        return isValid;
    }
    
    /**
     * Відправка форми через AJAX
     */
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Очистити попередні помилки та повідомлення
        formMessage.style.display = 'none';
        clearError(firstNameInput, firstNameError);
        clearError(phoneInput, phoneError);
        clearError(emailInput, emailError);
        
        // Валідація
        if (!validateForm()) {
            return;
        }
        
        // Показати loader
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Отримати дані форми
        const formData = new FormData(form);
        
        // Очистити телефон від форматування
        const cleanPhone = phoneInput.value.replace(/\D/g, '');
        formData.set('phone', '+' + cleanPhone.substring(0, 12));
        
        // Відправити через fetch
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => {
            if (!response.ok && response.status !== 400) {
                throw new Error('Network error');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Успіх
                showMessage(data.message, 'success');
                form.reset();
                
                // Facebook Pixel - Track Lead
                if (typeof fbq !== 'undefined') {
                    fbq('track', 'Lead');
                }
                
                // Google Analytics - Track Event
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'generate_lead', {
                        'event_category': 'engagement',
                        'event_label': 'Landing Page Form'
                    });
                }
            } else {
                // Помилки валідації
                if (data.errors) {
                    Object.keys(data.errors).forEach(field => {
                        const input = document.getElementById('id_' + field);
                        const errorElement = document.getElementById('error_' + field);
                        if (input && errorElement) {
                            showError(input, errorElement, data.errors[field][0]);
                        }
                    });
                }
                
                showMessage(data.message || 'Виникла помилка при обробці заявки', 'error');
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            showMessage('Виникла помилка при відправці форми. Спробуйте ще раз.', 'error');
        })
        .finally(() => {
            // Приховати loader
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        });
    });
    
    // Real-time валідація при введенні
    firstNameInput.addEventListener('blur', function() {
        const error = validateFirstName(this.value);
        if (error) {
            showError(this, firstNameError, error);
        } else {
            clearError(this, firstNameError);
        }
    });
    
    phoneInput.addEventListener('blur', function() {
        const error = validatePhone(this.value);
        if (error) {
            showError(this, phoneError, error);
        } else {
            clearError(this, phoneError);
        }
    });
    
    emailInput.addEventListener('blur', function() {
        const error = validateEmail(this.value);
        if (error) {
            showError(this, emailError, error);
        } else {
            clearError(this, emailError);
        }
    });
    
})();

