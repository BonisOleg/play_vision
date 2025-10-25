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
            // DEMO MODE: Показуємо заглушку з інформацією
            // В production режимі тут буде API запит

            // Спробуємо отримати дані з API
            const response = await fetch(`/api/content/course/${courseId}/preview/`).catch(() => null);

            if (response && response.ok) {
                // Якщо API працює - використовуємо реальні дані
                const data = await response.json();

                const bunnyVideoId = data.bunny_video_id;
                const bunnyLibraryId = data.bunny_library_id;

                if (bunnyVideoId && bunnyLibraryId) {
                    // Створюємо iframe для Bunny.net
                    const iframe = document.createElement('iframe');
                    iframe.src = `https://iframe.mediadelivery.net/embed/${bunnyLibraryId}/${bunnyVideoId}?autoplay=true&preload=true`;
                    iframe.loading = 'lazy';
                    iframe.allow = 'accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture';
                    iframe.allowFullscreen = true;

                    this.videoContainer.innerHTML = '';
                    this.videoContainer.appendChild(iframe);
                    this.videoPlayer = iframe;
                    return;
                } else if (data.preview_video_url) {
                    this.loadLocalVideo(data.preview_video_url);
                    return;
                }
            }

            // DEMO MODE: Показуємо красиву заглушку
            this.showDemoPreview();

        } catch (error) {
            console.error('Preview load error:', error);
            // Fallback на demo
            this.showDemoPreview();
        }
    }

    showDemoPreview() {
        // Показуємо красиву demo заглушку
        this.videoContainer.innerHTML = `
            <div style="
                display: flex; 
                flex-direction: column;
                align-items: center; 
                justify-content: center; 
                height: 100%; 
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                color: white;
                padding: 2rem;
                text-align: center;
            ">
                <svg viewBox="0 0 24 24" width="80" height="80" fill="currentColor" style="opacity: 0.8; margin-bottom: 1.5rem;">
                    <path d="M8,5.14V19.14L19,12.14L8,5.14Z"/>
                </svg>
                <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem; font-weight: 600;">Передперегляд курсу</h3>
                <p style="opacity: 0.8; max-width: 400px; line-height: 1.6;">
                    Тут буде показано 20-секундний фрагмент відео курсу з Bunny.net CDN
                </p>
                <div style="margin-top: 1.5rem; padding: 1rem 1.5rem; background: rgba(229, 9, 20, 0.2); border-radius: 8px; border: 1px solid rgba(229, 9, 20, 0.5);">
                    <small style="opacity: 0.9;">💡 Функція буде активна після додавання відео в адмінці</small>
                </div>
            </div>
        `;
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

