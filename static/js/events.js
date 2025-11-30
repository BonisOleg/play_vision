document.addEventListener('DOMContentLoaded', () => {
    initCalendarCarousel();
    initEventFilters();
});

function initCalendarCarousel() {
    const section = document.querySelector('.events-calendar-section');
    const track = document.querySelector('.calendar-carousel-track');
    const prevBtn = document.querySelector('.calendar-nav-prev');
    const nextBtn = document.querySelector('.calendar-nav-next');
    
    if (!track || !section) return;
    
    const cards = Array.from(track.querySelectorAll('.calendar-card'));
    const totalCards = cards.length;
    
    if (totalCards === 0) return;
    
    let currentIndex = 0;
    
    // Визначення кількості карток на екрані
    function getCardsPerView() {
        const width = window.innerWidth;
        if (width <= 480) return 1;
        if (width <= 768) return 2;
        if (width <= 1024) return 3;
        return 5;
    }
    
    let cardsPerView = getCardsPerView();
    let maxIndex = Math.max(0, totalCards - cardsPerView);
    
    // КЛЮЧОВА ФУНКЦІЯ: показ/приховування стрілок
    // БЕЗ INLINE STYLES - тільки CSS класи
    function updateArrowsVisibility() {
        const shouldShow = totalCards >= 6;
        const navigation = section.querySelector('.calendar-navigation');
        
        if (navigation) {
            if (shouldShow) {
                navigation.classList.remove('calendar-navigation--hidden');
            } else {
                navigation.classList.add('calendar-navigation--hidden');
            }
        }
    }
    
    function updateCarousel() {
        if (!track || cards.length === 0) return;
        
        const cardWidth = cards[0].offsetWidth;
        const gap = 24;
        const offset = currentIndex * (cardWidth + gap);
        
        track.style.transform = `translateX(-${offset}px)`;
        
        // Disabled стан кнопок
        if (prevBtn) prevBtn.disabled = currentIndex === 0;
        if (nextBtn) nextBtn.disabled = currentIndex >= maxIndex;
    }
    
    // Події для кнопок
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentIndex < maxIndex) {
                currentIndex++;
                updateCarousel();
            }
        });
    }
    
    // Touch/Swipe для мобільних (iOS/Android)
    let touchStartX = 0;
    let touchEndX = 0;
    let isDragging = false;
    
    track.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        isDragging = true;
    }, { passive: true });
    
    track.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        touchEndX = e.touches[0].clientX;
    }, { passive: true });
    
    track.addEventListener('touchend', () => {
        if (!isDragging) return;
        isDragging = false;
        
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0 && currentIndex < maxIndex) {
                currentIndex++;
                updateCarousel();
            } else if (diff < 0 && currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        }
        
        touchStartX = 0;
        touchEndX = 0;
    });
    
    // Resize з debounce
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            cardsPerView = getCardsPerView();
            maxIndex = Math.max(0, totalCards - cardsPerView);
            currentIndex = Math.min(currentIndex, maxIndex);
            updateCarousel();
            updateArrowsVisibility();
        }, 150);
    });
    
    // Ініціалізація
    updateArrowsVisibility();
    updateCarousel();
}

function initEventFilters() {
    // Ініціалізація event filters з shared slider компонентом
    const eventFilterSlider = window.initTabSlider ? window.initTabSlider('.event-filters', {
        sliderAttr: 'data-event-filter-slider',
        tabAttr: 'data-event-filter-tab',
        activeClass: 'active',
        containerPadding: 3.6,
        widthReduction: 5,
        rightOffset: 10,
        onTabChange: function(tab, index) {
            // Shared модуль УЖЕ оновив active class і slider позицію
            // Нам потрібно ТІЛЬКИ виконати HTMX запит
            
            const format = tab.dataset.format;
            
            // Build URL
            const url = new URL(window.location.href);
            url.searchParams.delete('page');
            
            if (format === 'all') {
                url.searchParams.delete('format');
            } else {
                url.searchParams.set('format', format);
            }
            
            // HTMX request - БЕЗ оновлення сторінки ✅
            htmx.ajax('GET', url.toString(), {
                target: '#events-catalog-content',
                swap: 'innerHTML'
            });
            
            // Update URL in browser
            window.history.pushState({}, '', url.toString());
        }
    }) : null;
    
    if (!eventFilterSlider) {
        console.warn('Events: tab-slider.js не завантажено');
    }
}

// Модальне вікно для безкоштовної реєстрації
(function() {
    const modal = document.getElementById('free-registration-modal');
    if (!modal) return;
    
    const openBtn = document.querySelector('[data-open-free-modal]');
    const closeBtn = document.querySelector('[data-close-modal]');
    
    if (openBtn) {
        openBtn.addEventListener('click', () => {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Закриття при кліку поза вікном
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
    
    // Закриття при ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
})();
