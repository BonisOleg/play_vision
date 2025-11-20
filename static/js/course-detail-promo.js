/**
 * Course Detail Promo Video Logic
 * Handles promo modal and after-video popup
 */

document.addEventListener('DOMContentLoaded', function() {
    const openModalBtn = document.querySelector('[data-open-promo-modal]');
    const modal = document.getElementById('promoModal');
    const videoFrame = document.getElementById('promoVideoFrame');
    const popup = document.getElementById('afterPromoPopup');
    
    if (!openModalBtn || !modal || !videoFrame || !popup) {
        return; // Elements not found
    }
    
    // Get Bunny Library ID from body data attribute
    const bunnyLibraryId = document.body.dataset.bunnyLibraryId || '';
    
    let videoWatched = false;
    
    // Open modal
    openModalBtn.addEventListener('click', function() {
        const bunnyId = this.dataset.bunnyId;
        if (!bunnyId) {
            console.error('Bunny video ID not found');
            return;
        }
        
        // Build embed URL
        const embedUrl = `https://iframe.mediadelivery.net/embed/${bunnyLibraryId}/${bunnyId}?autoplay=true`;
        videoFrame.src = embedUrl;
        
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');
        
        // Track video end (approximate - через таймер)
        trackVideoEnd();
    });
    
    // Close modal handlers
    const closeModalElements = modal.querySelectorAll('[data-close-modal]');
    closeModalElements.forEach(el => {
        el.addEventListener('click', closeModal);
    });
    
    function closeModal() {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        videoFrame.src = ''; // Stop video
        document.body.classList.remove('modal-open');
        
        // Show popup if video was watched
        if (videoWatched) {
            showPopup();
        }
    }
    
    // Close popup handlers
    const closePopupElements = popup.querySelectorAll('[data-close-popup]');
    closePopupElements.forEach(el => {
        el.addEventListener('click', closePopup);
    });
    
    function closePopup() {
        popup.style.display = 'none';
        videoWatched = false; // Reset
    }
    
    function showPopup() {
        popup.style.display = 'flex';
    }
    
    /**
     * Track video end
     * Простий варіант через таймер (30 секунд)
     * TODO: Покращити через Bunny Player API postMessage
     */
    function trackVideoEnd() {
        // Показати popup через 30 секунд (typical promo length)
        setTimeout(() => {
            videoWatched = true;
        }, 30000); // 30 seconds
        
        // TODO: Альтернатива через Bunny Player API:
        // window.addEventListener('message', function(event) {
        //     if (event.origin === 'https://iframe.mediadelivery.net') {
        //         try {
        //             const data = JSON.parse(event.data);
        //             if (data.event === 'ended') {
        //                 videoWatched = true;
        //             }
        //         } catch (e) {
        //             console.error('Error parsing video message:', e);
        //         }
        //     }
        // });
    }
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (modal.style.display === 'flex') {
                closeModal();
            }
            if (popup.style.display === 'flex') {
                closePopup();
            }
        }
    });
});

