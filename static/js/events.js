document.addEventListener('DOMContentLoaded', () => {
    initCalendarCarousel();
    initEventFilters();
});

function initCalendarCarousel() {
    const track = document.querySelector('.calendar-carousel-track');
    const prevBtn = document.querySelector('.calendar-nav-prev');
    const nextBtn = document.querySelector('.calendar-nav-next');
    const currentPageEl = document.querySelector('.current-page');
    
    if (!track || !prevBtn || !nextBtn) return;
    
    const cards = Array.from(track.querySelectorAll('.calendar-card'));
    const totalCards = cards.length;
    
    let currentIndex = 0;
    const cardsPerView = getCardsPerView();
    const maxIndex = Math.max(0, totalCards - cardsPerView);
    
    function getCardsPerView() {
        const width = window.innerWidth;
        if (width <= 480) return 1;
        if (width <= 768) return 2;
        if (width <= 1024) return 3;
        return 5;
    }
    
    function updateCarousel() {
        const cardWidth = cards[0].offsetWidth;
        const gap = 24;
        const offset = currentIndex * (cardWidth + gap);
        
        track.style.transform = `translateX(-${offset}px)`;
        
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex >= maxIndex;
        
        if (currentPageEl) {
            const pageNumber = String(currentIndex + 1).padStart(2, '0');
            currentPageEl.textContent = pageNumber;
        }
    }
    
    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });
    
    nextBtn.addEventListener('click', () => {
        if (currentIndex < maxIndex) {
            currentIndex++;
            updateCarousel();
        }
    });
    
    window.addEventListener('resize', () => {
        const newCardsPerView = getCardsPerView();
        const newMaxIndex = Math.max(0, totalCards - newCardsPerView);
        
        if (currentIndex > newMaxIndex) {
            currentIndex = newMaxIndex;
        }
        
        updateCarousel();
    });
    
    updateCarousel();
}

function initEventFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const eventCards = document.querySelectorAll('.event-catalog-card');
    
    if (!filterBtns.length || !eventCards.length) return;
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.filter;
            
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            eventCards.forEach(card => {
                const cardType = card.dataset.type;
                
                if (filter === 'online') {
                    card.style.display = cardType === 'online' ? 'flex' : 'none';
                } else if (filter === 'offline') {
                    card.style.display = cardType === 'offline' ? 'flex' : 'none';
                }
            });
        });
    });
}

