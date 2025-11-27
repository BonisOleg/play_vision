/**
 * About Hero Video Player
 * BunnyNet integration з повною крос-браузерною підтримкою
 */

(function() {
    'use strict';

    // === UTILITIES ===
    
    /**
     * Mobile detection (використовує breakpoint з проекту)
     */
    const isMobile = () => window.innerWidth <= 768;
    
    /**
     * Cross-browser fullscreen API
     */
    const fullscreenAPI = {
        request: (element) => {
            if (element.requestFullscreen) {
                return element.requestFullscreen();
            } else if (element.webkitRequestFullscreen) { // Safari
                return element.webkitRequestFullscreen();
            } else if (element.mozRequestFullScreen) { // Firefox
                return element.mozRequestFullScreen();
            } else if (element.msRequestFullscreen) { // IE11
                return element.msRequestFullscreen();
            }
            return Promise.reject(new Error('Fullscreen not supported'));
        },
        
        exit: () => {
            if (document.exitFullscreen) {
                return document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                return document.webkitExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                return document.mozCancelFullScreen();
            } else if (document.msExitFullscreen) {
                return document.msExitFullscreen();
            }
            return Promise.reject(new Error('Exit fullscreen not supported'));
        },
        
        get element() {
            return document.fullscreenElement || 
                   document.webkitFullscreenElement || 
                   document.mozFullScreenElement ||
                   document.msFullscreenElement;
        }
    };

    /**
     * Main Video Player Class
     */
    class AboutHeroVideoPlayer {
        constructor(section) {
            this.section = section;
            this.enabled = this.section.dataset.videoEnabled === 'true';
            
            if (!this.enabled) return;

            this.libraryId = this.section.dataset.videoLibrary;
            this.videoId = this.section.dataset.videoId;
            
            if (!this.libraryId || !this.videoId) {
                console.warn('⚠️ Video IDs missing for About Hero');
                if (this.section.querySelector('.about-hero-play')) {
                    this.section.querySelector('.about-hero-play').style.display = 'none';
                }
                return;
            }

            // Elements
            this.playBtn = this.section.querySelector('.about-hero-play');
            this.closeBtn = this.section.querySelector('.about-video-close');
            this.bgContainer = this.section.querySelector('.about-hero-bg');
            this.videoContainer = this.section.querySelector('.about-hero-video');
            this.playerWrapper = this.section.querySelector('.about-hero-player');
            this.errorMessage = this.section.querySelector('.about-video-error');

            // State
            this.iframe = null;
            this.isActive = false;
            this.hasError = false;
            
            // Bound listeners (для cleanup)
            this.boundFullscreenChange = null;
            this.boundMessageHandler = null;

            this.init();
        }

        init() {
            if (!this.playBtn || !this.videoContainer) {
                console.error('❌ Required elements missing');
                return;
            }

            // Event listeners (з touch optimization)
            this.playBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handlePlay();
            }, { passive: false });

            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.handleClose();
                }, { passive: false });
            }

            // Retry button
            const retryBtn = this.errorMessage?.querySelector('.btn-error-retry');
            if (retryBtn) {
                retryBtn.addEventListener('click', () => {
                    this.hasError = false;
                    this.errorMessage.style.display = 'none';
                    this.createPlayer();
                });
            }

            console.log('✅ About Hero Video initialized');
        }

        handlePlay() {
            if (isMobile()) {
                this.playMobile();
            } else {
                this.playDesktop();
            }
        }

        playDesktop() {
            console.log('🖥️ Desktop: Play clicked');
            
            // Hide background with transition
            if (this.bgContainer) {
                this.bgContainer.classList.add('is-hidden');
            }
            
            // Hide play button with transition
            if (this.playBtn) {
                this.playBtn.classList.add('is-hidden');
            }
            
            // Show video container - explicit flex display
            this.videoContainer.style.display = 'flex';
            this.videoContainer.style.opacity = '1';
            
            // Small delay for smooth transition
            setTimeout(() => {
                this.createPlayer(false); // No autoplay
                this.isActive = true;
                console.log('✅ Desktop player created');
            }, 300);
        }

        playMobile() {
            console.log('📱 Mobile: Play clicked');
            
            // Hide background
            this.bgContainer?.classList.add('is-hidden');
            
            // Hide play button
            this.playBtn?.classList.add('is-hidden');
            
            // Show video container - explicit flex display
            this.videoContainer.style.display = 'flex';
            this.videoContainer.style.opacity = '1';
            
            // Create player з autoplay
            this.createPlayer(true);
            this.isActive = true;
            
            // Check fullscreen support
            if (!document.fullscreenEnabled && 
                !document.webkitFullscreenEnabled && 
                !document.mozFullScreenEnabled) {
                console.warn('⚠️ Fullscreen not supported, playing inline');
                return;
            }
            
            // Fullscreen з затримкою (iOS потребує user interaction)
            setTimeout(() => {
                if (this.iframe) {
                    fullscreenAPI.request(this.iframe)
                        .then(() => console.log('✅ Fullscreen activated'))
                        .catch(err => {
                            console.warn('⚠️ Fullscreen denied:', err);
                        });
                }
            }, 500);
        }

        createPlayer(autoplay = false) {
            if (this.iframe) {
                console.log('⚠️ Player already exists, reusing');
                return;
            }
            
            console.log(`🎬 Creating player (autoplay: ${autoplay})`);

            try {
                const baseUrl = 'https://iframe.mediadelivery.net/embed';
                
                // Validate IDs
                if (!this.libraryId || !this.videoId) {
                    throw new Error('Missing library or video ID');
                }
                
                // Quality selection based on device
                const quality = isMobile() ? '720p' : 'auto';
                
                const params = new URLSearchParams({
                    autoplay: autoplay ? 'true' : 'false',
                    preload: 'false',
                    responsive: 'true',
                    quality: quality
                });
                
                const iframeUrl = `${baseUrl}/${this.libraryId}/${this.videoId}?${params}`;
                
                console.log('📺 Video URL:', iframeUrl);

                this.iframe = document.createElement('iframe');
                this.iframe.src = iframeUrl;
                this.iframe.allow = 'accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture; fullscreen';
                this.iframe.allowFullscreen = true;
                this.iframe.webkitAllowFullscreen = true;
                this.iframe.style.cssText = 'width:100%;height:100%;border:0;position:absolute;top:0;left:0;';
                
                // Error handling
                this.iframe.addEventListener('error', () => {
                    console.error('❌ Iframe error event');
                    this.showError();
                });
                
                // Show loading
                const loading = document.createElement('div');
                loading.className = 'video-loading';
                loading.textContent = 'Завантаження відео';
                this.playerWrapper.appendChild(loading);
                
                // Network timeout (збільшено для 3G)
                const loadTimeout = setTimeout(() => {
                    if (!this.iframe.contentWindow) {
                        console.error('❌ Load timeout (15s)');
                        this.showError();
                    }
                }, 15000); // 15 sec
                
                this.iframe.addEventListener('load', () => {
                    clearTimeout(loadTimeout);
                    // Remove loading spinner
                    const loadingEl = this.playerWrapper.querySelector('.video-loading');
                    if (loadingEl) {
                        loadingEl.remove();
                    }
                    console.log('✅ Iframe loaded');
                });

                // Append to DOM
                this.playerWrapper.innerHTML = '';
                this.playerWrapper.appendChild(loading);
                this.playerWrapper.appendChild(this.iframe);

                // Listen for video events
                this.listenForVideoEvents();

            } catch (err) {
                console.error('❌ Player creation failed:', err);
                this.showError();
            }
        }

        listenForVideoEvents() {
            // Message handler (один раз)
            if (!this.boundMessageHandler) {
                this.boundMessageHandler = (event) => {
                    // Validate origin
                    if (!event.origin.includes('mediadelivery.net')) return;
                    
                    const data = event.data;
                    
                    // Handle video ended
                    if (data && (data.event === 'ended' || data.type === 'ended')) {
                        console.log('✅ Video ended');
                        this.handleClose();
                    }
                };
                
                window.addEventListener('message', this.boundMessageHandler);
            }
            
            // Fullscreen change handler (один раз)
            if (!this.boundFullscreenChange) {
                this.boundFullscreenChange = () => {
                    if (!fullscreenAPI.element && this.isActive) {
                        console.log('📹 Exited fullscreen');
                        
                        // Mobile: закрити відео
                        if (isMobile()) {
                            console.log('📱 Mobile: closing video');
                            this.handleClose();
                        } else {
                            console.log('🖥️ Desktop: video stays in Hero');
                        }
                    }
                };
                
                // Add for all browsers
                document.addEventListener('fullscreenchange', this.boundFullscreenChange);
                document.addEventListener('webkitfullscreenchange', this.boundFullscreenChange);
                document.addEventListener('mozfullscreenchange', this.boundFullscreenChange);
                document.addEventListener('MSFullscreenChange', this.boundFullscreenChange);
            }
        }

        handleClose() {
            console.log('🔴 Closing video player');
            
            // Exit fullscreen якщо active
            if (fullscreenAPI.element) {
                fullscreenAPI.exit()
                    .then(() => console.log('✅ Exited fullscreen'))
                    .catch(err => console.warn('⚠️ Fullscreen exit failed:', err));
            }
            
            // Reset UI
            this.videoContainer.style.display = 'none';
            this.videoContainer.style.opacity = '0';
            
            // Show background
            this.bgContainer?.classList.remove('is-hidden');
            
            // Show play button
            this.playBtn?.classList.remove('is-hidden');

            // Remove iframe
            if (this.iframe) {
                this.iframe.src = ''; // Stop loading
                this.iframe.remove();
                this.iframe = null;
            }
            
            // Clear player wrapper
            if (this.playerWrapper) {
                this.playerWrapper.innerHTML = '';
            }

            // Cleanup listeners
            this.cleanup();

            // Reset state
            this.isActive = false;
            this.hasError = false;
            
            // Hide error if shown
            if (this.errorMessage) {
                this.errorMessage.style.display = 'none';
            }
            
            console.log('✅ Video closed and cleaned up');
        }
        
        cleanup() {
            // Remove message listener
            if (this.boundMessageHandler) {
                window.removeEventListener('message', this.boundMessageHandler);
                this.boundMessageHandler = null;
            }
            
            // Remove fullscreen listeners
            if (this.boundFullscreenChange) {
                document.removeEventListener('fullscreenchange', this.boundFullscreenChange);
                document.removeEventListener('webkitfullscreenchange', this.boundFullscreenChange);
                document.removeEventListener('mozfullscreenchange', this.boundFullscreenChange);
                document.removeEventListener('MSFullscreenChange', this.boundFullscreenChange);
                this.boundFullscreenChange = null;
            }
            
            console.log('🧹 Listeners cleaned up');
        }

        showError() {
            if (this.hasError) return;
            
            this.hasError = true;
            if (this.errorMessage) {
                this.errorMessage.style.display = 'block';
            }
            console.error('❌ Video loading error');
        }
    }

    // === INITIALIZATION ===
    document.addEventListener('DOMContentLoaded', () => {
        const heroSection = document.querySelector('.about-hero[data-video-enabled="true"]');
        if (heroSection) {
            new AboutHeroVideoPlayer(heroSection);
        }
    });

})();

