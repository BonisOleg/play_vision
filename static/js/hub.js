/**
 * Hub Knowledge Base Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
    // Перевірити чи банер був закритий
    const bannerClosed = localStorage.getItem('banner_closed');
    if (bannerClosed === 'true') {
        const banner = document.getElementById('subscription-banner');
        if (banner) {
            banner.style.display = 'none';
        }
    }
});
