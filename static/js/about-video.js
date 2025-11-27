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
            // Hide background
            if (this.bgContainer) {
                this.bgContainer.classList.add('is-hidden');
            }
            
            // Show video container
            this.videoContainer.style.display = 'block';
            this.playBtn.style.display = 'none';
            
            // Create player
            this.createPlayer(false); // No autoplay
            this.isActive = true;
        }

        playMobile() {
            // Одразу fullscreen на мобільному
            this.bgContainer?.classList.add('is-hidden');
            this.videoContainer.style.display = 'block';
            this.playBtn.style.display = 'none';
            
            // Create player з autoplay
            this.createPlayer(true);
            
            // Спробувати відкрити fullscreen
            setTimeout(() => {
                if (this.iframe) {
                    fullscreenAPI.request(this.iframe)
                        .catch(err => console.warn('Fullscreen denied:', err));
                }
            }, 500);
            
            this.isActive = true;
        }

        createPlayer(autoplay = false) {
            if (this.iframe) {
                console.log('Player already exists');
                return;
            }

            try {
                const baseUrl = 'https://iframe.mediadelivery.net/embed';
                const params = new URLSearchParams({
                    autoplay: autoplay ? 'true' : 'false',
                    preload: 'false',
                    responsive: 'true'
                });
                
                const iframeUrl = `${baseUrl}/${this.libraryId}/${this.videoId}?${params}`;

                this.iframe = document.createElement('iframe');
                this.iframe.src = iframeUrl;
                this.iframe.allow = 'accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture; fullscreen';
                this.iframe.allowFullscreen = true;
                this.iframe.style.cssText = 'width:100%;height:100%;border:0;';
                
                // Error handling
                this.iframe.addEventListener('error', () => this.showError());
                
                // Network timeout
                const loadTimeout = setTimeout(() => {
                    if (!this.iframe.contentWindow) {
                        this.showError();
                    }
                }, 10000); // 10 sec
                
                this.iframe.addEventListener('load', () => {
                    clearTimeout(loadTimeout);
                });

                this.playerWrapper.innerHTML = '';
                this.playerWrapper.appendChild(this.iframe);

                // Listen for video end через postMessage
                this.listenForVideoEvents();

            } catch (err) {
                console.error('❌ Player creation failed:', err);
                this.showError();
            }
        }

        listenForVideoEvents() {
            // BunnyNet може надсилати events через postMessage
            window.addEventListener('message', (event) => {
                // Validate origin
                if (!event.origin.includes('mediadelivery.net')) return;
                
                const data = event.data;
                
                // Handle video ended
                if (data && (data.event === 'ended' || data.type === 'ended')) {
                    console.log('✅ Video ended');
                    this.handleClose();
                }
            });
            
            // Fullscreen exit listener
            const fullscreenChange = () => {
                if (!fullscreenAPI.element && this.isActive) {
                    console.log('Exited fullscreen, player stays in Hero');
                    // На мобільному при виході з fullscreen - закрити
                    if (isMobile()) {
                        this.handleClose();
                    }
                }
            };
            
            document.addEventListener('fullscreenchange', fullscreenChange);
            document.addEventListener('webkitfullscreenchange', fullscreenChange);
            document.addEventListener('mozfullscreenchange', fullscreenChange);
            document.addEventListener('MSFullscreenChange', fullscreenChange);
        }

        handleClose() {
            // Reset state
            this.videoContainer.style.display = 'none';
            this.bgContainer?.classList.remove('is-hidden');
            this.playBtn.style.display = 'block';

            // Remove iframe
            if (this.iframe) {
                this.iframe.src = '';
                this.iframe.remove();
                this.iframe = null;
            }

            this.isActive = false;
            console.log('✅ Video closed');
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

