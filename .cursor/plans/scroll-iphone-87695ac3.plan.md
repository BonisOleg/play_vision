<!-- 87695ac3-980e-4aca-a195-7d4b45abc2b4 5936f2e0-f714-4d1a-b632-f0dc40235565 -->
# Виправлення конфлікту: TAP на картці рухає каруселль

## 100% ПРИЧИНА ЗНАЙДЕНА

У [`static/js/expert-carousel-unified.js`](static/js/expert-carousel-unified.js) обробники touch на `.track` (experts-grid) спрацьовують для ВСІХ touch подій, включно з tap на картці. Події спливають від картки до каруселі, і карусель думає що це swipe і викликає `nextSlide()`/`prevSlide()` → каруселл РУХАЄТЬСЯ.

## РІШЕННЯ

### Варіант 1: stopPropagation при TAP (РЕКОМЕНДОВАНИЙ)

У [`static/js/expert-flip-cards.js`](static/js/expert-flip-cards.js) додати `e.stopPropagation()` при TAP:

```javascript
card.addEventListener('touchend', (e) => {
    const touchEndX = e.changedTouches[0].clientX;
    const touchEndY = e.changedTouches[0].clientY;
    const touchDuration = Date.now() - touchStartTime;
    const deltaX = Math.abs(touchEndX - touchStartX);
    const deltaY = Math.abs(touchEndY - touchStartY);

    // Якщо це TAP: швидкий і без значного руху
    if (!isMoved && touchDuration < 300 && deltaX < 20 && deltaY < 20) {
        // БЛОКУЄМО спливання до каруселі
        e.stopPropagation();
        e.preventDefault();
        
        // Перегорнути картку
        card.classList.toggle('flipped');
    }
    // Якщо це SWIPE (isMoved = true, великий deltaX/Y) - НЕ блокуємо, дозволяємо каруселі обробити
}, { passive: false });
```

**Також** додати `e.stopPropagation()` на `touchstart`:

```javascript
card.addEventListener('touchstart', (e) => {
    if (e.target.tagName === 'A' || e.target.classList.contains('expert-detail-link')) {
        return;
    }
    
    // БЛОКУЄМО спливання для потенційного TAP
    e.stopPropagation();
    
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    touchStartTime = Date.now();
    isMoved = false;
}, { passive: false });
```

**І** на `touchmove` при малому русі:

```javascript
card.addEventListener('touchmove', (e) => {
    if (!isMoved) {
        const currentX = e.touches[0].clientX;
        const currentY = e.touches[0].clientY;
        const deltaX = Math.abs(currentX - touchStartX);
        const deltaY = Math.abs(currentY - touchStartY);
        
        // Якщо це малий рух (можливо tap)
        if (deltaX < 5 && deltaY < 5) {
            // БЛОКУЄМО scroll і спливання
            e.preventDefault();
            e.stopPropagation();
        }
    }
    isMoved = true;
}, { passive: false });
```

## Результат

- ✅ TAP на картці → картка перегортається, карусель СТАТИЧНА (події заблоковані через stopPropagation)
- ✅ SWIPE на картці → карусель рухається (події спливають, картка НЕ перегортається)
- ✅ Scroll праvює
- ✅ Стрілки працюють
- ✅ Desktop не змінився

### To-dos

- [ ] Додати e.stopPropagation() при TAP в touchend
- [ ] Додати e.stopPropagation() в touchstart
- [ ] Додати e.stopPropagation() при малому русі в touchmove