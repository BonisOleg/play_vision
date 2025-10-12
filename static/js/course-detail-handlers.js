/**
 * Course Detail Page Handlers
 * Event handlers без inline onclick
 */

document.addEventListener('DOMContentLoaded', () => {
    initCourseDetailHandlers();
});

function initCourseDetailHandlers() {
    // Preview button
    const previewBtn = document.querySelector('[data-action="start-preview"]');
    if (previewBtn) {
        previewBtn.addEventListener('click', startPreview);
    }

    // Start free course button
    const freeCourseBtn = document.querySelector('[data-action="start-free-course"]');
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

    // Preview modal close
    const previewModalClose = document.querySelector('#previewModal .modal-close');
    if (previewModalClose) {
        previewModalClose.addEventListener('click', closePreview);
    }
}

function startPreview() {
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.classList.add('is-active');

        // Запускаємо відео
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

    const button = document.querySelector('[data-action="start-free-course"]');
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

