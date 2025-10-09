/**
 * Home Page Components
 */

// Hero Carousel (7 слайдів)
function heroCarousel() {
    return {
        currentSlide: 0,
        slides: [
            {
                title: 'Продуктивна практика у футбольних клубах',
                subtitle: 'Реальні кейси, стажування та менторинг з професіоналами індустрії',
                ctaUrl: '/about/'
            },
            {
                title: 'Ми відкрились!',
                subtitle: 'Приєднуйтесь до спільноти футбольних професіоналів України',
                ctaUrl: '/about/'
            },
            {
                title: 'Івенти',
                subtitle: 'Вебінари, майстер-класи та форуми від міжнародних експертів',
                ctaUrl: '/events/'
            },
            {
                title: 'Хаб знань — долучайся першим',
                subtitle: 'Ексклюзивні курси та матеріали для розвитку футбольних фахівців',
                ctaUrl: '/hub/'
            },
            {
                title: 'Ментор-коучинг',
                subtitle: 'Індивідуальний підхід до комплексного розвитку кожного футболіста',
                ctaUrl: '/mentor-coaching/'
            },
            {
                title: 'Про нас',
                subtitle: 'Дізнайтеся більше про нашу місію, цінності та команду експертів',
                ctaUrl: '/about/'
            },
            {
                title: 'Напрямки діяльності',
                subtitle: '4 ключових напрямки для професійного зростання у футболі',
                ctaUrl: '/about/#directions'
            }
        ],

        init() {
            // Автопрокрутка кожні 5 секунд
            setInterval(() => {
                this.nextSlide();
            }, 5000);
        },

        nextSlide() {
            this.currentSlide = (this.currentSlide + 1) % this.slides.length;
        }
    };
}

// Courses Carousel (6 курсів)
function coursesCarousel() {
    return {
        currentIndex: 0,
        slidesPerView: 3,
        totalSlides: 6,

        get slideWidth() {
            return 100 / this.slidesPerView;
        },

        get maxIndex() {
            return Math.max(0, this.totalSlides - this.slidesPerView);
        },

        init() {
            this.updateSlidesPerView();
            window.addEventListener('resize', () => this.updateSlidesPerView());
        },

        updateSlidesPerView() {
            if (window.innerWidth < 768) {
                this.slidesPerView = 1;
            } else if (window.innerWidth < 1024) {
                this.slidesPerView = 2;
            } else {
                this.slidesPerView = 3;
            }
        },

        nextSlide() {
            if (this.currentIndex < this.maxIndex) {
                this.currentIndex++;
            }
        },

        prevSlide() {
            if (this.currentIndex > 0) {
                this.currentIndex--;
            }
        }
    };
}
