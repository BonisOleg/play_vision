/**
 * About Page Functionality
 * Про нас - Навігатор футбольного розвитку
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
        '.about-hero, .about-triangle-section, .about-mission-section, .about-values-section, .about-team-section'
    );
    sections.forEach(section => observer.observe(section));

    // SVG Image blocks - анімація появи з затримкою
    const imageBlocks = document.querySelectorAll('.about-image-block');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 150);
            }
        });
    }, { threshold: 0.2 });

    imageBlocks.forEach(block => {
        block.style.opacity = '0';
        block.style.transform = 'translateY(20px)';
        block.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        imageObserver.observe(block);
    });

    // Експерти - анімація появи (якщо є expert-flip-cards.js, він подбає про це)
    const expertCards = document.querySelectorAll('.expert-card');
    if (expertCards.length > 0 && !window.expertFlipCardsInitialized) {
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
    }

    // Lazy loading для зображень
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    const lazyImageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.addEventListener('load', () => {
                    img.style.opacity = '1';
                });
                lazyImageObserver.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
        lazyImageObserver.observe(img);
    });

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

    // Touch оптимізація для мобільних пристроїв
    if ('ontouchstart' in window) {
        const touchElements = document.querySelectorAll(
            '.expert-card, .about-image-block'
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

    // Parallax ефект для hero section (легкий)
    const heroSection = document.querySelector('.about-hero');
    if (heroSection && window.innerWidth > 768) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * 0.3;
            if (scrolled < window.innerHeight) {
                heroSection.style.transform = `translateY(${rate}px)`;
            }
        }, { passive: true });
    }

    // Performance optimization - відключити анімації при низькій продуктивності
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.querySelectorAll('.animate-in, .about-image-block').forEach(el => {
            el.style.animation = 'none';
            el.style.transition = 'none';
        });
    }

    // Анімація заголовків при появі
    const sectionTitles = document.querySelectorAll('.section-title');
    const titleObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.5 });

    sectionTitles.forEach(title => {
        title.style.opacity = '0';
        title.style.transform = 'translateY(20px)';
        title.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        titleObserver.observe(title);
    });

    console.log('✅ About page initialized successfully');
});
