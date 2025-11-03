/**
 * Mentoring Page Scripts
 * Обробка інтерактивності сторінки ментор-коучингу
 */

class MentoringPage {
    constructor() {
        this.contactButtons = document.querySelectorAll('.mentoring-btn');
        this.init();
    }

    init() {
        this.setupContactButtons();
        this.setupImageLazyLoading();
        this.setupScrollAnimations();
    }

    /**
     * Налаштування кнопок контакту
     */
    setupContactButtons() {
        if (!this.contactButtons.length) return;

        this.contactButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const buttonText = button.querySelector('.btn-text')?.textContent || '';
                this.handleContactClick(buttonText, button);
            });
        });
    }

    /**
     * Обробка кліку по кнопці контакту
     */
    handleContactClick(type, button) {
        console.log(`Клік по кнопці: ${type}`);
        
        // Додаємо візуальний фідбек
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
        }, 150);

        // Тут можна додати логіку відкриття модального вікна, форми тощо
        // Наприклад, показати alert або перенаправити
        // alert(`Скоро відкриється форма для ${type}`);
    }

    /**
     * Налаштування lazy loading для зображень
     */
    setupImageLazyLoading() {
        const images = document.querySelectorAll('.mentoring-card-image img, .mentoring-image-block img');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            images.forEach(img => imageObserver.observe(img));
        }
    }

    /**
     * Налаштування анімацій при скролі
     */
    setupScrollAnimations() {
        const sections = document.querySelectorAll('.mentoring-what-section, .mentoring-structure-section, .mentoring-methodology-section, .mentoring-team-section, .mentoring-contact-section');
        
        if ('IntersectionObserver' in window) {
            const sectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('section-visible');
                    }
                });
            }, {
                rootMargin: '-50px 0px',
                threshold: 0.1
            });

            sections.forEach(section => {
                section.classList.add('section-animated');
                sectionObserver.observe(section);
            });
        }
    }

    /**
     * Плавний скрол до секції
     */
    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
}

// Ініціалізація при завантаженні DOM
document.addEventListener('DOMContentLoaded', () => {
    const mentoringPage = new MentoringPage();
    
    // Експортуємо в глобальну область для можливого доступу ззовні
    window.mentoringPage = mentoringPage;
});

// Додаємо стилі для анімації скролу
const style = document.createElement('style');
style.textContent = `
    .section-animated {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }

    .section-animated.section-visible {
        opacity: 1;
        transform: translateY(0);
    }

    .mentoring-card-image img {
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .mentoring-card-image img.loaded {
        opacity: 1;
    }
`;

// Додаємо стилі тільки якщо їх ще немає
if (!document.getElementById('mentoring-animations-style')) {
    style.id = 'mentoring-animations-style';
    document.head.appendChild(style);
}

