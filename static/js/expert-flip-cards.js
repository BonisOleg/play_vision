/**
 * Expert Flip Cards
 * Обробка перегортання карток експертів
 */

class ExpertFlipCards {
    constructor() {
        this.cards = document.querySelectorAll('.expert-card');
        this.init();
    }

    init() {
        if (!this.cards.length) return;

        this.cards.forEach(card => {
            card.addEventListener('click', (e) => this.handleCardClick(e, card));
            this.addTouchSupport(card);
        });
    }

    handleCardClick(event, card) {
        // Перевіряємо чи клік не на посилання
        if (event.target.tagName === 'A') {
            event.preventDefault();
        }

        // Запобігаємо подвійному спрацьовуванню для текстового посилання
        if (event.target.classList.contains('expert-detail-link')) {
            event.stopPropagation();
        }

        // Toggle класу flipped
        card.classList.toggle('flipped');
    }

    // Метод для програмного перевертання картки
    flipCard(cardElement) {
        if (cardElement && cardElement.classList.contains('expert-card')) {
            cardElement.classList.toggle('flipped');
        }
    }

    // Метод для скидання всіх карток до початкового стану
    resetAllCards() {
        this.cards.forEach(card => {
            card.classList.remove('flipped');
        });
    }

    // Метод для перевертання картки за ID
    flipCardById(expertId) {
        const card = document.querySelector(`.expert-card[data-expert-id="${expertId}"]`);
        if (card) {
            this.flipCard(card);
        }
    }

    // Метод для обробки touch-подій на мобільних пристроях
    addTouchSupport(card) {
        let touchStartX = 0;
        let touchStartY = 0;
        let touchStartTime = 0;
        let isMoved = false;

        card.addEventListener('touchstart', (e) => {
            // Якщо touch на посиланні - пропустити
            if (e.target.tagName === 'A' || e.target.classList.contains('expert-detail-link')) {
                return;
            }

            // БЛОКУЄМО scroll на Android (критично для Android Chrome)
            e.preventDefault();
            
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            touchStartTime = Date.now();
            isMoved = false;
        }, { passive: false });

        card.addEventListener('touchmove', (e) => {
            if (!isMoved) {
                const currentX = e.touches[0].clientX;
                const currentY = e.touches[0].clientY;
                const deltaX = Math.abs(currentX - touchStartX);
                const deltaY = Math.abs(currentY - touchStartY);
                
                // Якщо це малий рух (можливо tap) - блокуємо scroll
                // Поріг 20px для підтримки обох платформ (iPhone та Android)
                if (deltaX < 20 && deltaY < 20) {
                    e.preventDefault();
                }
            }
            // Відмічаємо що був рух
            isMoved = true;
        }, { passive: false });

        card.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            const touchDuration = Date.now() - touchStartTime;

            const deltaX = Math.abs(touchEndX - touchStartX);
            const deltaY = Math.abs(touchEndY - touchStartY);

            // Якщо це tap: швидкий (< 300ms) і без значного руху (< 20px)
            if (touchDuration < 300 && deltaX < 20 && deltaY < 20) {
                // БЛОКУЄМО спливання до каруселі
                e.stopPropagation();
                e.preventDefault();
                
                // Перегорнути картку
                card.classList.toggle('flipped');
            }
            // Якщо був рух (isMoved = true) - це swipe, дозволяємо каруселі обробити
            // НЕ викликаємо stopPropagation() - дозволяємо події спливти до каруселі
        }, { passive: false });
    }
}

// Ініціалізація при завантаженні DOM
document.addEventListener('DOMContentLoaded', () => {
    const expertFlipCards = new ExpertFlipCards();

    // Експортуємо в глобальну область для можливого доступу ззовні
    window.expertFlipCards = expertFlipCards;
});

