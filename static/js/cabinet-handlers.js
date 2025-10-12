/**
 * Cabinet Page Handlers
 */

document.addEventListener('DOMContentLoaded', () => {
    initCabinetHandlers();
});

function initCabinetHandlers() {
    // Avatar upload
    const avatarUploadBtn = document.querySelector('.avatar-upload-btn');
    const avatarInput = document.getElementById('avatar-input');

    if (avatarUploadBtn && avatarInput) {
        avatarUploadBtn.addEventListener('click', () => {
            avatarInput.click();
        });

        avatarInput.addEventListener('change', handleAvatarUpload);
    }
}

function handleAvatarUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Валідація
    if (!file.type.startsWith('image/')) {
        if (window.PlayVision && window.PlayVision.showMessage) {
            window.PlayVision.showMessage('Будь ласка, виберіть зображення', 'error');
        }
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        if (window.PlayVision && window.PlayVision.showMessage) {
            window.PlayVision.showMessage('Розмір файлу не повинен перевищувати 5МБ', 'error');
        }
        return;
    }

    // Показуємо preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const avatarImg = document.querySelector('.avatar-image');
        if (avatarImg) {
            avatarImg.src = e.target.result;
        }
    };
    reader.readAsDataURL(file);

    // Відправляємо на сервер
    const formData = new FormData();
    formData.append('avatar', file);

    fetch('/cabinet/upload-avatar/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (window.PlayVision && window.PlayVision.showMessage) {
                    window.PlayVision.showMessage('Аватар оновлено', 'success');
                }
            } else {
                if (window.PlayVision && window.PlayVision.showMessage) {
                    window.PlayVision.showMessage(data.error || 'Помилка завантаження', 'error');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (window.PlayVision && window.PlayVision.showMessage) {
                window.PlayVision.showMessage('Помилка з\'єднання', 'error');
            }
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

