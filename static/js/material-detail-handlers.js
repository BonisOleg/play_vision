/**
 * Material Detail Page Handlers
 * Event handlers без inline onclick
 */

document.addEventListener('DOMContentLoaded', () => {
    initMaterialDetailHandlers();
});

function initMaterialDetailHandlers() {
    // Mark as completed button
    const completeBtn = document.querySelector('.btn[data-action="mark-completed"]');
    if (completeBtn && !completeBtn.disabled) {
        completeBtn.addEventListener('click', markAsCompleted);
    }

    // Preview button
    const previewBtn = document.querySelector('.preview-btn');
    if (previewBtn) {
        previewBtn.addEventListener('click', startPreview);
    }

    // Start free course button
    const freeCourseBtn = document.querySelector('.btn[data-action="start-free"]');
    if (freeCourseBtn) {
        freeCourseBtn.addEventListener('click', startFreeCourse);
    }

    // Modal close buttons
    const modalCloseButtons = document.querySelectorAll('.modal-close');
    modalCloseButtons.forEach(btn => {
        const modal = btn.closest('.modal');
        if (modal) {
            btn.addEventListener('click', () => closeModal(modal));
        }
    });

    // Progress modal close button
    const progressModalClose = document.querySelector('#progressModal .btn-primary');
    if (progressModalClose) {
        progressModalClose.addEventListener('click', closeProgressModal);
    }

    // Preview modal close button
    const previewModalClose = document.querySelector('#previewModal .modal-close');
    if (previewModalClose) {
        previewModalClose.addEventListener('click', closePreview);
    }
}

function markAsCompleted() {
    const materialId = getMaterialId();
    if (!materialId) return;

    const button = document.querySelector('.btn[data-action="mark-completed"]');
    if (button) {
        button.disabled = true;
        button.textContent = 'Зберігаємо...';
    }

    fetch(`/api/materials/${materialId}/complete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (button) {
                    button.textContent = '✓ Завершено';
                }

                if (data.all_completed) {
                    showProgressModal();
                } else {
                    if (window.PlayVision && window.PlayVision.showMessage) {
                        window.PlayVision.showMessage('Матеріал позначено як завершений!', 'success');
                    }
                }
            } else {
                if (button) {
                    button.disabled = false;
                    button.textContent = 'Позначити як виконане';
                }

                if (window.PlayVision && window.PlayVision.showMessage) {
                    window.PlayVision.showMessage(data.error || 'Помилка збереження', 'error');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);

            if (button) {
                button.disabled = false;
                button.textContent = 'Позначити як виконане';
            }

            if (window.PlayVision && window.PlayVision.showMessage) {
                window.PlayVision.showMessage('Помилка з\'єднання', 'error');
            }
        });
}

function showProgressModal() {
    const modal = document.getElementById('progressModal');
    if (modal) {
        modal.classList.add('is-active');
    }
}

function closeProgressModal() {
    const modal = document.getElementById('progressModal');
    if (modal) {
        modal.classList.remove('is-active');
    }
}

function startPreview() {
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.classList.add('is-active');

        // Запускаємо відео якщо є
        const video = modal.querySelector('video');
        if (video) {
            video.play().catch(err => console.log('Video autoplay prevented:', err));
        }
    }
}

function closePreview() {
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.classList.remove('is-active');

        // Зупиняємо відео
        const video = modal.querySelector('video');
        if (video) {
            video.pause();
            video.currentTime = 0;
        }
    }
}

function startFreeCourse() {
    const courseId = document.querySelector('[data-course-id]')?.dataset.courseId;
    if (!courseId) return;

    const button = document.querySelector('.btn[data-action="start-free"]');
    if (button) {
        button.disabled = true;
        button.textContent = 'Обробка...';
    }

    fetch(`/api/courses/${courseId}/start-free/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                if (button) {
                    button.disabled = false;
                    button.textContent = 'Розпочати безкоштовний курс';
                }

                if (window.PlayVision && window.PlayVision.showMessage) {
                    window.PlayVision.showMessage(data.error || 'Помилка', 'error');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);

            if (button) {
                button.disabled = false;
                button.textContent = 'Розпочати безкоштовний курс';
            }

            if (window.PlayVision && window.PlayVision.showMessage) {
                window.PlayVision.showMessage('Помилка з\'єднання', 'error');
            }
        });
}

function closeModal(modal) {
    if (modal) {
        modal.classList.remove('is-active');
    }
}

function getMaterialId() {
    const element = document.querySelector('[data-material-id]');
    return element ? element.dataset.materialId : null;
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

