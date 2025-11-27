/**
 * About Hero BunnyNet Video Player
 * Покращена версія з Memory Leak fixes
 */

(function() {
    'use strict';

    // === UTILITIES ===
    const isMobile = () => {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
            || window.innerWidth < 768;
    };

    const fullscreenAPI = {
        request: (element) => {
            if (element.requestFullscreen) {
                return element.requestFullscreen();
            } else if (element.webkitRequestFullscreen) {
                return element.webkitRequestFullscreen();
            } else if (element.mozRequestFullScreen) {
                return element.mozRequestFullScreen();
            } else if (element.msRequestFullscreen) {
                return element.msRequestFullscreen();
            }
            return Promise.reject(new Error('Fullscreen not supported'));
        },
        exit: () => {
            if (document.fullscreenElement || document.webkitFullscreenElement 
                || document.mozFullScreenElement || document.msFullscreenElement) {
                if (document.exitFullscreen) {
                    return document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    return document.webkitExitFullscreen();
                } else if (document.mozCancelFullScreen) {
                    return document.mozCancelFullScreen();
                } else if (document.msExitFullscreen) {
                    return document.msExitFullscreen();
                }
            }
            return Promise.resolve();
        },
        get element() {
            return document.fullscreenElement 
                || document.webkitFullscreenElement 
                || document.mozFullScreenElement 
                || document.msFullscreenElement 
                || null;
        }
    };

    // === MAIN CLASS ===
    class AboutHeroVideoPlayer {
        constructor() {
            this.section = document.querySelector('.about-hero-section');
            if (!this.section) return;

            this.libraryId = this.section.dataset.videoLibrary;
            this.videoId = this.section.dataset.videoId;
            
            if (!this.libraryId || !this.videoId) {
                console.warn('⚠️ Video IDs missing for About Hero');
                return;
            }

            this.playerContainer = document.getElementById('about-hero-player');
            if (!this.playerContainer) {
                console.error('❌ Player container missing');
                return;
            }

            // State
            this.iframe = null;
            this.isActive = false;
            this.hasError = false;

            // Event listener references (для cleanup)
            this.boundMessageHandler = null;
            this.boundFullscreenChange = null;

            this.init();
        }

        init() {
            console.log('🎬 Initializing BunnyNet player');
            this.createPlayer();
        }

        createPlayer() {
            if (this.iframe) {
                console.log('⚠️ Player already exists, reusing');
                return;
            }

            const autoplay = isMobile();
            console.log(`📹 Creating player (autoplay: ${autoplay}, Mobile: ${isMobile()})`);

            try {
                // Validation
                if (!this.libraryId || !this.videoId) {
                    throw new Error('Missing library or video ID');
                }

                const baseUrl = 'https://iframe.mediadelivery.net/embed';
                const quality = isMobile() ? '720p' : 'auto';
                
                const params = new URLSearchParams({
                    autoplay: autoplay ? 'true' : 'false',
                    preload: 'false',
                    responsive: 'true',
                    quality: quality
                });
                
                const iframeUrl = `${baseUrl}/${this.libraryId}/${this.videoId}?${params}`;
                console.log('📺 Video URL constructed');

                this.iframe = document.createElement('iframe');
                this.iframe.src = iframeUrl;
                this.iframe.allow = 'accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture; fullscreen';
                this.iframe.allowFullscreen = true;
                this.iframe.webkitAllowFullscreen = true;
                this.iframe.setAttribute('playsinline', '');
                this.iframe.setAttribute('webkit-playsinline', '');
                this.iframe.style.cssText = 'width:100%;height:100%;border:0;position:absolute;top:0;left:0;';
                
                // Error event
                this.iframe.addEventListener('error', () => {
                    console.error('❌ Iframe error event');
                });
                
                // Load timeout (15s для 3G)
                const loadTimeout = setTimeout(() => {
                    if (!this.iframe.contentWindow) {
                        console.error('❌ Load timeout (15s)');
                    }
                }, 15000);
                
                this.iframe.addEventListener('load', () => {
                    clearTimeout(loadTimeout);
                    console.log('✅ Iframe loaded successfully');
                });

                this.playerContainer.innerHTML = '';
                this.playerContainer.appendChild(this.iframe);

                // Setup listeners
                this.listenForVideoEvents();

                console.log('✅ BunnyNet player created');
                this.isActive = true;

            } catch (err) {
                console.error('❌ Player creation failed:', err);
            }
        }

        listenForVideoEvents() {
            // Message handler for video events
            if (!this.boundMessageHandler) {
                this.boundMessageHandler = (event) => {
                    // Security check
                    if (!event.origin.includes('mediadelivery.net')) return;
                    
                    const data = event.data;
                    if (data && (data.event === 'ended' || data.type === 'ended')) {
                        console.log('✅ Video ended');
                        this.handleClose();
                    }
                };
                
                window.addEventListener('message', this.boundMessageHandler);
            }
            
            // Fullscreen change handler
            if (!this.boundFullscreenChange) {
                this.boundFullscreenChange = () => {
                    if (!fullscreenAPI.element && this.isActive) {
                        console.log('📹 Exited fullscreen');
                        
                        if (isMobile()) {
                            console.log('📱 Mobile: closing video');
                            this.handleClose();
                        } else {
                            console.log('🖥️ Desktop: video stays in player');
                        }
                    }
                };
                
                document.addEventListener('fullscreenchange', this.boundFullscreenChange);
                document.addEventListener('webkitfullscreenchange', this.boundFullscreenChange);
                document.addEventListener('mozfullscreenchange', this.boundFullscreenChange);
                document.addEventListener('MSFullscreenChange', this.boundFullscreenChange);
            }
        }

        handleClose() {
            console.log('🔴 Closing video player');
            
            // Exit fullscreen if active
            if (fullscreenAPI.element) {
                fullscreenAPI.exit()
                    .then(() => console.log('✅ Exited fullscreen'))
                    .catch(err => console.warn('⚠️ Fullscreen exit failed:', err));
            }
            
            // Remove iframe
            if (this.iframe) {
                this.iframe.src = '';
                this.iframe.remove();
                this.iframe = null;
            }
            
            if (this.playerContainer) {
                this.playerContainer.innerHTML = '';
            }

            // Cleanup listeners
            this.cleanup();

            // Reset state
            this.isActive = false;
            this.hasError = false;
            
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
            
            console.log('🧹 Event listeners cleaned up');
        }
    }

    // === INITIALIZATION ===
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🚀 About page loaded');
        new AboutHeroVideoPlayer();
    });

})();
