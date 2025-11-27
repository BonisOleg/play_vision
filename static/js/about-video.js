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
            // Створюємо BunnyNet iframe
            const iframe = document.createElement('iframe');
            iframe.src = `https://iframe.mediadelivery.net/embed/${libraryId}/${videoId}?autoplay=false&preload=false&responsive=true`;
            iframe.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
            iframe.allowFullscreen = true;
            iframe.webkitAllowFullscreen = true; // iOS Safari
            iframe.setAttribute('playsinline', ''); // iOS inline playback
            iframe.setAttribute('webkit-playsinline', ''); // iOS Safari strict
            iframe.setAttribute('muted', ''); // For autoplay
            iframe.style.cssText = 'width:100%;height:100%;border:0;display:block;background:#000;';
            
            // Перевірка перед добавленням
            console.log('📹 Container height:', window.getComputedStyle(container).height);
            console.log('📹 Container width:', window.getComputedStyle(container).width);
            
            container.appendChild(iframe);
            console.log('✅ BunnyNet player initialized successfully');
            console.log('📹 Iframe src:', iframe.src);
            
        } catch (err) {
            console.error('❌ Failed to initialize player:', err);
        }
    });
})();
