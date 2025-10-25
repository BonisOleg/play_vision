/**
 * HUB PREVIEW - Play Button & Bunny.net Preview
 * Обробка preview відео з 20-секундним обмеженням
 * Інтеграція з Bunny.net CDN
 */

'use strict';

class HubPreviewManager {
    constructor() {
        this.modal = document.getElementById('previewModal');
        this.modalTitle = document.getElementById('previewModalTitle');
        this.videoContainer = document.getElementById('previewVideoContainer');
        this.timerText = document.getElementById('previewTimerText');
        this.lockScreen = document.getElementById('previewLockScreen');
        this.closeBtn = this.modal?.querySelector('.preview-close-btn');
        this.buyBtn = document.getElementById('buyCoursebtn');

        this.currentCourse = null;
        this.timer = null;
        this.timeLeft = 20;
        this.videoPlayer = null;

        if (this.modal) {
            this.init();
        }
    }

    init() {
        // Play buttons click
        const playButtons = document.querySelectorAll('.play-btn');
        playButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.openPreview(btn);
            });
        });

        // Close button
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.closePreview());
        }

        // Click outside modal
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closePreview();
            }
        });

        // ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('is-active')) {
                this.closePreview();
            }
        });

        // Buy course button
        if (this.buyBtn) {
            this.buyBtn.addEventListener('click', () => this.buyCourse());
        }
    }

    openPreview(button) {
        const courseId = button.dataset.courseId;
        const courseTitle = button.dataset.courseTitle;
        const hasAccess = button.dataset.hasAccess === 'true';

        this.currentCourse = {
            id: courseId,
            title: courseTitle,
            hasAccess: hasAccess
        };

        // Update modal title
        this.modalTitle.textContent = `Передперегляд: ${courseTitle}`;

        // Show modal
        this.modal.classList.add('is-active');
        document.body.style.overflow = 'hidden';

        // Load Bunny.net video
        this.loadBunnyVideo(courseId);

        // Start timer (якщо немає доступу)
        if (!hasAccess) {
            this.startTimer();
        } else {
            // Якщо є доступ - ховаємо таймер
            if (this.timerText.parentElement) {
                this.timerText.parentElement.style.display = 'none';
            }
        }
    }

    async loadBunnyVideo(courseId) {
        try {
            // Отримуємо Bunny.net video ID для курсу
            // В реальності це має бути API запит до вашого бекенду
            const response = await fetch(`/api/content/course/${courseId}/preview/`);

            if (!response.ok) {
                throw new Error('Failed to load preview');
            }

            const data = await response.json();

            // Bunny.net embed URL
            const bunnyVideoId = data.bunny_video_id;
            const bunnyLibraryId = data.bunny_library_id || 'YOUR_LIBRARY_ID';

            if (bunnyVideoId) {
                // Створюємо iframe для Bunny.net
                const iframe = document.createElement('iframe');
                iframe.src = `https://iframe.mediadelivery.net/embed/${bunnyLibraryId}/${bunnyVideoId}?autoplay=true&preload=true`;
                iframe.loading = 'lazy';
                iframe.allow = 'accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture';
                iframe.allowFullscreen = true;

                // Очищуємо контейнер і додаємо iframe
                this.videoContainer.innerHTML = '';
                this.videoContainer.appendChild(iframe);

                this.videoPlayer = iframe;
            } else {
                // Fallback: якщо немає Bunny.net ID, показуємо локальне відео
                this.loadLocalVideo(data.preview_video_url);
            }
        } catch (error) {
            console.error('Preview load error:', error);
            this.showError('Не вдалося завантажити передперегляд');
        }
    }

    loadLocalVideo(videoUrl) {
        if (!videoUrl) {
            this.showError('Відео недоступне');
            return;
        }

        const video = document.createElement('video');
        video.src = videoUrl;
        video.controls = true;
        video.autoplay = true;
        video.preload = 'metadata';
        video.style.width = '100%';
        video.style.height = '100%';

        this.videoContainer.innerHTML = '';
        this.videoContainer.appendChild(video);

        this.videoPlayer = video;
    }

    startTimer() {
        this.timeLeft = 20;
        this.updateTimerDisplay();

        this.timer = setInterval(() => {
            this.timeLeft--;
            this.updateTimerDisplay();

            if (this.timeLeft <= 0) {
                this.showLockScreen();
            }
        }, 1000);
    }

    updateTimerDisplay() {
        if (this.timerText) {
            this.timerText.textContent = `${this.timeLeft} сек`;
        }
    }

    showLockScreen() {
        // Stop timer
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }

        // Pause video
        if (this.videoPlayer) {
            if (this.videoPlayer.tagName === 'VIDEO') {
                this.videoPlayer.pause();
            } else if (this.videoPlayer.tagName === 'IFRAME') {
                // Для Bunny.net iframe - відправляємо postMessage для паузи
                this.videoPlayer.contentWindow.postMessage(
                    JSON.stringify({ event: 'pause' }),
                    '*'
                );
            }
        }

        // Show lock screen
        if (this.lockScreen) {
            this.lockScreen.classList.add('is-visible');
        }
    }

    closePreview() {
        // Stop timer
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }

        // Hide modal
        this.modal.classList.remove('is-active');
        document.body.style.overflow = '';

        // Hide lock screen
        if (this.lockScreen) {
            this.lockScreen.classList.remove('is-visible');
        }

        // Clear video
        if (this.videoContainer) {
            this.videoContainer.innerHTML = '';
        }

        this.videoPlayer = null;
        this.currentCourse = null;
        this.timeLeft = 20;

        // Reset timer display
        if (this.timerText && this.timerText.parentElement) {
            this.timerText.parentElement.style.display = 'block';
            this.timerText.textContent = '20 сек';
        }
    }

    buyCourse() {
        if (!this.currentCourse) return;

        // Додаємо курс в кошик через HTMX або redirect
        const courseId = this.currentCourse.id;

        // Використовуємо HTMX для додавання в кошик
        fetch('/htmx/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: `item_type=course&item_id=${courseId}`
        })
            .then(response => {
                if (response.ok) {
                    // Закриваємо modal і редірект на кошик
                    this.closePreview();
                    window.location.href = '/cart/';
                }
            })
            .catch(error => {
                console.error('Add to cart error:', error);
            });
    }

    showError(message) {
        this.videoContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #000; color: white;">
                <p>${message}</p>
            </div>
        `;
    }

    getCSRFToken() {
        const name = 'csrftoken';
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
}

// Ініціалізація після завантаження DOM
document.addEventListener('DOMContentLoaded', () => {
    new HubPreviewManager();
});

