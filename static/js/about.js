/**
 * About Page Functionality
 * Про нас - Чиста версія без паралакс ефектів
 */

document.addEventListener('DOMContentLoaded', function () {

    // Smooth scrolling для якорних посилань
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Lazy loading для зображень через IntersectionObserver
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    if ('IntersectionObserver' in window) {
        const lazyImageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.classList.add('lazy-loaded');
                    lazyImageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => {
            lazyImageObserver.observe(img);
        });
    }

    // Fallback для зображень експертів
    const expertImages = document.querySelectorAll('.expert-photo img');
    expertImages.forEach(img => {
        img.addEventListener('error', function () {
            const placeholder = document.createElement('div');
            placeholder.className = 'expert-placeholder';
            placeholder.innerHTML = `
                <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
                    <circle cx="40" cy="40" r="38" fill="#f5f5f5"/>
                    <circle cx="40" cy="30" r="12" fill="#999"/>
                    <path d="M20 60C20 50 28 45 40 45C52 45 60 50 60 60" fill="#999"/>
                </svg>
            `;
            this.parentElement.replaceChild(placeholder, this);
        });
    });

    console.log('✅ About page initialized successfully');
});
