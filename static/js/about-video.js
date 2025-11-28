/**
 * About Hero - BunnyNet Video Player
 * Універсальне рішення без розрізнення пристроїв
 */

(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', () => {
        const container = document.getElementById('about-hero-player');
        if (!container) {
            console.warn('❌ Video container not found');
            return;
        }
        
        const section = document.querySelector('.about-hero-section');
        if (!section) {
            console.warn('❌ Hero section not found');
            return;
        }
        
        const libraryId = section.dataset.videoLibrary;
        const videoId = section.dataset.videoId;
        
        console.log('📺 Video config:', { libraryId, videoId });
        
        if (!libraryId || !videoId) {
            console.warn('❌ Video IDs missing');
            return;
        }
        
        try {
            // Перевірка контейнеру ПЕРЕД додаванням
            const containerRect = container.getBoundingClientRect();
            const sectionRect = section.getBoundingClientRect();
            const containerStyles = window.getComputedStyle(container);
            const sectionStyles = window.getComputedStyle(section);
            
            console.log('📹 === CONTAINER INFO ===');
            console.log('📹 Container display:', containerStyles.display);
            console.log('📹 Container height (computed):', containerStyles.height);
            console.log('📹 Container width (computed):', containerStyles.width);
            console.log('📹 Container offsetHeight:', container.offsetHeight);
            console.log('📹 Container offsetWidth:', container.offsetWidth);
            console.log('📹 Container getBoundingClientRect:', {
                height: containerRect.height,
                width: containerRect.width,
                top: containerRect.top,
                left: containerRect.left
            });
            
            console.log('📹 === SECTION INFO ===');
            console.log('📹 Section display:', sectionStyles.display);
            console.log('📹 Section height (computed):', sectionStyles.height);
            console.log('📹 Section width (computed):', sectionStyles.width);
            console.log('📹 Section offsetHeight:', section.offsetHeight);
            console.log('📹 Section offsetWidth:', section.offsetWidth);
            console.log('📹 Section getBoundingClientRect:', {
                height: sectionRect.height,
                width: sectionRect.width,
                top: sectionRect.top,
                left: sectionRect.left
            });
            
            // Створюємо BunnyNet iframe
            const iframe = document.createElement('iframe');
            iframe.src = `https://iframe.mediadelivery.net/embed/${libraryId}/${videoId}?autoplay=false&preload=false&responsive=true`;
            iframe.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
            iframe.allowFullscreen = true;
            iframe.webkitAllowFullscreen = true; // iOS Safari
            iframe.setAttribute('playsinline', ''); // iOS inline playback
            iframe.setAttribute('webkit-playsinline', 'true'); // iOS Safari strict
            iframe.setAttribute('touch-action', 'manipulation'); // iOS touch events
            iframe.style.cssText = 'width:100%;height:100%;border:0;display:block;background:#000;pointer-events:auto;';
            
            container.appendChild(iframe);
            
            // Перевірка ПІСЛЯ додавання
            console.log('✅ BunnyNet player added to DOM');
            console.log('📹 Iframe in DOM:', container.contains(iframe));
            console.log('📹 Iframe src:', iframe.src);
            console.log('📹 Container children count:', container.children.length);
            
            // Перевірка після малої затримки
            setTimeout(() => {
                const iframeRect = iframe.getBoundingClientRect();
                const iframeStyles = window.getComputedStyle(iframe);
                console.log('⏱️ === IFRAME AFTER 100ms ===');
                console.log('⏱️ Iframe display:', iframeStyles.display);
                console.log('⏱️ Iframe height:', iframeStyles.height);
                console.log('⏱️ Iframe width:', iframeStyles.width);
                console.log('⏱️ Iframe getBoundingClientRect:', {
                    height: iframeRect.height,
                    width: iframeRect.width,
                    top: iframeRect.top,
                    left: iframeRect.left
                });
            }, 100);
            
        } catch (err) {
            console.error('❌ Failed to initialize player:', err);
            console.error('❌ Error stack:', err.stack);
        }
    });
})();
