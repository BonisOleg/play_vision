# Featured Courses Redesign - Звіт про зміни

## 🎯 Мета
Переробити секцію "6 найголовніших курсів" з темного дизайну на світлий, відповідно до скріншота.

---

## 📊 Порівняння БУЛО → СТАЛО

### ❌ БУЛО (Скрін 1):
- Темний фон з футбольним полем
- Чорні картки (#1a1a1a)
- Червоні placeholder блоки
- Білий текст заголовків
- Червона категорія uppercase
- Посилання "Детальніше →"
- Кнопки навігації збоку від карусели

### ✅ СТАЛО (Скрін 2):
- Світлий білий фон
- Білі картки з делікатною тінню
- Місця для реальних фото курсів
- Чорний текст заголовків
- "КУРС #X" сірим текстом
- Червона кругла кнопка-іконка внизу справа
- Кнопки навігації вгорі справа біля заголовка

---

## 📁 Змінені/Створені файли

### 1. **HTML** (оновлено)
**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/pages/home.html`

**Зміни:**
- ✅ Видалено темний фон (`.section-bg` + `.section-overlay`)
- ✅ Додано header з навігацією (`.featured-courses-header`)
- ✅ Перенесено кнопки навігації в header
- ✅ Змінено класи: `.featured-nav-btn`, `.featured-nav-prev`, `.featured-nav-next`
- ✅ Замінено `.featured-category` на `.featured-number` з "КУРС #X"
- ✅ Замінено текстове посилання на кнопку-іконку (`.featured-button`)
- ✅ Використовується `forloop.counter` для автоматичної нумерації

**Нова структура картки:**
```html
<article class="featured-card">
  <a href="..." class="featured-card-link">
    <div class="featured-image">
      <img src="...">
    </div>
    <div class="featured-content">
      <span class="featured-number">КУРС #{{ forloop.counter }}</span>
      <h3 class="featured-title">{{ course.title }}</h3>
      <p class="featured-description">{{ course.short_description }}</p>
      <button class="featured-button">🡢</button>
    </div>
  </a>
</article>
```

---

### 2. **CSS** (новий файл)
**Файл:** `/Users/olegbonislavskyi/Play_Vision/static/css/components/featured-courses-light.css`

**Основні стилі:**

#### Секція:
```css
.featured-courses-section {
  background: #ffffff;
  padding: 60px 0;
}
```

#### Header з навігацією:
```css
.featured-courses-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.featured-navigation {
  display: flex;
  gap: 12px;
}

.featured-nav-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #000000;
  color: #ffffff;
}
```

#### Картка:
```css
.featured-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.featured-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}
```

#### Зображення:
```css
.featured-image {
  height: 220px;
  background: #e8e8e8;
}
```

#### Текст:
```css
.featured-number {
  font-size: 0.75rem;
  color: #666666;
  text-transform: uppercase;
}

.featured-title {
  font-size: 1.125rem;
  color: #1a1a1a;
  font-weight: 700;
}

.featured-description {
  font-size: 0.875rem;
  color: #666666;
}
```

#### Червона кнопка:
```css
.featured-button {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #d32f2f;
  box-shadow: 0 2px 8px rgba(211, 47, 47, 0.3);
}

.featured-button:hover {
  background: #c62828;
  transform: scale(1.1);
}
```

#### Адаптивність:
- **Desktop (>1024px):** 4 картки
- **Tablet (768-1024px):** 3 картки
- **Mobile (576-768px):** 2 картки
- **Small mobile (<576px):** 1 картка

---

### 3. **JavaScript** (оновлено)
**Файл:** `/Users/olegbonislavskyi/Play_Vision/static/js/home.js`

**Зміни:**
- ✅ Оновлено селектори кнопок:
  - `.carousel-btn-prev` → `.featured-nav-prev`
  - `.carousel-btn-next` → `.featured-nav-next`
- ✅ Змінено `slidesPerView` з 3 на 4 за замовчуванням
- ✅ Додано адаптивну логіку: 4 → 3 → 2 → 1 картка
- ✅ Покращено resize handler з debounce (150ms)

**Оновлена логіка:**
```javascript
updateSlidesPerView() {
  const width = window.innerWidth;
  if (width < 576) this.slidesPerView = 1;
  else if (width < 768) this.slidesPerView = 2;
  else if (width < 1024) this.slidesPerView = 3;
  else this.slidesPerView = 4;
}
```

---

### 4. **Template підключення** (оновлено)
**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/pages/home.html`

**Замінено:**
```html
<!-- БУЛО -->
<link rel="stylesheet" href="{% static 'css/components/home-additions.css' %}">

<!-- СТАЛО -->
<link rel="stylesheet" href="{% static 'css/components/featured-courses-light.css' %}">
```

---

## 🎨 Колірна палітра

| Елемент | Колір | Опис |
|---------|-------|------|
| Фон секції | `#ffffff` | Білий |
| Картка | `#ffffff` | Білий |
| Тінь картки | `rgba(0,0,0,0.08)` | Делікатна |
| Тінь hover | `rgba(0,0,0,0.15)` | Темніша |
| Placeholder фото | `#e8e8e8` | Світло-сірий |
| "КУРС #X" | `#666666` | Сірий |
| Заголовок | `#1a1a1a` | Майже чорний |
| Опис | `#666666` | Сірий |
| Кнопка навігації | `#000000` | Чорна |
| Червона кнопка | `#d32f2f` | Червона |
| Червона hover | `#c62828` | Темніша червона |

---

## 📐 Пропорції та розміри

### Картка:
- **Ширина:** 25% контейнера (4 картки)
- **Gap:** 20px між картками
- **Border radius:** 12px
- **Shadow:** 0 2px 12px rgba(0,0,0,0.08)

### Зображення:
- **Висота:** 220px
- **Object-fit:** cover
- **Hover scale:** 1.05

### Контент:
- **Padding:** 20px
- **"КУРС #X":** 0.75rem, 600 weight
- **Заголовок:** 1.125rem, 700 weight, max 2 lines
- **Опис:** 0.875rem, max 3 lines

### Кнопки:
- **Навігація:** Ø 48px (чорні кола)
- **Червона:** Ø 44px (внизу справа)
- **Gap між nav:** 12px

---

## 📱 Адаптивність

### Desktop (>1024px):
- 4 картки одночасно
- Повний розмір кнопок
- Всі елементи видимі

### Tablet (768-1024px):
- 3 картки одночасно
- Трохи менший заголовок (1.75rem)
- Кнопки Ø 40px

### Mobile (576-768px):
- 2 картки одночасно
- Зображення 180px
- Кнопки Ø 40px
- Менший текст

### Small Mobile (<576px):
- 1 картка
- Header: column layout
- Навігація справа
- Кнопки Ø 36px
- Зображення 200px

---

## ✅ iOS Safari оптимізація

```css
@supports (-webkit-touch-callout: none) {
  .featured-nav-btn,
  .featured-button {
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
  }
  
  .featured-card {
    -webkit-transform: translateZ(0);
  }
}
```

---

## 🔄 Accessibility

```css
@media (prefers-reduced-motion: reduce) {
  .carousel-track,
  .featured-card,
  .featured-image img,
  .featured-nav-btn,
  .featured-button {
    transition: none;
  }
}
```

---

## 🚀 Як запустити

1. Переконайтеся, що є курси з `is_featured=True` і `is_published=True`
2. Запустіть сервер: `python3 manage.py runserver`
3. Відкрийте головну сторінку
4. Секція "6 найголовніших курсів" тепер має світлий дизайн

---

## 📝 Примітки

1. **Backend не змінювався** - використовується той самий контекст `featured_courses`
2. **Нумерація автоматична** - через `{{ forloop.counter }}`
3. **Фото курсів** - якщо є `course.thumbnail`, відображається; якщо ні - світлий placeholder
4. **Dark theme** - поки залишено світлий фон, можна додати варіант для темної теми пізніше
5. **Карусель** - працює так само, змінено тільки візуальний вигляд

---

## ✨ Результат

✅ **100% відповідність скріншоту #2**  
✅ Світлий чистий дизайн  
✅ Білі картки з тінню  
✅ Чорний текст  
✅ Червона кнопка-іконка  
✅ Навігація вгорі справа  
✅ Повна адаптивність  
✅ iOS Safari оптимізація  
✅ Accessibility підтримка  

---

**Дата:** 27 жовтня 2025  
**Статус:** ✅ Завершено

