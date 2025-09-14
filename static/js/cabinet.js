/**
 * Кабінет користувача - JavaScript функціональність
 */

class Cabinet {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFormValidation();
        this.setupAvatarUpload();
        this.setupProgressBars();
        this.setupTabSwitching();
        this.loadUserData();
    }

    setupEventListeners() {
        // Форма профілю
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            profileForm.addEventListener('submit', this.handleProfileSubmit.bind(this));
        }

        // Кнопки інтересів
        document.querySelectorAll('.interest-tag').forEach(tag => {
            tag.addEventListener('click', this.toggleInterest.bind(this));
        });

        // Кнопки матеріалів
        document.querySelectorAll('[onclick*="viewMaterial"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const materialId = this.extractMaterialId(btn);
                if (materialId) this.viewMaterial(materialId);
            });
        });

        // Закриття модальних вікон
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // ESC для закриття модальних вікон
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    setupFormValidation() {
        const form = document.getElementById('profile-form');
        if (!form) return;

        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('blur', this.validateField.bind(this));
            input.addEventListener('input', this.clearFieldError.bind(this));
        });
    }

    setupAvatarUpload() {
        const avatarInput = document.getElementById('avatar-input');
        const avatarBtn = document.querySelector('.avatar-upload-btn');

        if (avatarInput && avatarBtn) {
            avatarInput.addEventListener('change', this.handleAvatarUpload.bind(this));
        }
    }

    setupProgressBars() {
        // Анімація прогрес барів
        const progressBars = document.querySelectorAll('.progress-fill');
        progressBars.forEach(bar => {
            const progress = bar.dataset.progress || bar.style.width.replace('%', '');
            if (progress) {
                this.animateProgressBar(bar, progress);
            }
        });
    }

    setupTabSwitching() {
        // Збереження активної вкладки в localStorage
        // Але НЕ переходимо автоматично якщо користувач на головній сторінці кабінету
        const currentPath = window.location.pathname;
        const isMainCabinet = currentPath === '/account/' || currentPath === '/account';

        if (!isMainCabinet) {
            const activeTab = localStorage.getItem('cabinet-active-tab');
            if (activeTab && document.querySelector(`[href*="${activeTab}"]`)) {
                // Переходимо на збережену вкладку тільки якщо не на головній сторінці
                const targetLink = document.querySelector(`[href*="${activeTab}"]`);
                if (targetLink) {
                    window.location.href = targetLink.href;
                }
            }
        }

        // Збереження при зміні вкладки
        document.querySelectorAll('.tab-link').forEach(link => {
            link.addEventListener('click', (e) => {
                // Витягуємо назву вкладки з URL (останній сегмент шляху)
                const url = new URL(link.href);
                const pathSegments = url.pathname.split('/').filter(segment => segment);
                const tab = pathSegments[pathSegments.length - 1]; // остання частина шляху

                if (tab && ['profile', 'subscription', 'payments', 'files', 'loyalty'].includes(tab)) {
                    localStorage.setItem('cabinet-active-tab', tab);
                }
            });
        });
    }

    loadUserData() {
        // Завантаження додаткових даних користувача
        this.loadNotifications();
        this.checkActiveSubscription();
        this.updateLoyaltyProgress();
    }

    // === ОБРОБКА ФОРМ ===

    async handleProfileSubmit(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('.btn-save');

        // Показати загрузку
        this.setButtonLoading(submitBtn, true);

        try {
            // Валідація
            if (!this.validateForm(form)) {
                this.setButtonLoading(submitBtn, false);
                return;
            }

            // Відправка
            const response = await fetch('/account/api/update-profile/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('Профіль успішно оновлено', 'success');
                this.updateUIAfterProfileUpdate(result);
            } else {
                this.showNotification(result.message || 'Помилка оновлення профілю', 'error');
                this.showFormErrors(form, result.errors);
            }

        } catch (error) {
            console.error('Помилка оновлення профілю:', error);
            this.showNotification('Помилка мережі', 'error');
        } finally {
            this.setButtonLoading(submitBtn, false);
        }
    }

    async handleAvatarUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Валідація файлу
        if (!this.validateImageFile(file)) {
            return;
        }

        const formData = new FormData();
        formData.append('avatar', file);

        try {
            const response = await fetch('/account/api/update-profile/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.updateAvatarPreview(file);
                this.showNotification('Аватар оновлено', 'success');
            } else {
                this.showNotification('Помилка завантаження аватара', 'error');
            }

        } catch (error) {
            console.error('Помилка завантаження аватара:', error);
            this.showNotification('Помилка мережі', 'error');
        }
    }

    // === МАТЕРІАЛИ ===

    async viewMaterial(materialId) {
        try {
            const modal = document.getElementById('material-modal');
            const modalTitle = document.getElementById('modal-title');
            const modalContent = document.getElementById('material-content');

            if (!modal) return;

            // Показати модальне вікно
            modal.style.display = 'flex';
            modalContent.innerHTML = '<div class="loading">Завантаження...</div>';

            // Завантажити контент матеріалу
            const response = await fetch(`/hub/material/${materialId}/view/`);
            const data = await response.json();

            if (data.success) {
                modalTitle.textContent = data.title;
                modalContent.innerHTML = data.content;

                // Оновити прогрес якщо потрібно
                this.updateMaterialProgress(materialId, true);
            } else {
                modalContent.innerHTML = '<div class="error">Помилка завантаження матеріалу</div>';
            }

        } catch (error) {
            console.error('Помилка перегляду матеріалу:', error);
            this.showNotification('Помилка завантаження матеріалу', 'error');
        }
    }

    async downloadMaterial(materialId) {
        try {
            this.showNotification('Завантаження розпочато...', 'info');

            window.open(`/account/download/${materialId}/`, '_blank');

            // Оновити прогрес
            this.updateMaterialProgress(materialId, true);

        } catch (error) {
            console.error('Помилка завантаження матеріалу:', error);
            this.showNotification('Помилка завантаження', 'error');
        }
    }

    async toggleFavorite(courseId) {
        try {
            const response = await fetch('/account/api/toggle-favorite/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: `course_id=${courseId}`
            });

            const result = await response.json();

            if (result.success) {
                // Оновити іконку улюбленого
                this.updateFavoriteIcon(courseId, result.is_favorite);
                this.showNotification(result.message, 'success');
            } else {
                this.showNotification(result.message, 'error');
            }

        } catch (error) {
            console.error('Помилка оновлення улюбленого:', error);
            this.showNotification('Помилка мережі', 'error');
        }
    }

    async toggleCompleted(materialId, isCompleted) {
        try {
            const response = await fetch('/account/api/material-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: `material_id=${materialId}&completed=${!isCompleted}`
            });

            const result = await response.json();

            if (result.success) {
                // Оновити UI
                this.updateMaterialCompletedState(materialId, result.completed);
                this.updateCourseProgress(materialId, result.course_progress);
                this.showNotification(result.message, 'success');
            } else {
                this.showNotification(result.message, 'error');
            }

        } catch (error) {
            console.error('Помилка оновлення прогресу:', error);
            this.showNotification('Помилка мережі', 'error');
        }
    }

    // === ПЛАТЕЖІ ===

    async downloadReceipt(paymentId) {
        try {
            window.open(`/payments/receipt/${paymentId}/`, '_blank');
        } catch (error) {
            console.error('Помилка завантаження чеку:', error);
            this.showNotification('Помилка завантаження чеку', 'error');
        }
    }

    async checkPaymentStatus(paymentId) {
        try {
            const response = await fetch(`/payments/status/${paymentId}/`);
            const result = await response.json();

            if (result.success) {
                this.updatePaymentStatus(paymentId, result.status);
                this.showNotification(`Статус платежу: ${result.status_display}`, 'info');
            }

        } catch (error) {
            console.error('Помилка перевірки статусу:', error);
            this.showNotification('Помилка перевірки статусу', 'error');
        }
    }

    async retryPayment(paymentId) {
        try {
            const response = await fetch(`/payments/retry/${paymentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                window.location.href = result.payment_url;
            } else {
                this.showNotification('Помилка повторної оплати', 'error');
            }

        } catch (error) {
            console.error('Помилка повторної оплати:', error);
            this.showNotification('Помилка мережі', 'error');
        }
    }

    // === ДОПОМІЖНІ МЕТОДИ ===

    toggleInterest(e) {
        const tag = e.target;
        tag.classList.toggle('active');

        // Оновити приховане поле якщо потрібно
        this.updateInterestsField();
    }

    updateInterestsField() {
        const activeTags = document.querySelectorAll('.interest-tag.active');
        const interests = Array.from(activeTags).map(tag => tag.textContent.trim());

        // Можна зберегти в прихованому полі або відправити окремо
        console.log('Активні інтереси:', interests);
    }

    validateForm(form) {
        let isValid = true;
        const fields = form.querySelectorAll('input[required]');

        fields.forEach(field => {
            if (!this.validateField({ target: field })) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(e) {
        const field = e.target;
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Очистити попередні помилки
        this.clearFieldError(e);

        // Валідація за типом поля
        switch (field.type) {
            case 'email':
                if (value && !this.isValidEmail(value)) {
                    errorMessage = 'Невірний формат email';
                    isValid = false;
                }
                break;

            case 'tel':
                if (value && !this.isValidPhone(value)) {
                    errorMessage = 'Невірний формат телефону';
                    isValid = false;
                }
                break;

            case 'password':
                if (value && value.length < 8) {
                    errorMessage = 'Пароль має бути не менше 8 символів';
                    isValid = false;
                }
                break;
        }

        // Перевірка на required
        if (field.hasAttribute('required') && !value) {
            errorMessage = 'Це поле обов\'язкове';
            isValid = false;
        }

        // Показати помилку якщо є
        if (!isValid) {
            this.showFieldError(field, errorMessage);
        }

        return isValid;
    }

    showFieldError(field, message) {
        const formGroup = field.closest('.form-group');
        if (!formGroup) return;

        // Додати клас помилки
        field.classList.add('error');

        // Створити повідомлення про помилку
        let errorElement = formGroup.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            formGroup.appendChild(errorElement);
        }

        errorElement.textContent = message;
    }

    clearFieldError(e) {
        const field = e.target;
        const formGroup = field.closest('.form-group');

        field.classList.remove('error');

        const errorElement = formGroup?.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    showFormErrors(form, errors) {
        if (!errors) return;

        Object.entries(errors).forEach(([fieldName, messages]) => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field && messages.length > 0) {
                this.showFieldError(field, messages[0]);
            }
        });
    }

    validateImageFile(file) {
        // Перевірка типу файлу
        if (!file.type.startsWith('image/')) {
            this.showNotification('Оберіть файл зображення', 'error');
            return false;
        }

        // Перевірка розміру (5MB)
        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showNotification('Файл занадто великий (макс. 5MB)', 'error');
            return false;
        }

        return true;
    }

    updateAvatarPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const avatarImg = document.querySelector('.avatar-img');
            const avatarPlaceholder = document.querySelector('.avatar-placeholder');

            if (avatarImg) {
                avatarImg.src = e.target.result;
            } else if (avatarPlaceholder) {
                // Замінити placeholder на зображення
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'avatar-img';
                avatarPlaceholder.parentNode.replaceChild(img, avatarPlaceholder);
            }
        };
        reader.readAsDataURL(file);
    }

    updateUIAfterProfileUpdate(result) {
        // Оновити відображення імені якщо потрібно
        if (result.full_name) {
            const nameElements = document.querySelectorAll('.user-name');
            nameElements.forEach(el => el.textContent = result.full_name);
        }
    }

    updateMaterialProgress(materialId, completed) {
        const materialCard = document.querySelector(`[data-material-id="${materialId}"]`);
        if (!materialCard) return;

        const progressBar = materialCard.querySelector('.progress-fill');
        const progressText = materialCard.querySelector('.progress-text');
        const completeBtn = materialCard.querySelector('[onclick*="toggleCompleted"]');

        if (completed) {
            if (progressBar) {
                progressBar.style.width = '100%';
            }
            if (progressText) {
                progressText.textContent = '100%';
            }
            if (completeBtn) {
                completeBtn.textContent = 'Переглянуто';
            }
        }
    }

    updateMaterialCompletedState(materialId, completed) {
        const materialCard = document.querySelector(`[data-material-id="${materialId}"]`);
        if (!materialCard) return;

        const completeBtn = materialCard.querySelector('[onclick*="toggleCompleted"]');
        if (completeBtn) {
            completeBtn.textContent = completed ? 'Переглянуто' : 'Позначити';
            completeBtn.onclick = () => this.toggleCompleted(materialId, completed);
        }

        // Оновити прогрес бар
        const progressBar = materialCard.querySelector('.progress-fill');
        const progressText = materialCard.querySelector('.progress-text');

        if (completed) {
            if (progressBar) progressBar.style.width = '100%';
            if (progressText) progressText.textContent = '100%';
        }
    }

    updateFavoriteIcon(courseId, isFavorite) {
        const favoriteButtons = document.querySelectorAll(`[onclick*="toggleFavorite(${courseId})"]`);
        favoriteButtons.forEach(btn => {
            if (isFavorite) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    updatePaymentStatus(paymentId, status) {
        const paymentRow = document.querySelector(`[data-payment-id="${paymentId}"]`);
        if (!paymentRow) return;

        const statusBadge = paymentRow.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.className = `status-badge status-${status}`;
            statusBadge.textContent = this.getStatusDisplayName(status);
        }
    }

    animateProgressBar(bar, targetProgress) {
        let currentProgress = 0;
        const increment = targetProgress / 50; // 50 кроків анімації

        const animate = () => {
            currentProgress += increment;
            if (currentProgress >= targetProgress) {
                currentProgress = targetProgress;
            }

            bar.style.width = `${currentProgress}%`;

            if (currentProgress < targetProgress) {
                requestAnimationFrame(animate);
            }
        };

        // Затримка для плавної анімації
        setTimeout(animate, 100);
    }

    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'Збереження...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }

    showNotification(message, type = 'info') {
        // Створити елемент повідомлення
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;

        // Додати стилі якщо ще немає
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 8px;
                    padding: 15px 20px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    border-left: 4px solid #007bff;
                    z-index: 1060;
                    min-width: 300px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    transition: all 0.3s ease;
                    transform: translateX(100%);
                }
                .notification-success { border-left-color: #28a745; }
                .notification-error { border-left-color: #dc3545; }
                .notification-warning { border-left-color: #ffc107; }
                .notification-info { border-left-color: #17a2b8; }
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    margin-left: 15px;
                    color: #6c757d;
                }
                .notification.show {
                    transform: translateX(0);
                }
            `;
            document.head.appendChild(styles);
        }

        // Додати на сторінку
        document.body.appendChild(notification);

        // Показати з анімацією
        setTimeout(() => notification.classList.add('show'), 100);

        // Закриття по кліку
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.hideNotification(notification);
        });

        // Автоматичне закриття
        setTimeout(() => {
            if (notification.parentNode) {
                this.hideNotification(notification);
            }
        }, 5000);
    }

    hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    closeModal(modal) {
        modal.style.display = 'none';
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    closeMaterialModal() {
        this.closeModal(document.getElementById('material-modal'));
    }

    closePaymentDetailsModal() {
        this.closeModal(document.getElementById('payment-details-modal'));
    }

    // === УТИЛІТИ ===

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    isValidPhone(phone) {
        const re = /^\+?[\d\s\-\(\)]+$/;
        return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
    }

    extractMaterialId(element) {
        const onclick = element.getAttribute('onclick');
        const match = onclick?.match(/viewMaterial\((\d+)\)/);
        return match ? parseInt(match[1]) : null;
    }

    getStatusDisplayName(status) {
        const statusNames = {
            'succeeded': 'Успішно',
            'pending': 'Очікує',
            'failed': 'Помилка',
            'cancelled': 'Скасовано'
        };
        return statusNames[status] || status;
    }

    loadNotifications() {
        // Завантаження повідомлень для користувача
        // TODO: Реалізувати API для повідомлень
    }

    checkActiveSubscription() {
        // Перевірка статусу підписки
        // TODO: Реалізувати перевірку статусу
    }

    updateLoyaltyProgress() {
        // Оновлення прогресу лояльності
        const loyaltyProgressBars = document.querySelectorAll('.loyalty-tab .progress-fill');
        loyaltyProgressBars.forEach(bar => {
            const progress = bar.style.width.replace('%', '');
            if (progress) {
                this.animateProgressBar(bar, parseInt(progress));
            }
        });
    }

    // Нові методи для кнопок кабінету

    async cancelSubscription() {
        if (!confirm('Ви впевнені, що хочете скасувати підписку?')) {
            return;
        }

        try {
            const response = await fetch('/account/subscription/cancel/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                this.showMessage(data.error || 'Помилка при скасуванні підписки', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('Помилка мережі', 'error');
        }
    }

    async renewSubscription() {
        try {
            const response = await fetch('/account/subscription/renew/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                this.showMessage(data.error || 'Помилка при поновленні підписки', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('Помилка мережі', 'error');
        }
    }

    async changeSubscriptionPlan(planId) {
        try {
            const response = await fetch('/account/subscription/change/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: `plan_id=${planId}`
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(data.message, 'success');
                if (data.redirect_url) {
                    setTimeout(() => window.location.href = data.redirect_url, 1500);
                } else {
                    setTimeout(() => location.reload(), 1500);
                }
            } else {
                this.showMessage(data.error || 'Помилка при зміні підписки', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('Помилка мережі', 'error');
        }
    }

    async addLoyaltyPoints(points = 50, reason = 'Тестове нарахування') {
        try {
            const response = await fetch('/account/loyalty/add-points/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: `points=${points}&reason=${encodeURIComponent(reason)}`
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(data.message, 'success');

                // Оновлюємо відображення балів
                const pointsElement = document.querySelector('.loyalty-points .points-value');
                if (pointsElement) {
                    pointsElement.textContent = data.new_points;
                }

                if (data.tier_changed) {
                    setTimeout(() => location.reload(), 2000);
                }
            } else {
                this.showMessage(data.error || 'Помилка при додаванні балів', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('Помилка мережі', 'error');
        }
    }

    async markCourseComplete(courseId) {
        try {
            const response = await fetch('/account/course/complete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: `course_id=${courseId}`
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(data.message, 'success');

                // Оновлюємо кнопку
                const button = document.querySelector(`[onclick*="markCourseComplete(${courseId})"]`);
                if (button) {
                    button.textContent = 'Завершено';
                    button.disabled = true;
                    button.classList.add('completed');
                }

                // Оновлюємо прогрес бар
                const progressBar = document.querySelector(`[data-course-id="${courseId}"] .progress-fill`);
                if (progressBar) {
                    progressBar.style.width = '100%';
                }

                // Оновлюємо відсоток
                const progressText = document.querySelector(`[data-course-id="${courseId}"] .progress-text`);
                if (progressText) {
                    progressText.textContent = '100%';
                }
            } else {
                this.showMessage(data.error || 'Помилка при позначенні курсу', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('Помилка мережі', 'error');
        }
    }

    downloadMaterial(materialId) {
        const downloadUrl = `/account/download/${materialId}/`;

        // Створюємо невидиме посилання для завантаження
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.showMessage('Завантаження розпочато...', 'info');
    }
}

// Глобальні функції для onclick handlers
function toggleFavorite(courseId) {
    if (window.cabinet) {
        window.cabinet.toggleFavorite(courseId);
    }
}

function viewMaterial(materialId) {
    if (window.cabinet) {
        window.cabinet.viewMaterial(materialId);
    }
}

function downloadMaterial(materialId) {
    if (window.cabinet) {
        window.cabinet.downloadMaterial(materialId);
    }
}

function toggleCompleted(materialId, isCompleted) {
    if (window.cabinet) {
        window.cabinet.toggleCompleted(materialId, isCompleted);
    }
}

function downloadReceipt(paymentId) {
    if (window.cabinet) {
        window.cabinet.downloadReceipt(paymentId);
    }
}

function checkPaymentStatus(paymentId) {
    if (window.cabinet) {
        window.cabinet.checkPaymentStatus(paymentId);
    }
}

function retryPayment(paymentId) {
    if (window.cabinet) {
        window.cabinet.retryPayment(paymentId);
    }
}

function closeMaterialModal() {
    if (window.cabinet) {
        window.cabinet.closeMaterialModal();
    }
}

function closePaymentDetailsModal() {
    if (window.cabinet) {
        window.cabinet.closePaymentDetailsModal();
    }
}

// Нові глобальні функції для кнопок кабінету
function cancelSubscription() {
    if (window.cabinet) {
        window.cabinet.cancelSubscription();
    }
}

function renewSubscription() {
    if (window.cabinet) {
        window.cabinet.renewSubscription();
    }
}

function changeSubscriptionPlan(planId) {
    if (window.cabinet) {
        window.cabinet.changeSubscriptionPlan(planId);
    }
}

function addLoyaltyPoints(points, reason) {
    if (window.cabinet) {
        window.cabinet.addLoyaltyPoints(points, reason);
    }
}

function markCourseComplete(courseId) {
    if (window.cabinet) {
        window.cabinet.markCourseComplete(courseId);
    }
}

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    window.cabinet = new Cabinet();
});

// Функція для очищення localStorage кабінету (для тестування)
function clearCabinetStorage() {
    localStorage.removeItem('cabinet-active-tab');
    console.log('Cabinet localStorage cleared');
}
