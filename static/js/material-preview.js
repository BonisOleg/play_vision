/**
 * MATERIAL PREVIEW
 * Відтворення перших 20 секунд відео для preview
 * Popup з CTA після закінчення preview
 */

'use strict';

class VideoPreviewManager {
    constructor(videoElement) {
        this.video = videoElement;
        this.previewSeconds = parseInt(videoElement.dataset.previewSeconds || 20);
        this.overlay = document.getElementById('previewOverlay');
        this.hasAccess = videoElement.dataset.hasAccess === 'true';
        this.isGuest = videoElement.dataset.isGuest === 'true';
        this.courseId = videoElement.dataset.courseId;
        this.coursePath = videoElement.dataset.coursePath;

        this.hasShownPreview = false;

        if (!this.hasAccess) {
            this.init();
        }
    }

    init() {
        this.video.addEventListener('timeupdate', () => this.handleTimeUpdate());
        this.video.addEventListener('seeking', (e) => this.handleSeeking(e));
        this.video.addEventListener('loadedmetadata', () => this.setupPreview());

        this.createCTAButtons();
    }

    setupPreview() {
        this.video.currentTime = 0;
    }

    handleTimeUpdate() {
        if (this.video.currentTime >= this.previewSeconds && !this.hasShownPreview) {
            this.showPreviewEnd();
        }
    }

    handleSeeking(e) {
        if (this.video.currentTime > this.previewSeconds) {
            e.preventDefault();
            this.video.currentTime = this.previewSeconds;
            this.showPreviewEnd();
        }
    }

    showPreviewEnd() {
        this.hasShownPreview = true;
        this.video.pause();

        if (this.overlay) {
            this.overlay.classList.remove('is-hidden');
        }

        this.saveToSessionForCart();
    }

    createCTAButtons() {
        if (!this.overlay) return;

        const messageDiv = this.overlay.querySelector('.preview-message');
        if (!messageDiv) return;

        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'preview-actions';
        actionsDiv.style.cssText = 'display: flex; gap: 1rem; margin-top: 1.5rem; justify-content: center;';

        if (this.isGuest) {
            const registerBtn = this.createButton(
                'Вступити в клуб',
                'btn-primary',
                () => this.handleRegister()
            );
            actionsDiv.appendChild(registerBtn);
        } else {
            // Subscription button hidden per requirements
            // const subscribeBtn = this.createButton(
            //     'Оформити підписку',
            //     'btn-primary',
            //     () => window.location.href = '/pricing/'
            // );

            const buyBtn = this.createButton(
                'Купити курс',
                'btn-outline',
                () => this.addToCart()
            );

            // actionsDiv.appendChild(subscribeBtn);
            actionsDiv.appendChild(buyBtn);
        }

        messageDiv.appendChild(actionsDiv);
    }

    createButton(text, className, onClick) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.className = `btn ${className}`;
        btn.addEventListener('click', onClick);
        return btn;
    }

    handleRegister() {
        const currentPath = encodeURIComponent(window.location.pathname);
        window.location.href = `/accounts/register/?next=${currentPath}`;
    }

    saveToSessionForCart() {
        if (this.isGuest && this.courseId) {
            try {
                sessionStorage.setItem('pendingCourseId', this.courseId);
                sessionStorage.setItem('pendingCourseAction', 'preview_ended');
            } catch (e) {
                console.warn('SessionStorage not available:', e);
            }
        }
    }

    addToCart() {
        if (!this.courseId) return;

        const formData = new FormData();
        formData.append('item_type', 'course');
        formData.append('item_id', this.courseId);

        fetch('/htmx/cart/add/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/cart/';
                } else {
                    alert(data.message || 'Помилка додавання до кошику');
                }
            })
            .catch(error => {
                console.error('Cart error:', error);
                alert('Помилка додавання до кошику');
            });
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// Auto-add to cart after registration
class PostRegistrationCart {
    constructor() {
        this.checkPendingCart();
    }

    checkPendingCart() {
        try {
            const courseId = sessionStorage.getItem('pendingCourseId');
            const action = sessionStorage.getItem('pendingCourseAction');

            if (courseId && action === 'preview_ended') {
                this.addToCart(courseId);
                sessionStorage.removeItem('pendingCourseId');
                sessionStorage.removeItem('pendingCourseAction');
            }
        } catch (e) {
            console.warn('SessionStorage not available:', e);
        }
    }

    addToCart(courseId) {
        const formData = new FormData();
        formData.append('item_type', 'course');
        formData.append('item_id', courseId);

        fetch('/htmx/cart/add/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('Курс додано до кошику!');
                }
            })
            .catch(error => {
                console.error('Auto-add to cart error:', error);
            });
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--color-success);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', () => {
    // Initialize video previews
    const previewVideos = document.querySelectorAll('.preview-video');
    previewVideos.forEach(video => {
        new VideoPreviewManager(video);
    });

    // Check for post-registration cart action
    const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
    if (isAuthenticated) {
        new PostRegistrationCart();
    }
});

// Setup global function for inline onloadedmetadata
window.setupVideoPreview = function (videoElement) {
    new VideoPreviewManager(videoElement);
};

