/**
 * Course Detail Promo Video - Popup після закінчення
 */

document.addEventListener('DOMContentLoaded', function() {
    const iframe = document.getElementById('promoVideoIframe');
    const popup = document.getElementById('afterPromoPopup');
    
    if (!iframe || !popup) {
        return;
    }
    
    let videoWatched = false;
    
    // Слухати повідомлення від Bunny Player (postMessage API)
    window.addEventListener('message', function(event) {
        // Перевірити що повідомлення від Bunny.net
        if (event.origin !== 'https://iframe.mediadelivery.net') {
            return;
        }
        
        try {
            const data = JSON.parse(event.data);
            
            // Bunny Player надсилає event: "ended" коли відео закінчилось
            if (data.event === 'ended' && !videoWatched) {
                videoWatched = true;
                showPopup();
            }
        } catch (e) {
            // Ignore parsing errors
        }
    });
    
    // Fallback: якщо postMessage не працює, показати через 60 секунд
    setTimeout(() => {
        if (!videoWatched) {
            videoWatched = true;
            showPopup();
        }
    }, 60000); // 60 секунд
    
    // Показати popup
    function showPopup() {
        popup.style.display = 'flex';
    }
    
    // Закрити popup
    const closePopupElements = popup.querySelectorAll('[data-close-popup]');
    closePopupElements.forEach(el => {
        el.addEventListener('click', closePopup);
    });
    
    function closePopup() {
        popup.style.display = 'none';
    }
    
    // Close on Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && popup.style.display === 'flex') {
            closePopup();
        }
    });
});
