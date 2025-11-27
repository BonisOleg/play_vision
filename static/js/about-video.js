/**
 * About Hero BunnyNet Video Player
 * Мінімальна версія - тільки відео
 */

(function() {
    'use strict';

    class AboutHeroVideoPlayer {
        constructor() {
            this.section = document.querySelector('.about-hero-section');
            if (!this.section) return;

            this.libraryId = this.section.dataset.videoLibrary;
            this.videoId = this.section.dataset.videoId;
            
            if (!this.libraryId || !this.videoId) {
                console.warn('⚠️ Video IDs missing');
                return;
            }

            this.playerContainer = document.getElementById('about-hero-player');
            if (!this.playerContainer) return;

            this.init();
        }

        init() {
            console.log('🎬 Initializing BunnyNet player');
            this.createPlayer();
        }

        createPlayer() {
            try {
                const baseUrl = 'https://iframe.mediadelivery.net/embed';
                const params = new URLSearchParams({
                    autoplay: 'false',
                    preload: 'false',
                    responsive: 'true'
                });
                
                const iframeUrl = `${baseUrl}/${this.libraryId}/${this.videoId}?${params}`;

                const iframe = document.createElement('iframe');
                iframe.src = iframeUrl;
                iframe.allow = 'accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture; fullscreen';
                iframe.allowFullscreen = true;
                iframe.webkitAllowFullscreen = true;
                iframe.style.cssText = 'width:100%;height:100%;border:0;';
                
                this.playerContainer.appendChild(iframe);
                console.log('✅ BunnyNet player created');

            } catch (err) {
                console.error('❌ Player creation failed:', err);
            }
        }
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', () => {
        new AboutHeroVideoPlayer();
    });

})();
