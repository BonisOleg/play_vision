/**
 * About Page Functionality
 * Vanilla JS без Alpine.js, без конфліктів з CSS
 */

class QuotesCarousel {
    constructor(element) {
        this.element = element;
        this.currentQuote = 0;
        this.quotes = [
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
        ];

        this.init();
    }

    init() {
        this.render();
        setInterval(() => this.nextQuote(), 10000);
    }

    render() {
        const quote = this.quotes[this.currentQuote];
        const textEl = this.element.querySelector('.quote-text');
        const nameEl = this.element.querySelector('.quote-name');
        const titleEl = this.element.querySelector('.quote-title');

        if (textEl) textEl.textContent = quote.text;
        if (nameEl) nameEl.textContent = quote.name;
        if (titleEl) titleEl.textContent = quote.title;
    }

    nextQuote() {
        this.currentQuote = (this.currentQuote + 1) % this.quotes.length;
        this.render();
    }

    prevQuote() {
        this.currentQuote = this.currentQuote === 0 ? this.quotes.length - 1 : this.currentQuote - 1;
        this.render();
    }
}

class MaterialsCarousel {
    constructor(element) {
        this.element = element;
        this.currentMaterial = 0;
        this.materials = [
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
        ];

        this.init();
    }

    init() {
        this.render();
        setInterval(() => this.nextMaterial(), 20000);
    }

    render() {
        const material = this.materials[this.currentMaterial];
        const titleEl = this.element.querySelector('.material-title');
        const descEl = this.element.querySelector('.material-description');

        if (titleEl) titleEl.textContent = material.title;
        if (descEl) descEl.textContent = material.description;
    }

    nextMaterial() {
        this.currentMaterial = (this.currentMaterial + 1) % this.materials.length;
        this.render();
    }

    prevMaterial() {
        this.currentMaterial = this.currentMaterial === 0 ? this.materials.length - 1 : this.currentMaterial - 1;
        this.render();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
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
    const sections = document.querySelectorAll('.mission-section, .triangle-section, .values-section, .knowledge-hub-section');
    sections.forEach(section => observer.observe(section));

    // Triangle interaction effects - використовуємо CSS класи замість маніпуляції style
    const triangleSvg = document.querySelector('.triangle-svg');
    const triangleLabels = document.querySelectorAll('.triangle-label');

    triangleLabels.forEach(label => {
        label.addEventListener('mouseenter', function () {
            triangleSvg?.classList.add('triangle-highlighted');
        });

        label.addEventListener('mouseleave', function () {
            triangleSvg?.classList.remove('triangle-highlighted');
        });

        // Touch feedback через CSS класи
        label.addEventListener('click', function () {
            this.classList.add('label-clicked');
            setTimeout(() => {
                this.classList.remove('label-clicked');
            }, 150);
        });
    });

    // Value circles animation on scroll - використовуємо CSS класи
    const valueCircles = document.querySelectorAll('.value-circle');
    const valueObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-fade-in-up');
                }, index * 100);
            }
        });
    }, { threshold: 0.3 });

    valueCircles.forEach(circle => valueObserver.observe(circle));

    // Lazy loading for images
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

    lazyImages.forEach(img => imageObserver.observe(img));

    // Fallback images for experts
    const expertImages = document.querySelectorAll('.author-avatar img');
    expertImages.forEach(img => {
        img.addEventListener('error', function () {
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMzAiIGZpbGw9IiNmNWY1ZjUiLz4KPHN2ZyB4PSIxNSIgeT0iMTAiIHdpZHRoPSIzMCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSIjOTk5Ij4KPHA+aDpwYXRoIGQ9Ik0xMiAxMmMyLjIxIDAgNC0xLjc5IDQtNHMtMS43OS00LTQtNC00IDEuNzktNCA0IDEuNzkgNCA0IDR6bTAgMmMtMi42NyAwLTggMS4zNC04IDRtMTIgNGMwLTIuNjctNS4zMy00LTgtNHoiLz4KPC9zdmc+';
        });
    });

    // Touch device optimization - використовуємо CSS класи
    if ('ontouchstart' in window) {
        const touchElements = document.querySelectorAll('.triangle-point, .value-circle, .material-card');

        touchElements.forEach(element => {
            element.addEventListener('touchstart', function () {
                this.classList.add('touch-active');
            });

            element.addEventListener('touchend', function () {
                this.classList.remove('touch-active');
            });
        });
    }

    // Ініціалізуємо карусель якщо є
    const quotesElement = document.querySelector('.quotes-carousel');
    if (quotesElement) {
        new QuotesCarousel(quotesElement);
    }

    const materialsElement = document.querySelector('.materials-carousel');
    if (materialsElement) {
        new MaterialsCarousel(materialsElement);
    }
});
