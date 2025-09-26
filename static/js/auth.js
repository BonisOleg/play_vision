// Auth JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Initialize tabs
    initAuthTabs();

    // Initialize form validation
    initFormValidation();

    // Initialize phone input
    initPhoneInput();

    // Initialize social auth
    initSocialAuth();
});

// Tab functionality
function initAuthTabs() {
    const tabs = document.querySelectorAll('.auth-tab');
    const tabContents = document.querySelectorAll('.form-tab');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const targetTab = this.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('auth-tab--active'));
            this.classList.add('auth-tab--active');

            // Show corresponding content
            tabContents.forEach(content => {
                if (content.dataset.tab === targetTab) {
                    content.classList.add('form-tab--active');
                } else {
                    content.classList.remove('form-tab--active');
                }
            });

            // Update form requirements based on active tab
            updateFormRequirements(targetTab);
        });
    });
}

// Update form requirements based on active tab
function updateFormRequirements(activeTab) {
    const emailInput = document.querySelector('input[name="email"], input[name="username"]');
    const phoneInput = document.querySelector('input[name="phone"]');
    const form = document.querySelector('#registerForm, #loginForm');

    if (activeTab === 'email') {
        if (emailInput) {
            emailInput.required = true;
        }
        if (phoneInput) {
            phoneInput.required = false;
            phoneInput.value = ''; // Очистити замість disabled
        }
    } else if (activeTab === 'phone') {
        if (emailInput) {
            emailInput.required = false;
            emailInput.value = ''; // Очистити замість disabled
        }
        if (phoneInput) {
            phoneInput.required = true;
        }
    }
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('#registerForm, #loginForm');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            // Clear existing server errors
            clearServerErrors(this);

            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }

            // Add loading state
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.classList.add('btn--loading');
            submitButton.disabled = true;
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function () {
                validateInput(this);
            });

            input.addEventListener('input', function () {
                if (this.classList.contains('error')) {
                    validateInput(this);
                }
            });
        });
    });
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });

    // Check password match for registration
    if (form.id === 'registerForm') {
        const password1 = form.querySelector('input[name="password1"]');
        const password2 = form.querySelector('input[name="password2"]');

        if (password1 && password2 && password1.value !== password2.value) {
            showError(password2, 'Паролі не співпадають');
            isValid = false;
        }
    }

    return isValid;
}

function validateInput(input) {
    removeError(input);

    // Check if empty
    if (!input.value.trim()) {
        showError(input, 'Це поле обов\'язкове');
        return false;
    }

    // Email validation
    if (input.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value)) {
            showError(input, 'Введіть коректну email адресу');
            return false;
        }
    }

    // Phone validation
    if (input.name === 'phone') {
        const phoneRegex = /^[0-9]{9}$/;
        if (!phoneRegex.test(input.value)) {
            showError(input, 'Введіть 9 цифр номера телефону');
            return false;
        }
    }

    // Password validation
    if (input.type === 'password' && input.name === 'password1') {
        if (input.value.length < 8) {
            showError(input, 'Пароль має містити мінімум 8 символів');
            return false;
        }
    }

    return true;
}

function showError(input, message) {
    input.classList.add('error');

    // Remove existing client error message
    const existingError = input.parentElement.querySelector('.form-error.client-error');
    if (existingError) {
        existingError.remove();
    }

    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error client-error';
    errorDiv.textContent = message;
    input.parentElement.appendChild(errorDiv);
}

function removeError(input) {
    input.classList.remove('error');
    const errorDiv = input.parentElement.querySelector('.form-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Phone input formatting
function initPhoneInput() {
    const phoneInputs = document.querySelectorAll('input[name="phone"]');

    phoneInputs.forEach(input => {
        input.addEventListener('input', function (e) {
            // Remove non-digits
            let value = e.target.value.replace(/\D/g, '');

            // Limit to 9 digits
            if (value.length > 9) {
                value = value.substr(0, 9);
            }

            // Format the number
            let formatted = '';
            if (value.length > 0) {
                formatted = value.substr(0, 2);
            }
            if (value.length > 2) {
                formatted += ' ' + value.substr(2, 3);
            }
            if (value.length > 5) {
                formatted += ' ' + value.substr(5, 2);
            }
            if (value.length > 7) {
                formatted += ' ' + value.substr(7, 2);
            }

            e.target.value = formatted;
        });

        // Handle backspace
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Backspace' && this.value.endsWith(' ')) {
                e.preventDefault();
                this.value = this.value.slice(0, -2);
            }
        });
    });
}

// Social auth
function initSocialAuth() {
    const socialButtons = document.querySelectorAll('.social-btn');

    socialButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const provider = this.classList.contains('social-btn--google') ? 'google' :
                this.classList.contains('social-btn--telegram') ? 'telegram' :
                    this.classList.contains('social-btn--tiktok') ? 'tiktok' : null;

            if (provider) {
                // Add loading state
                this.classList.add('loading');

                // In a real implementation, this would redirect to the OAuth provider
                console.log(`Authenticating with ${provider}`);

                // Simulate API call
                setTimeout(() => {
                    this.classList.remove('loading');
                    showNotification(`Авторизація через ${provider} тимчасово недоступна`, 'info');
                }, 1000);
            }
        });
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const existingNotification = document.querySelector('.auth-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.className = `auth-notification auth-notification--${type}`;
    notification.textContent = message;

    // Add styles if not present
    if (!document.querySelector('#auth-notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'auth-notification-styles';
        styles.textContent = `
            .auth-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 16px 24px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 1000;
                animation: slideInRight 0.3s ease;
                max-width: 400px;
            }
            
            .auth-notification--success {
                background: #4CAF50;
            }
            
            .auth-notification--error {
                background: #F44336;
            }
            
            .auth-notification--info {
                background: #2196F3;
            }
            
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideOutRight {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
        `;
        document.head.appendChild(styles);
    }

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Password visibility toggle
document.querySelectorAll('input[type="password"]').forEach(input => {
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = 'password-toggle';
    toggleButton.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
        </svg>
    `;
    toggleButton.style.cssText = `
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        color: #666;
    `;

    wrapper.appendChild(toggleButton);

    toggleButton.addEventListener('click', function () {
        const type = input.type === 'password' ? 'text' : 'password';
        input.type = type;

        // Update icon
        if (type === 'text') {
            this.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
            `;
        } else {
            this.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                </svg>
            `;
        }
    });
});

// Handle form messages from server
const messages = document.querySelector('.messages');
if (messages) {
    setTimeout(() => {
        messages.style.animation = 'fadeOut 0.5s ease forwards';
        setTimeout(() => {
            messages.remove();
        }, 500);
    }, 5000);
}

// Clear server-side validation errors
function clearServerErrors(form) {
    // Remove Django form errors (but keep client-side errors)
    const serverErrors = form.querySelectorAll('.form-error:not(.client-error)');
    serverErrors.forEach(error => error.remove());

    // Remove error classes from inputs with server errors
    const inputsWithServerErrors = form.querySelectorAll('input.error');
    inputsWithServerErrors.forEach(input => {
        // Only remove error class if it's not a current client validation error
        if (!input.value.trim() === false) { // If field has content
            input.classList.remove('error');
        }
    });
}

// Initialize server error handling on page load
document.addEventListener('DOMContentLoaded', function () {
    // Mark existing server errors (from Django) differently 
    const serverErrors = document.querySelectorAll('.form-error');
    serverErrors.forEach(error => {
        error.classList.add('server-error');
    });
});
