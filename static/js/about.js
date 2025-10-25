/**
 * About Page Functionality
 * Про Play Vision - Навігатор футбольного розвитку
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

    // Intersection Observer для анімацій появи секцій
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Спостерігаємо за секціями
    const sections = document.querySelectorAll(
        '.hero-section, .why-born-section, .mission-philosophy-section, .values-section, .team-section'
    );
    sections.forEach(section => observer.observe(section));

    // Трикутник - інтерактивні ефекти
    const triangleSvg = document.querySelector('.triangle-svg');
    const triangleLabels = document.querySelectorAll('.triangle-label');

    if (triangleSvg && triangleLabels.length > 0) {
        triangleLabels.forEach(label => {
            label.addEventListener('mouseenter', function () {
                triangleSvg.style.filter = 'drop-shadow(0 16px 32px rgba(255, 107, 53, 0.4))';
            });

            label.addEventListener('mouseleave', function () {
                triangleSvg.style.filter = 'drop-shadow(0 8px 16px rgba(255, 107, 53, 0.2))';
            });

            // Клік ефект
            label.addEventListener('click', function () {
                this.style.transform = this.style.transform.includes('scale') ? '' : 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });
        });
    }

    // Цінності - анімація появи з затримкою
    const valueCircles = document.querySelectorAll('.value-circle');
    const valueObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-in');
                }, index * 100);
            }
        });
    }, { threshold: 0.3 });

    valueCircles.forEach(circle => valueObserver.observe(circle));

    // MPV Cards - анімація появи
    const mpvCards = document.querySelectorAll('.mpv-card');
    const mpvObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-in');
                }, index * 150);
            }
        });
    }, { threshold: 0.2 });

    mpvCards.forEach(card => mpvObserver.observe(card));

    // Експерти - анімація появи
    const expertCards = document.querySelectorAll('.expert-card');
    const expertObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-in');
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });

    expertCards.forEach(card => expertObserver.observe(card));

    // Lazy loading для зображень
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.addEventListener('load', () => {
                    img.style.opacity = '1';
                });
                imageObserver.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
        imageObserver.observe(img);
    });

    // Fallback для зображень експертів
    const expertImages = document.querySelectorAll('.expert-image img');
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

    // Touch оптимізація для мобільних пристроїв
    if ('ontouchstart' in window) {
        const touchElements = document.querySelectorAll(
            '.value-circle, .expert-card, .mpv-card, .triangle-label'
        );

        touchElements.forEach(element => {
            element.addEventListener('touchstart', function () {
                this.style.opacity = '0.8';
            }, { passive: true });

            element.addEventListener('touchend', function () {
                this.style.opacity = '1';
            }, { passive: true });
        });
    }

    // Відео placeholder - додати анімацію пульсації
    const videoPlaceholder = document.querySelector('.video-placeholder');
    if (videoPlaceholder) {
        const videoIcon = videoPlaceholder.querySelector('.video-icon');
        if (videoIcon) {
            setInterval(() => {
                videoIcon.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    videoIcon.style.transform = 'scale(1)';
                }, 500);
            }, 3000);
        }
    }

    // Parallax ефект для hero section (легкий)
    const heroSection = document.querySelector('.hero-section');
    if (heroSection && window.innerWidth > 768) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * 0.3;
            heroSection.style.transform = `translateY(${rate}px)`;
        }, { passive: true });
    }

    // Лічильник для статистики (якщо буде додано в майбутньому)
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = Math.round(target);
                clearInterval(timer);
            } else {
                element.textContent = Math.round(start);
            }
        }, 16);
    }

    // Кастомна анімація для problem list
    const problemItems = document.querySelectorAll('.problem-item');
    const problemObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, index * 200);
            }
        });
    }, { threshold: 0.5 });

    problemItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        item.style.transition = 'all 0.5s ease';
        problemObserver.observe(item);
    });

    // Performance optimization - відключити анімації при низькій продуктивності
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.querySelectorAll('.animate-in').forEach(el => {
            el.style.animation = 'none';
        });
    }

    console.log('✅ About page initialized');
});
