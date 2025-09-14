// About page JavaScript functionality

// Expert quotes carousel
function quotesCarousel() {
    return {
        currentQuote: 0,
        quotes: [
            {
                text: "Найважливіше в футболі — це не фізичні дані, а розуміння гри та прийняття правильних рішень.",
                name: "Dr. Fabian Otte",
                title: "Фахівець з розвитку навичок",
                avatar: "/static/images/experts/fabian-otte.jpg"
            },
            {
                text: "Сучасний футбол вимагає системного підходу до підготовки гравців на всіх рівнях.",
                name: "Dr. Adam Owen",
                title: "Експерт з методології тренувань",
                avatar: "/static/images/experts/adam-owen.jpg"
            },
            {
                text: "Фізіологічні принципи є основою для ефективного тренувального процесу.",
                name: "Prof. Hassane Zouhal",
                title: "Професор спортивної фізіології",
                avatar: "/static/images/experts/hassane-zouhal.jpg"
            },
            {
                text: "Правильне харчування та відновлення — половина успіху в професійному футболі.",
                name: "Dr. Raphael Villatore",
                title: "Лікар спортивної медицини",
                avatar: "/static/images/experts/raphael-villatore.jpg"
            }
        ],

        init() {
            // Auto-rotate quotes every 10 seconds as specified in requirements
            setInterval(() => {
                this.nextQuote();
            }, 10000);
        },

        nextQuote() {
            this.currentQuote = (this.currentQuote + 1) % this.quotes.length;
        },

        prevQuote() {
            this.currentQuote = this.currentQuote === 0 ? this.quotes.length - 1 : this.currentQuote - 1;
        }
    }
}

// Main materials carousel
function materialsCarousel() {
    return {
        currentMaterial: 0,
        materials: [
            {
                title: "Тренерські принципи",
                description: "Основи ефективного коучингу та методології тренувального процесу від провідних експертів світу.",
                image: "/static/images/courses/coaching-principles.jpg",
                duration: "8 годин",
                price: "₴1,200",
                badge: "Топ продажів"
            },
            {
                title: "Спортивна фізіологія",
                description: "Науковий підхід до фізичної підготовки та відновлення спортсменів для максимальної ефективності.",
                image: "/static/images/courses/sports-physiology.jpg",
                duration: "12 годин",
                price: "₴1,800",
                badge: "Новинка"
            },
            {
                title: "Скаутинг та аналітика",
                description: "Сучасні методи аналізу гри та пошуку талантів з використанням найновіших технологій.",
                image: "/static/images/courses/scouting-analytics.jpg",
                duration: "6 годин",
                price: "₴900",
                badge: "Для вас"
            },
            {
                title: "Тактична підготовка",
                description: "Глибокий аналіз тактичних схем та їх практичне застосування в ігровій діяльності.",
                image: "/static/images/courses/tactical-preparation.jpg",
                duration: "10 годин",
                price: "₴1,500",
                badge: "Вічна класика"
            },
            {
                title: "Психологія в футболі",
                description: "Ментальна підготовка гравців та управління командною динамікою для досягнення результатів.",
                image: "/static/images/courses/football-psychology.jpg",
                duration: "5 годин",
                price: "₴800",
                badge: "Рекомендуємо"
            }
        ],

        init() {
            // Auto-rotate materials every 20 seconds
            setInterval(() => {
                this.nextMaterial();
            }, 20000);
        },

        nextMaterial() {
            this.currentMaterial = (this.currentMaterial + 1) % this.materials.length;
        },

        prevMaterial() {
            this.currentMaterial = this.currentMaterial === 0 ? this.materials.length - 1 : this.currentMaterial - 1;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('About page loaded');

    // Smooth scrolling for anchor links
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

    // Intersection Observer for animations
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

    // Observe sections for animations
    document.querySelectorAll('.mission-section, .triangle-section, .values-section, .knowledge-hub-section').forEach(section => {
        observer.observe(section);
    });

    // Triangle interaction effects
    const triangleSvg = document.querySelector('.triangle-svg');
    const triangleLabels = document.querySelectorAll('.triangle-label');

    // Add hover effects to triangle labels
    triangleLabels.forEach(label => {
        label.addEventListener('mouseenter', function () {
            triangleSvg.style.filter = 'drop-shadow(0 16px 32px rgba(255, 107, 53, 0.4))';

            // Highlight corresponding part of triangle
            const triangleInnerLines = triangleSvg.querySelectorAll('.triangle-inner-line');
            triangleInnerLines.forEach(line => {
                line.style.opacity = '1';
                line.style.strokeWidth = '3';
            });
        });

        label.addEventListener('mouseleave', function () {
            triangleSvg.style.filter = '';

            const triangleInnerLines = triangleSvg.querySelectorAll('.triangle-inner-line');
            triangleInnerLines.forEach(line => {
                line.style.opacity = '';
                line.style.strokeWidth = '';
            });
        });

        // Add click interaction
        label.addEventListener('click', function () {
            // Add click ripple effect
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

    // Value circles animation on scroll
    const valueCircles = document.querySelectorAll('.value-circle');
    const valueObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                }, index * 100);
            }
        });
    }, { threshold: 0.3 });

    valueCircles.forEach(circle => {
        valueObserver.observe(circle);
    });
});

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.8s ease-out forwards;
    }
    
    /* Lazy loading for images */
    img[loading="lazy"] {
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    img[loading="lazy"].loaded {
        opacity: 1;
    }
`;
document.head.appendChild(style);

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function () {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');

    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.addEventListener('load', () => {
                    img.classList.add('loaded');
                });
                imageObserver.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });
});

// Fallback images for experts (if images don't exist)
document.addEventListener('DOMContentLoaded', function () {
    const expertImages = document.querySelectorAll('.author-avatar img');

    expertImages.forEach(img => {
        img.addEventListener('error', function () {
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMzAiIGZpbGw9IiNmNWY1ZjUiLz4KPHN2ZyB4PSIxNSIgeT0iMTAiIHdpZHRoPSIzMCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSIjOTk5Ij4KPHA+aDpwYXRoIGQ9Ik0xMiAxMmMyLjIxIDAgNC0xLjc5IDQtNHMtMS43OS00LTQtNC00IDEuNzktNCA0IDEuNzkgNCA0IDR6bTAgMmMtMi42NyAwLTggMS4zNC04IDRtMTIgNGMwLTIuNjctNS4zMy00LTgtNHoiLz4KPC9zdmc+';
        });
    });
});

// Mobile menu enhancements for touch devices
if ('ontouchstart' in window) {
    document.addEventListener('DOMContentLoaded', function () {
        // Add touch-friendly interactions
        const touchElements = document.querySelectorAll('.triangle-point, .value-circle, .material-card');

        touchElements.forEach(element => {
            element.addEventListener('touchstart', function () {
                this.style.transform = this.style.transform + ' scale(0.95)';
            });

            element.addEventListener('touchend', function () {
                this.style.transform = this.style.transform.replace(' scale(0.95)', '');
            });
        });
    });
}
