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
        });
    }

    handleCardClick(event, card) {
        // Перевіряємо чи клік не на посилання
        if (event.target.tagName === 'A') {
            event.preventDefault();
        }

        // Запобігаємо подвійному спрацьовуванню для кнопки
        if (event.target.classList.contains('expert-detail-btn')) {
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
}

// Ініціалізація при завантаженні DOM
document.addEventListener('DOMContentLoaded', () => {
    const expertFlipCards = new ExpertFlipCards();

    // Експортуємо в глобальну область для можливого доступу ззовні
    window.expertFlipCards = expertFlipCards;
});

