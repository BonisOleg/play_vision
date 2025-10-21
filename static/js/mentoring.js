/**
 * Ментор-коучинг сторінка - інтерактивність
 */

document.addEventListener('DOMContentLoaded', () => {
    // Анімація появи карток при скролі
    const observeElements = () => {
        const elements = document.querySelectorAll('.hexagon-card, .principle-card, .role-card');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(20px)';

                    setTimeout(() => {
                        entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 100);

                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        elements.forEach(el => observer.observe(el));
    };

    // Викликати тільки якщо prefers-reduced-motion НЕ активний
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        observeElements();
    }

    // Плавний скрол до секцій
    const smoothScroll = () => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href !== '#') {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    };

    smoothScroll();
});

