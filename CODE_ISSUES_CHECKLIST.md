# 🔍 ДЕТАЛЬНИЙ ЧЕКЛИСТ ВИЯВЛЕНИХ ПРОБЛЕМ

> **Дата аудиту:** 2025-10-09  
> **Статус:** Готово до виправлення  
> **Підхід:** Incremental fixes

---

## 🔴 КРИТИЧНІ (High Priority)

### 1. Дублікати функцій (10 файлів)

**Проблема:** Функція `getCookie()` / `getCSRFToken()` повторюється

**Знайдено в:**
- [ ] static/js/components/ai-global.js
- [ ] static/js/main.js
- [ ] static/js/material-detail.js
- [ ] static/js/api-utils.js
- [ ] static/js/course-detail.js
- [ ] static/js/core/cart-header.js
- [ ] apps/video_security/static/video_security/js/secure_video.js

**Рішення:** Створити `static/js/shared/csrf.js` з єдиною функцією

---

### 2. Дублікати notification систем (89 місць!)

**Проблема:** Кожен файл має власну `showMessage()` / `showToast()`

**Знайдено в:**
- [ ] static/js/auth.js (showNotification)
- [ ] static/js/pwa.js (showToast, showSuccessMessage, showErrorMessage)
- [ ] static/js/main.js (showMessage)
- [ ] static/js/core/cart-header.js (showMessage)
- [ ] static/js/components/cart.js (showToast - 16 refs!)
- [ ] static/js/cabinet.js (showNotification - 42 refs!)
- [ ] static/js/events.js (showNotification)
- [ ] static/js/hub.js (showToast)
- [ ] static/js/course-detail.js (showToast)
- [ ] apps/video_security/static/video_security/js/secure_video.js (showSecurityWarning)

**Рішення:** Створити `static/js/shared/notifications.js` з window.notify

---

## 🟡 СЕРЕДНІ (Medium Priority)

### 3. Inline styles в HTML (23 файли)

**Проблема:** `style="..."` в templates

**Файли:**
- [ ] templates/hub/course_list.html (2 місця)
- [ ] templates/admin/ai/test_ai.html (1)
- [ ] templates/hub/material_detail.html (3)
- [ ] templates/pages/about.html (3)
- [ ] templates/account/tabs/files.html (3)
- [ ] templates/account/tabs/loyalty.html (1)
- [ ] templates/account/tabs/payments.html (1)
- [ ] templates/account/cabinet.html (1)
- [ ] templates/events/event_list.html (1)
- [ ] templates/events/event_detail.html (2)
- [ ] templates/events/event_registration_form.html (2)
- [ ] templates/hub/course_detail.html (2)
- [ ] templates/partials/course_card.html (1)

**Рішення:** Замінити на classes або `hidden` attribute

---

### 4. JS style manipulation (116 місць)

**Проблема:** `element.style.cssText = ...` та `element.style.property = ...`

**Файли з найбільше проблем:**
- [ ] static/js/cabinet.js (17 місць)
- [ ] static/js/course-detail.js (14)
- [ ] static/js/components/cart.js (11)
- [ ] static/js/material-detail.js (10)
- [ ] static/js/pwa.js (8)
- [ ] apps/video_security/static/video_security/js/secure_video.js (11)

**Що МОЖНА замінити:** ~79 місць (toasts, modals, visibility)  
**Що ТРЕБА ЗАЛИШИТИ:** ~37 місць (progress, animations, security)

---

## 🟢 НИЗЬКІ (Low Priority)

### 5. !important в CSS (4 використання)

**Файл:** `static/css/components/hub.css` (рядки 2110-2113)

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;  /* ← видалити */
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**Рішення:** Видалити !important, додати ::before, ::after селектори

---

### 6. Дублікати @keyframes (6 різних файлів)

**Проблема:** Однакові анімації повторюються

**Знайдено:**
- fadeIn, fadeOut, fadeInUp - в 4 файлах
- slideInRight, slideOutRight - в 5 файлах
- spin - в 3 файлах
- pulse - в 2 файлах

**Рішення:** Консолідувати в `animations.css`

---

### 7. Hardcoded values замість variables

**Проблема:** Box shadows, transitions, radii повторюються

**Приклади:**
- `box-shadow: 0 2px 8px rgba(0,0,0,0.1)` - ~50 місць
- `transition: all 0.3s ease` - ~80 місць
- `border-radius: 8px` - ~60 місць

**Рішення:** Використовувати CSS variables

---

## ⚠️ ВИКЛЮЧЕННЯ (НЕ чіпати!)

### Що залишаємо як є:

#### ✅ Alpine.js inline styles
```html
<!-- Alpine додає динамічно - це NORMAL -->
<div x-show="open" style="display: none;">
```

#### ✅ Django progress bars
```html
<!-- Backend value - треба inline або data-attr -->
<div style="width: {{ progress }}%"></div>
```

#### ✅ Video watermark animations
```javascript
// Security feature - НЕ ЧІПАТИ!
watermark.style.top = y + 'px';
```

#### ✅ Touch gesture handlers
```javascript
// Dynamic values - треба style
element.style.transform = `translateX(${touchX}px)`;
```

---

## 🎯 ПРІОРИТИЗАЦІЯ

### ЩО РОБИТИ СПОЧАТКУ:

**Тиждень 1 (Quick Wins):**
1. ✅ Створити utilities.css
2. ✅ Створити animations.css
3. ✅ Розширити main.css variables
4. ✅ Видалити !important

**Тиждень 2-3 (Notification Migration):**
5. ✅ Створити notification system
6. ✅ Мігрувати auth.js, events.js
7. ✅ Мігрувати hub.js, course-detail.js
8. ✅ Мігрувати cabinet.js, cart.js

**Тиждень 4 (Cleanup):**
9. ✅ Оптимізувати CSS files (variables usage)
10. ✅ Modal standardization  
11. ✅ SW cache update
12. ✅ Final testing

---

## 📈 TRACKING PROGRESS

### Використати:

```markdown
## Progress Tracking

- [x] ~~КРОК 1: Utilities~~ (2025-10-09)
- [x] ~~КРОК 2: Notifications~~ (2025-10-10)
- [ ] КРОК 3: !important
- [ ] КРОК 4: Accessibility
- [ ] КРОК 5: CSS Variables
- [ ] КРОК 6: Modals
- [ ] КРОК 7: Service Worker

Current: 2/7 (28%)
```

---

## 🚦 Статус файлів

### CSS Files Status:

| File | Inline styles | !important | Hardcode | Priority |
|------|---------------|------------|----------|----------|
| main.css | 0 | 0 | many | EXTEND |
| hub.css | 0 | 4 | many | FIX |
| cart.css | 0 | 0 | many | OPTIMIZE |
| events.css | 0 | 0 | many | OPTIMIZE |
| cabinet.css | 0 | 0 | many | OPTIMIZE |

### JS Files Status:

| File | Duplicates | Inline styles | Priority |
|------|------------|---------------|----------|
| cabinet.js | showNotif (42) | style (17) | HIGH |
| cart.js | showToast (16) | style (11) | HIGH |
| auth.js | showNotif (2) | style (4) | MEDIUM |
| events.js | showNotif (4) | style (8) | MEDIUM |
| hub.js | showToast (3) | style (4) | MEDIUM |

---

## ✅ РЕКОМЕНДАЦІЯ

**Почніть з:**
1. Крок 1 (utilities) - 1 година, 0 ризику
2. Тестування - 30 хвилин
3. Commit: "Add utilities foundation"

**Потім:**
- Крок 2-3 (notifications + !important) - 1 день
- Тестування всіх сторінок
- Commit: "Add notification system"

**Результат через 2 дні:**
- Foundation готовий
- -200 рядків коду
- Чистіша архітектура
- БЕЗ regression bugs

---

**Next:** Див. FRONTEND_REFACTOR_SAFE_PLAN.md для деталей

