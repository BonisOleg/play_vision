/**
 * Material Detail Page JavaScript
 * Handles video protection, progress tracking, and interactive features
 */

// Global variables for material management
let materialConfig = {};
let videoTimer = null;
let progressTracker = null;

/**
 * Initialize material detail page
 */
function initializeMaterial(config) {
    materialConfig = config;

    if (materialConfig.contentType === 'video') {
        initializeVideoFunctionality();
    }

    initializeProgressTracking();
    initializeAccessibilityFeatures();

    console.log('Material detail initialized:', config);
}

/**
 * Video functionality with protection
 */
function initializeVideoFunctionality() {
    const video = document.getElementById('mainVideo') || document.getElementById('previewVideo');
    if (!video) return;

    if (materialConfig.hasAccess) {
        initializeFullVideoAccess(video);
    } else if (materialConfig.isPreview) {
        initializePreviewVideo(video);
    }

    // Add video protection measures
    addVideoProtection(video);
}

/**
 * Initialize full video access with watermarking
 */
function initializeFullVideoAccess(video) {
    // Update watermark position periodically
    let watermarkUpdateInterval = setInterval(() => {
        updateWatermarkPosition();
    }, 30000); // Every 30 seconds

    // Progress tracking
    video.addEventListener('timeupdate', () => {
        updateVideoProgress(video);
    });

    // Completion tracking
    video.addEventListener('ended', () => {
        markMaterialAsCompleted();
    });

    // Quality/speed controls
    initializeVideoControls(video);

    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        clearInterval(watermarkUpdateInterval);
    });
}

/**
 * Initialize preview video with 20-second limit
 */
function initializePreviewVideo(video) {
    let previewTimeLeft = materialConfig.previewSeconds || 20;
    const timerElement = document.getElementById('previewTimer');
    const timeLeftElement = document.getElementById('timeLeft');

    video.addEventListener('play', () => {
        if (timerElement) timerElement.style.display = 'block';

        videoTimer = setInterval(() => {
            previewTimeLeft--;
            if (timeLeftElement) timeLeftElement.textContent = previewTimeLeft;

            if (previewTimeLeft <= 0) {
                endPreview(video);
            }
        }, 1000);

        // Track preview start
        trackEvent('preview_start', {
            material_id: materialConfig.materialId,
            course_id: materialConfig.courseId,
            content_type: materialConfig.contentType
        });
    });

    video.addEventListener('pause', () => {
        if (videoTimer) {
            clearInterval(videoTimer);
            videoTimer = null;
        }
    });
}

/**
 * End preview and show paywall
 */
function endPreview(video) {
    if (videoTimer) {
        clearInterval(videoTimer);
        videoTimer = null;
    }

    video.pause();
    video.style.pointerEvents = 'none';

    // Show paywall modal
    showPaywallModal();

    // Track preview end
    trackEvent('preview_end', {
        material_id: materialConfig.materialId,
        course_id: materialConfig.courseId,
        time_watched: (materialConfig.previewSeconds || 20) - (document.getElementById('timeLeft')?.textContent || 0)
    });
}

/**
 * Add video protection measures
 */
function addVideoProtection(video) {
    // Disable right-click context menu
    video.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Disable keyboard shortcuts
    video.addEventListener('keydown', (e) => {
        // Block common video download/save shortcuts
        if (e.ctrlKey || e.metaKey) {
            if (['s', 'S', 'a', 'A', 'c', 'C', 'v', 'V'].includes(e.key)) {
                e.preventDefault();
                return false;
            }
        }
    });

    // Disable selection
    video.style.userSelect = 'none';
    video.style.webkitUserSelect = 'none';

    // Add additional protection attributes
    video.setAttribute('controlsList', 'nodownload noremoteplayback');
    video.setAttribute('disablePictureInPicture', 'true');

    // Monitor for developer tools (basic detection)
    detectDevTools();
}

/**
 * Basic developer tools detection
 */
function detectDevTools() {
    let devtools = {
        open: false,
        orientation: null
    };

    setInterval(() => {
        const heightThreshold = window.outerHeight - window.innerHeight > 200;
        const widthThreshold = window.outerWidth - window.innerWidth > 200;

        if (heightThreshold || widthThreshold) {
            if (!devtools.open) {
                devtools.open = true;

                // Track developer tools usage
                trackEvent('devtools_detected', {
                    material_id: materialConfig.materialId,
                    user_id: materialConfig.userId
                });

                // Optional: Pause video or show warning
                const video = document.getElementById('mainVideo');
                if (video && !video.paused) {
                    video.pause();
                }
            }
        } else {
            devtools.open = false;
        }
    }, 1000);
}

/**
 * Update watermark position to prevent easy removal
 */
function updateWatermarkPosition() {
    const watermark = document.querySelector('.watermark');
    if (!watermark) return;

    const positions = [
        { bottom: '20px', right: '20px', left: 'auto', top: 'auto' },
        { bottom: '20px', left: '20px', right: 'auto', top: 'auto' },
        { top: '20px', right: '20px', left: 'auto', bottom: 'auto' },
        { top: '20px', left: '20px', right: 'auto', bottom: 'auto' }
    ];

    const randomPosition = positions[Math.floor(Math.random() * positions.length)];

    Object.assign(watermark.style, randomPosition);
}

/**
 * Initialize video controls enhancement
 */
function initializeVideoControls(video) {
    const speedControl = document.querySelector('.speed-control');
    const fullscreenBtn = document.querySelector('.fullscreen-btn');

    if (speedControl) {
        let currentSpeed = 1;
        const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2];

        speedControl.addEventListener('click', () => {
            const currentIndex = speeds.indexOf(currentSpeed);
            const nextIndex = (currentIndex + 1) % speeds.length;
            currentSpeed = speeds[nextIndex];

            video.playbackRate = currentSpeed;
            speedControl.textContent = `${currentSpeed}x`;
        });
    }

    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', () => {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                video.requestFullscreen().catch(console.error);
            }
        });
    }
}

/**
 * Playback speed control
 */
function changePlaybackSpeed() {
    const video = document.getElementById('mainVideo');
    const speedBtn = document.querySelector('.speed-control');

    if (!video || !speedBtn) return;

    const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2];
    let currentIndex = speeds.indexOf(video.playbackRate);

    if (currentIndex === -1) currentIndex = 2; // Default to 1x

    const nextIndex = (currentIndex + 1) % speeds.length;
    const newSpeed = speeds[nextIndex];

    video.playbackRate = newSpeed;
    speedBtn.textContent = `${newSpeed}x`;
}

/**
 * Toggle fullscreen
 */
function toggleFullscreen() {
    const video = document.getElementById('mainVideo');
    if (!video) return;

    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        video.requestFullscreen().catch(console.error);
    }
}

/**
 * Progress tracking for materials
 */
function initializeProgressTracking() {
    if (!materialConfig.hasAccess || !materialConfig.userId) return;

    progressTracker = new MaterialProgressTracker();
    progressTracker.init();
}

/**
 * Material Progress Tracker Class
 */
class MaterialProgressTracker {
    constructor() {
        this.startTime = Date.now();
        this.lastActivity = Date.now();
        this.progressUpdateInterval = null;
        this.minWatchTime = 30; // Minimum seconds to consider as "watched"
    }

    init() {
        this.trackActivity();
        this.startProgressTracking();
        this.setupUnloadHandler();
    }

    trackActivity() {
        ['click', 'scroll', 'keypress', 'mousemove'].forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivity = Date.now();
            }, { passive: true });
        });
    }

    startProgressTracking() {
        this.progressUpdateInterval = setInterval(() => {
            this.updateProgress();
        }, 30000); // Every 30 seconds
    }

    updateProgress() {
        const timeSpent = Date.now() - this.lastActivity;

        // Only update if user was active in last 2 minutes
        if (timeSpent < 120000) {
            const totalTime = Math.floor((Date.now() - this.startTime) / 1000);

            if (totalTime >= this.minWatchTime) {
                this.sendProgressUpdate(totalTime);
            }
        }
    }

    setupUnloadHandler() {
        window.addEventListener('beforeunload', () => {
            const totalTime = Math.floor((Date.now() - this.startTime) / 1000);

            if (totalTime >= this.minWatchTime) {
                this.sendProgressUpdate(totalTime, true);
            }
        });
    }

    sendProgressUpdate(timeSpent, isFinal = false) {
        const data = {
            material_id: materialConfig.materialId,
            time_spent: timeSpent,
            is_final: isFinal
        };

        // Use sendBeacon for reliability on page unload
        if (isFinal && navigator.sendBeacon) {
            navigator.sendBeacon(
                `/api/content/material/progress/`,
                JSON.stringify(data)
            );
        } else {
            fetch(`/api/content/material/progress/`, {
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
 * Update video progress and track completion
 */
function updateVideoProgress(video) {
    if (!video || !materialConfig.hasAccess) return;

    const progress = (video.currentTime / video.duration) * 100;

    // Consider video watched if >= 80% completed
    if (progress >= 80 && !video.dataset.markedComplete) {
        video.dataset.markedComplete = 'true';
        markMaterialAsCompleted();
    }
}

/**
 * Mark material as completed
 */
function markMaterialAsCompleted() {
    if (!materialConfig.userId || !materialConfig.materialId) return;

    fetch(`/api/content/course/${materialConfig.courseId}/progress/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            material_id: materialConfig.materialId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.progress_percentage !== undefined) {
                updateProgressDisplay(data.progress_percentage);
            }

            // Update navigation UI
            markMaterialInNavigation();

            // Track completion
            trackEvent('material_completed', {
                material_id: materialConfig.materialId,
                course_id: materialConfig.courseId,
                progress_percentage: data.progress_percentage
            });
        })
        .catch(console.error);
}

/**
 * Update progress display
 */
function updateProgressDisplay(percentage) {
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-widget p');

    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }

    if (progressText) {
        progressText.textContent = `${Math.round(percentage)}% завершено`;
    }
}

/**
 * Mark material as completed in navigation
 */
function markMaterialInNavigation() {
    const currentNavItem = document.querySelector('.material-nav-item.current');
    if (currentNavItem) {
        currentNavItem.classList.add('completed');
    }
}

/**
 * Show paywall modal
 */
function showPaywallModal() {
    const modal = document.getElementById('paywallModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Focus management
        const firstButton = modal.querySelector('button, a');
        if (firstButton) firstButton.focus();
    }
}

/**
 * Close paywall modal
 */
function closePaywallModal() {
    const modal = document.getElementById('paywallModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

/**
 * Accessibility features
 */
function initializeAccessibilityFeatures() {
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closePaywallModal();
        }

        // Space bar to play/pause video
        if (e.key === ' ' && e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT') {
            const video = document.getElementById('mainVideo') || document.getElementById('previewVideo');
            if (video) {
                e.preventDefault();
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            }
        }
    });

    // Add ARIA labels
    enhanceAccessibility();
}

/**
 * Enhance accessibility
 */
function enhanceAccessibility() {
    // Video controls
    const video = document.getElementById('mainVideo') || document.getElementById('previewVideo');
    if (video) {
        video.setAttribute('role', 'video');
        video.setAttribute('aria-label', `Відео: ${document.title}`);
    }

    // Progress bar
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

    // Navigation items
    const navItems = document.querySelectorAll('.material-nav-item');
    navItems.forEach((item, index) => {
        item.setAttribute('role', 'listitem');
        item.setAttribute('aria-label', `Матеріал ${index + 1}`);

        if (item.classList.contains('current')) {
            item.setAttribute('aria-current', 'page');
        }

        if (item.classList.contains('completed')) {
            item.setAttribute('aria-label', `Матеріал ${index + 1} - завершено`);
        }
    });
}

/**
 * Utility functions
 */
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

/**
 * Handle modal clicks outside content
 */
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('paywallModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closePaywallModal();
            }
        });
    }
});

// Export for global access
window.MaterialDetail = {
    initializeMaterial,
    changePlaybackSpeed,
    toggleFullscreen,
    showPaywallModal,
    closePaywallModal,
    MaterialProgressTracker
};
