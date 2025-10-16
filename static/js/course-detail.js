/**
 * Course Detail Page JavaScript
 * Handles interactive functionality for course detail page
 */

// Preview functionality
let previewTimer = null;
let previewTimeLeft = 20;

/**
 * Start preview video with 20-second limit
 */
function startPreview() {
    const modal = document.getElementById('previewModal');
    const video = document.getElementById('previewVideo');
    const timer = document.getElementById('previewTimer');

    if (!modal) return;

    // Show modal
    modal.classList.add('is-active');

    const scrollY = window.scrollY;
    document.body.style.top = `-${scrollY}px`;
    document.body.classList.add('modal-open');

    // Reset timer
    previewTimeLeft = 20;
    timer.textContent = previewTimeLeft;

    // Start video if available
    if (video) {
        video.currentTime = 0;
        video.play().catch(console.error);

        // Disable video controls after preview
        video.controls = false;
    }

    // Start countdown timer
    previewTimer = setInterval(() => {
        previewTimeLeft--;
        timer.textContent = previewTimeLeft;

        if (previewTimeLeft <= 0) {
            endPreview();
        }
    }, 1000);

    // Track analytics event
    trackEvent('paywall_preview_start', {
        course_id: getCourseId(),
        preview_duration: 20
    });
}

/**
 * End preview and show paywall
 */
function endPreview() {
    const video = document.getElementById('previewVideo');

    // Stop timer
    if (previewTimer) {
        clearInterval(previewTimer);
        previewTimer = null;
    }

    // Pause video
    if (video) {
        video.pause();
        video.controls = false;
    }

    // Show paywall section in modal
    showPaywallInModal();

    // Track analytics event
    trackEvent('paywall_preview_end', {
        course_id: getCourseId(),
        time_watched: 20 - previewTimeLeft
    });
}

/**
 * Close preview modal
 */
function closePreview() {
    const modal = document.getElementById('previewModal');
    const video = document.getElementById('previewVideo');

    // Stop timer
    if (previewTimer) {
        clearInterval(previewTimer);
        previewTimer = null;
    }

    // Stop video
    if (video) {
        video.pause();
        video.currentTime = 0;
    }

    // Hide modal
    modal.classList.remove('is-active');

    const scrollY = document.body.style.top;
    document.body.classList.remove('modal-open');
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';

    if (scrollY) {
        window.scrollTo(0, parseInt(scrollY || '0') * -1);
    }
}

/**
 * Show paywall content in modal
 */
function showPaywallInModal() {
    const modalFooter = document.querySelector('.modal-footer');
    if (modalFooter) {
        modalFooter.style.display = 'block';
    }

    // Update modal content to show paywall message
    const modalBody = document.querySelector('.modal-body');
    if (modalBody) {
        const paywall = document.createElement('div');
        paywall.className = 'preview-paywall';
        paywall.innerHTML = `
            <div class="paywall-message">
                <h3>🔒 Передперегляд завершено</h3>
                <p>Щоб переглянути повний курс, оформіть підписку або купіть курс окремо</p>
            </div>
        `;
        modalBody.appendChild(paywall);
    }
}

/**
 * Start free course (for authenticated users)
 */
function startFreeCourse() {
    const materialsSection = document.getElementById('course-materials');
    if (materialsSection) {
        materialsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Track analytics event
    trackEvent('course_start', {
        course_id: getCourseId(),
        course_type: 'free'
    });
}

/**
 * Handle course progress updates
 */
class CourseProgress {
    constructor() {
        this.initProgressTracking();
        this.initMaterialCompletion();
    }

    initProgressTracking() {
        // Track time spent on page
        this.startTime = Date.now();
        this.lastActivity = Date.now();

        // Track user activity
        ['click', 'scroll', 'keypress'].forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivity = Date.now();
            }, { passive: true });
        });

        // Send progress updates periodically
        setInterval(() => {
            this.updateProgress();
        }, 30000); // Every 30 seconds

        // Send final progress on page unload
        window.addEventListener('beforeunload', () => {
            this.finalUpdate();
        });
    }

    initMaterialCompletion() {
        // Track material link clicks
        const materialLinks = document.querySelectorAll('.material-item a');
        materialLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const materialItem = e.target.closest('.material-item');
                const materialTitle = materialItem.querySelector('h3').textContent;

                // Track material start
                trackEvent('material_start', {
                    course_id: getCourseId(),
                    material_title: materialTitle
                });
            });
        });
    }

    updateProgress() {
        const timeSpent = Date.now() - this.lastActivity;

        // Only update if user was active in last 2 minutes
        if (timeSpent < 120000) {
            const totalTime = Date.now() - this.startTime;

            // Send progress update via HTMX or fetch
            this.sendProgressUpdate(totalTime);
        }
    }

    finalUpdate() {
        const totalTime = Date.now() - this.startTime;

        // Send final progress update
        this.sendProgressUpdate(totalTime, true);
    }

    sendProgressUpdate(timeSpent, isFinal = false) {
        const courseId = getCourseId();
        if (!courseId) return;

        const data = {
            time_spent: Math.floor(timeSpent / 1000), // Convert to seconds
            is_final: isFinal
        };

        // Use sendBeacon for reliability on page unload
        if (isFinal && navigator.sendBeacon) {
            navigator.sendBeacon(
                `/api/course/${courseId}/progress/`,
                JSON.stringify(data)
            );
        } else {
            fetch(`/api/course/${courseId}/progress/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(data)
            }).catch(console.error);
        }
    }
}

/**
 * Handle favorite button functionality
 */
class FavoriteManager {
    constructor() {
        this.initFavoriteButtons();
    }

    initFavoriteButtons() {
        const favoriteButtons = document.querySelectorAll('.favorite-btn');
        favoriteButtons.forEach(btn => {
            btn.addEventListener('htmx:afterRequest', (event) => {
                this.handleFavoriteResponse(event, btn);
            });
        });
    }

    handleFavoriteResponse(event, btn) {
        if (event.detail.successful) {
            // Update button state
            btn.classList.toggle('active');

            // Update button text
            const span = btn.querySelector('span');
            if (span) {
                span.textContent = btn.classList.contains('active')
                    ? 'В улюблених'
                    : 'Додати в улюблені';
            }

            // Show success message
            showToast(
                btn.classList.contains('active')
                    ? 'Додано в улюблені'
                    : 'Видалено з улюблених',
                'success'
            );

            // Track analytics
            trackEvent('favorite_toggle', {
                course_id: getCourseId(),
                action: btn.classList.contains('active') ? 'add' : 'remove'
            });
        } else {
            showToast('Помилка при оновленні улюблених', 'error');
        }
    }
}

/**
 * Handle smooth scrolling and navigation
 */
class NavigationManager {
    constructor() {
        this.initSmoothScrolling();
        this.initSectionHighlighting();
        this.initBackToTop();
    }

    initSmoothScrolling() {
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    initSectionHighlighting() {
        // Highlight current section in navigation
        const sections = document.querySelectorAll('section[id]');
        if (sections.length === 0) return;

        const observerOptions = {
            threshold: 0.3,
            rootMargin: '-20% 0px -35% 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Update navigation highlighting if needed
                    this.updateNavigationHighlight(entry.target.id);
                }
            });
        }, observerOptions);

        sections.forEach(section => observer.observe(section));
    }

    initBackToTop() {
        // Create back to top button
        const backToTop = document.createElement('button');
        backToTop.className = 'back-to-top';
        backToTop.innerHTML = '↑';
        backToTop.setAttribute('aria-label', 'Повернутися наверх');
        backToTop.style.cssText = `
            position: fixed;
            bottom: 6rem;
            right: 2rem;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--hub-primary);
            color: white;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 999;
        `;

        document.body.appendChild(backToTop);

        // Show/hide based on scroll position
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 500) {
                backToTop.style.opacity = '1';
                backToTop.style.visibility = 'visible';
            } else {
                backToTop.style.opacity = '0';
                backToTop.style.visibility = 'hidden';
            }
        });

        // Smooth scroll to top
        backToTop.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    updateNavigationHighlight(sectionId) {
        // This could be used to highlight navigation items
        console.log('Current section:', sectionId);
    }
}

/**
 * Utility Functions
 */

function getCourseId() {
    // Extract course ID from page context or URL
    const courseElement = document.querySelector('[data-course-id]');
    if (courseElement) {
        return courseElement.dataset.courseId;
    }

    // Fallback: extract from URL pattern
    const urlMatch = window.location.pathname.match(/\/course\/([^\/]+)\//);
    return urlMatch ? urlMatch[1] : null;
}

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function trackEvent(eventName, parameters = {}) {
    // Google Analytics 4
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, parameters);
    }

    // Meta Pixel
    if (typeof fbq !== 'undefined') {
        fbq('trackCustom', eventName, parameters);
    }

    // Internal analytics
    console.log('Analytics Event:', eventName, parameters);
}

function showToast(message, type = 'info') {
    // Використовуємо нову централізовану систему якщо доступна
    if (window.notify && typeof window.notify.show === 'function') {
        return window.notify.show(message, type, 3000);
    }

    // Fallback на стару систему (для сумісності)
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    Object.assign(toast.style, {
        position: 'fixed',
        top: '100px',
        right: '20px',
        background: type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#333',
        color: 'white',
        padding: '12px 20px',
        borderRadius: '6px',
        zIndex: '1001',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        maxWidth: '300px'
    });

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);

    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

/**
 * Accessibility enhancements
 */
class AccessibilityManager {
    constructor() {
        this.initKeyboardNavigation();
        this.initFocusManagement();
        this.initScreenReaderSupport();
    }

    initKeyboardNavigation() {
        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('previewModal');
                if (modal && modal.classList.contains('is-active')) {
                    closePreview();
                }
            }
        });

        // Enter/Space for custom buttons
        document.querySelectorAll('.favorite-btn, .preview-btn').forEach(btn => {
            btn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    btn.click();
                }
            });
        });
    }

    initFocusManagement() {
        // Trap focus in modal
        const modal = document.getElementById('previewModal');
        if (modal) {
            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    this.trapFocus(e, modal);
                }
            });
        }
    }

    initScreenReaderSupport() {
        // Add aria-labels where needed
        const favoriteBtn = document.querySelector('.favorite-btn');
        if (favoriteBtn) {
            favoriteBtn.setAttribute('role', 'button');
            favoriteBtn.setAttribute('aria-pressed', favoriteBtn.classList.contains('active'));
        }

        // Update progress bar accessibility
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.setAttribute('role', 'progressbar');
            progressBar.setAttribute('aria-label', 'Прогрес курсу');

            const progressFill = progressBar.querySelector('.progress-fill');
            if (progressFill) {
                const progress = parseInt(progressFill.style.width) || 0;
                progressBar.setAttribute('aria-valuenow', progress);
                progressBar.setAttribute('aria-valuemin', '0');
                progressBar.setAttribute('aria-valuemax', '100');
            }
        }
    }

    trapFocus(e, container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                lastElement.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastElement) {
                firstElement.focus();
                e.preventDefault();
            }
        }
    }
}

/**
 * Initialize everything when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all managers
    new CourseProgress();
    new FavoriteManager();
    new NavigationManager();
    new AccessibilityManager();

    // Close modal when clicking outside
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closePreview();
            }
        });
    }

    console.log('Course detail page initialized successfully');
});

// Export for global access
window.CourseDetailPage = {
    startPreview,
    closePreview,
    startFreeCourse,
    CourseProgress,
    FavoriteManager,
    NavigationManager,
    AccessibilityManager
};
