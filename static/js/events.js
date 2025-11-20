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
    const filterBtns = document.querySelectorAll('.event-filters .filter-btn');
    
    if (!filterBtns.length) return;
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            
            const format = btn.dataset.format;
            
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Build URL
            const url = new URL(window.location.href);
            url.searchParams.delete('page');
            
            if (format === 'all') {
                url.searchParams.delete('format');
            } else {
                url.searchParams.set('format', format);
            }
            
            // HTMX request
            htmx.ajax('GET', url.toString(), {
                target: '#events-catalog-content',
                swap: 'innerHTML'
            });
            
            // Update URL
            window.history.pushState({}, '', url.toString());
        });
    });
}

