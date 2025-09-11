document.addEventListener('DOMContentLoaded', function () {

    // Initialize Alpine.js data for hero slider if exists
    if (typeof Alpine !== 'undefined' && document.querySelector('.hero-section')) {
        // Auto-advance hero slider with better performance
        const heroSlider = {
            currentSlide: 0,
            maxSlides: 4,
            interval: null,

            start() {
                this.interval = setInterval(() => {
                    this.nextSlide();
                }, 5000);
            },

            stop() {
                if (this.interval) {
                    clearInterval(this.interval);
                    this.interval = null;
                }
            },

            nextSlide() {
                this.currentSlide = (this.currentSlide + 1) % this.maxSlides;
                this.updateDots();
            },

            goToSlide(index) {
                this.currentSlide = index;
                this.updateDots();
            },

            updateDots() {
                const dots = document.querySelectorAll('.slider-dot');
                dots.forEach((dot, index) => {
                    dot.classList.toggle('active', index === this.currentSlide);
                });
            }
        };

        // Start slider only if hero section is visible
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            heroSlider.start();

            // Add click listeners to dots
            const dots = document.querySelectorAll('.slider-dot');
            dots.forEach((dot, index) => {
                dot.addEventListener('click', () => {
                    heroSlider.goToSlide(index);
                });
            });
        }
    }

    // Optimized intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                // Unobserve after animation to improve performance
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe sections for animations (exclude CTA section to prevent flickering)
    const sections = document.querySelectorAll('.fullscreen-section:not(.cta-section)');
    sections.forEach(section => {
        observer.observe(section);
    });

    // Removed scroll hijacking - let browser handle natural scrolling

    // Handle video loading optimization
    const heroVideo = document.querySelector('.section-bg-video');
    if (heroVideo) {
        // Only autoplay on desktop and if user prefers motion
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const isMobile = window.innerWidth < 768;

        if (prefersReducedMotion || isMobile) {
            heroVideo.removeAttribute('autoplay');
            heroVideo.pause();
        }

        // Preload only on fast connections
        if ('connection' in navigator) {
            const connection = navigator.connection;
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                heroVideo.removeAttribute('preload');
                heroVideo.preload = 'none';
            }
        }
    }

    // Simplified image loading for remaining lazy images
    const lazyImages = document.querySelectorAll('img[data-src]');
    if (lazyImages.length > 0) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (typeof heroSlider !== 'undefined' && heroSlider.stop) {
            heroSlider.stop();
        }
        if (typeof observer !== 'undefined') {
            observer.disconnect();
        }
        // imageObserver cleanup handled within its scope
    });
});
