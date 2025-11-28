/**
 * About Hero - BunnyNet Video Player
 * iOS Safari fix: Create iframe ONLY on user click, not on page load
 */

(function() {
    'use strict';
    
    class AboutHeroVideoPlayer {
        constructor() {
            this.section = document.querySelector('.about-hero-section');
            if (!this.section) {
                console.warn('❌ Hero section not found');
                return;
            }
            
            this.libraryId = this.section.dataset.videoLibrary;
            this.videoId = this.section.dataset.videoId;
            
            if (!this.libraryId || !this.videoId) {
                console.warn('❌ Video IDs missing');
                return;
            }
            
            this.playerWrapper = this.section.querySelector('.bunny-player-container');
            if (!this.playerWrapper) {
                console.warn('❌ Player wrapper not found');
                return;
            }
            
            this.iframe = null;
            this.init();
        }
        
        init() {
            console.log('📺 Video config ready:', { libraryId: this.libraryId, videoId: this.videoId });
            
            // На iOS потребуємо user interaction - слухаємо перший клік на контейнер
            this.section.addEventListener('click', () => this.handleFirstClick(), { once: true });
            console.log('✅ Ready to create player on first click');
        }
        
        handleFirstClick() {
            console.log('🎬 Creating player on user click (iOS compatible)');
            this.createPlayer();
        }
        
        createPlayer() {
            if (this.iframe) {
                console.log('⚠️ Player already exists');
                return;
            }
            
            try {
                const baseUrl = 'https://iframe.mediadelivery.net/embed';
                const params = new URLSearchParams({
                    autoplay: 'true',
                    preload: 'false',
                    responsive: 'true'
                });
                
                const iframeUrl = `${baseUrl}/${this.libraryId}/${this.videoId}?${params}`;
                
                this.iframe = document.createElement('iframe');
                this.iframe.src = iframeUrl;
                this.iframe.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media; accelerometer; gyroscope';
                this.iframe.allowFullscreen = true;
                this.iframe.webkitAllowFullscreen = true;
                this.iframe.setAttribute('playsinline', '');
                this.iframe.setAttribute('webkit-playsinline', 'true');
                this.iframe.style.cssText = 'width:100%;height:100%;border:0;display:block;';
                
                this.playerWrapper.innerHTML = '';
                this.playerWrapper.appendChild(this.iframe);
                
                console.log('✅ BunnyNet player created and appended');
                console.log('📹 Iframe src:', iframeUrl);
                
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
