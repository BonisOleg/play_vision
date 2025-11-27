/**
 * About Hero - BunnyNet Video Player
 * Універсальне рішення без розрізнення пристроїв
 */

(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', () => {
        const container = document.getElementById('about-hero-player');
        if (!container) {
            console.warn('Video container not found');
            return;
        }
        
        const section = document.querySelector('.about-hero-section');
        if (!section) return;
        
        const libraryId = section.dataset.videoLibrary;
        const videoId = section.dataset.videoId;
        
        if (!libraryId || !videoId) {
            console.warn('Video IDs missing');
            return;
        }
        
        // Створюємо BunnyNet iframe
        const iframe = document.createElement('iframe');
        iframe.src = `https://iframe.mediadelivery.net/embed/${libraryId}/${videoId}?autoplay=false&preload=false&responsive=true`;
        iframe.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
        iframe.allowFullscreen = true;
        iframe.webkitAllowFullscreen = true; // iOS Safari
        iframe.setAttribute('playsinline', ''); // iOS inline playback
        iframe.setAttribute('webkit-playsinline', ''); // iOS Safari
        iframe.style.cssText = 'width:100%;height:100%;border:0;display:block;';
        
        container.appendChild(iframe);
        console.log('✅ BunnyNet player initialized');
    });
})();
