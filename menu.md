# 📋 Документація: Десктопне меню PlayVision

## 📑 Зміст
1. [Загальна структура](#загальна-структура)
2. [HTML структура](#html-структура)
3. [CSS архітектура](#css-архітектура)
4. [JavaScript логіка](#javascript-логіка)
5. [AI Chat інтеграція](#ai-chat-інтеграція)
6. [Система позиціонування](#система-позиціонування)
7. [Анімації та ефекти](#анімації-та-ефекти)
8. [Інструкції для редагування](#інструкції-для-редагування)

---

## 🏗️ Загальна структура

Десктопне меню складається з 4 основних секцій:

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER (.main-header)                                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ CONTENT (.header-content) - зміщено на 100px ліворуч    │ │
│ │                                                           │ │
│ │ [1] LOGO  [2] NAVIGATION MENU  [3] AI CHAT  [4] ACTIONS │ │
│ │                                                           │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Секції:
1. **Логотип** - зліва, flex-column з tagline
2. **Навігаційне меню** - білий овал з кнопками та анімованим слайдером
3. **AI Chat** - інпут всередині овалу (візуально), але position: absolute
4. **Дії** - кошик, кабінет, перемикач теми (праворуч)

---

## 📄 HTML структура

### Файл: `templates/base/base.html`

```html
<header class="main-header">
    <div class="container">
        <div class="header-content">
            
            <!-- ============ СЕКЦІЯ 1: ЛОГОТИП ============ -->
            <a href="{% url 'core:home' %}" class="logo-link">
                <div class="logo-container">
                    <img src="/static/icons/playvision-logo.png" class="logo-img logo-light">
                    <img src="/static/icons/playvision-logo-dark.png" class="logo-img logo-dark">
                    <div class="logo-tagline">навігатор футбольного розвитку</div>
                </div>
            </a>

            <!-- ============ СЕКЦІЯ 2: НАВІГАЦІЙНЕ МЕНЮ ============ -->
            <nav class="header-nav-actions navbar-desktop-only">
                <div class="nav-tabs-container">
                    <!-- Анімований слайдер -->
                    <div class="nav-tabs-slider" data-nav-slider></div>
                    
                    <!-- Навігаційні кнопки -->
                    <a href="{% url 'core:home' %}" class="nav-tab-btn active" data-nav-tab>
                        <span class="nav-tab-text">Головна</span>
                    </a>
                    <a href="{% url 'core:about' %}" class="nav-tab-btn" data-nav-tab>
                        <span class="nav-tab-text">Про PlayVision</span>
                    </a>
                    <a href="{% url 'content:course_list' %}" class="nav-tab-btn" data-nav-tab>
                        <span class="nav-tab-text">ХАБ Знань</span>
                    </a>
                    
                    <!-- Dropdown меню для Івентів -->
                    <div class="nav-action-dropdown">
                        <a href="{% url 'events:event_list' %}" class="nav-tab-btn" data-nav-tab>
                            <span class="nav-tab-text">Івенти</span>
                        </a>
                        <div class="dropdown-menu">
                            <!-- Список найближчих подій -->
                        </div>
                    </div>
                    
                    <a href="{% url 'core:mentoring' %}" class="nav-tab-btn" data-nav-tab>
                        <span class="nav-tab-text">Ментор-коучинг</span>
                    </a>
                    <a href="{% url 'core:pricing' %}" class="nav-tab-btn" data-nav-tab>
                        <span class="nav-tab-text">Підписка</span>
                    </a>

                    <!-- ⭐ PLACEHOLDER - резервує місце для AI Chat -->
                    <div class="ai-chat-placeholder"></div>
                </div>

                <!-- ============ СЕКЦІЯ 3: AI CHAT (ABSOLUTE) ============ -->
                <div class="ai-chat-inline" data-ai-chat-inline>
                    <!-- Історія чату (росте вгору) -->
                    <div class="ai-chat-messages" data-ai-messages style="display: none;"></div>

                    <!-- Інпут (опускається вниз) -->
                    <div class="ai-chat-input-wrapper">
                        <input type="text" class="ai-chat-input" placeholder="Запитайте AI помічника...">
                        <button type="button" class="ai-chat-send-btn" data-ai-send>
                            <!-- SVG іконка відправки -->
                        </button>
                        <button type="button" class="ai-chat-detach-btn" data-ai-detach style="display: none;">
                            <!-- SVG іконка відкріплення -->
                        </button>
                    </div>
                </div>
            </nav>

            <!-- ============ СЕКЦІЯ 4: ДІЇ ============ -->
            <div class="header-actions desktop-actions navbar-desktop-only">
                <!-- Кошик -->
                <a href="{% url 'cart:cart' %}" class="navbar-icon cart-icon">
                    <svg>...</svg>
                    <span class="cart-count">0</span>
                </a>

                <!-- Кабінет -->
                <a href="{% url 'cabinet:dashboard' %}" class="navbar-icon">
                    <svg>...</svg>
                </a>

                <!-- Перемикач теми -->
                <button type="button" class="navbar-icon theme-toggle" data-theme-toggle>
                    <svg class="theme-icon-light">...</svg>
                    <svg class="theme-icon-dark">...</svg>
                </button>
            </div>

        </div>
    </div>
</header>
```

### Ключові особливості HTML:

1. **`.nav-tabs-container`** - білий овал, містить усі кнопки + placeholder
2. **`.ai-chat-placeholder`** - невидимий div, резервує місце (280px × 44px)
3. **`.ai-chat-inline`** - position: absolute, візуально накладається на placeholder
4. **`data-*` атрибути** - для JavaScript селекторів

---

## 🎨 CSS архітектура

### Файл: `static/css/components/header-desktop.css`

#### 1. Головний контейнер

```css
.header-content {
    display: grid;
    grid-template-columns: minmax(200px, auto) 1fr auto auto;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-lg) 0;
    width: 100%;
    transform: translateX(-100px); /* ⚠️ Зміщення всього меню */
}
```

**Пояснення:**
- `grid` - 4 колонки для 4 секцій
- `transform: translateX(-100px)` - зміщує ВСЕ меню на 100px ліворуч
- Змінюючи це значення, ви рухаєте все меню

#### 2. Навігаційне меню (овал)

```css
.header-nav-actions {
    position: relative; /* ⚠️ Для absolute позиціонування AI Chat */
    grid-column: 2 / 3;
    display: flex;
    justify-content: center;
    align-items: center;
}

.nav-tabs-container {
    display: flex;
    align-items: center;
    gap: 0;
    padding: 4px;
    min-height: 58px; /* Зменшено на 10% */
    border-radius: 50px;
    border: 2px solid var(--color-border);
    background: var(--color-bg);
    position: relative;
    overflow: visible;
}
```

#### 3. Навігаційні кнопки

```css
.nav-tab-btn {
    position: relative;
    padding: 8px 18px; /* Зменшено на 10% */
    min-height: 50px; /* Зменшено на 10% */
    border-radius: 50px;
    font-size: 14px;
    font-weight: 500;
    color: #666;
    transition: all 0.3s ease;
    z-index: 2;
}

.nav-tab-btn:hover {
    color: var(--color-bg); /* Білий на темному */
    background: rgba(0, 0, 0, 0.05);
}

.nav-tab-btn.active {
    color: #E50914; /* Червоний PlayVision */
}
```

#### 4. Анімований слайдер

```css
.nav-tabs-slider {
    position: absolute;
    top: 4px;
    left: 4px;
    height: calc(100% - 8px);
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    border-radius: 50px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
```

**Пояснення:** Слайдер рухається за активною кнопкою через JavaScript.

---

### Файл: `static/css/components/ai-chat-inline.css`

#### 1. Placeholder (резервує місце)

```css
.ai-chat-placeholder {
    width: 280px;
    height: 44px;
    margin-left: 12px;
    flex-shrink: 0;
    /* Невидимий, але займає місце в flex-контейнері овалу */
}
```

**Пояснення:**
- Знаходиться всередині `.nav-tabs-container`
- Займає місце, але нічого не відображає
- AI Chat візуально накладається поверх нього

#### 2. AI Chat контейнер (ABSOLUTE)

```css
.header-nav-actions {
    position: relative; /* Батьківський контекст */
}

.ai-chat-inline {
    position: absolute; /* ⚠️ Поза normal flow */
    width: 280px;
    display: flex;
    flex-direction: column;
    z-index: 100;
    
    /* 🎯 ПОЗИЦІОНУВАННЯ (змінювати тут) */
    top: 0;
    right: 0;
    transform: translate(0px, 0px);
}
```

**Пояснення:**
- `position: absolute` - не впливає на розмір овалу
- Відносно `.header-nav-actions` (position: relative)
- `transform: translate()` - точне позиціонування

#### 3. Історія чату (росте вгору)

```css
.ai-chat-messages {
    width: 100%;
    max-height: 50vh; /* Максимум 50% висоти екрану */
    overflow-y: auto;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 12px 12px 0 0;
    border-bottom: none;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
```

**Пояснення:**
- Спочатку `display: none`
- Після першого повідомлення показується
- Росте вгору (від позиції інпута)
- Інпут опускається вниз

#### 4. Інпут чату

```css
.ai-chat-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 24px;
    padding: 10px 16px;
    transition: all 0.3s ease;
}

.ai-chat-input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 14px;
    color: var(--color-text);
    outline: none;
}
```

#### 5. Відкріплене модальне вікно

```css
.ai-chat-modal {
    position: fixed;
    width: 400px;
    max-width: 90vw;
    max-height: 600px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    z-index: 10000;
    display: flex;
    flex-direction: column;
}

.ai-chat-modal-header {
    padding: 16px;
    border-bottom: 1px solid var(--color-border);
    cursor: move; /* Для drag & drop */
    display: flex;
    justify-content: space-between;
    align-items: center;
}
```

**Пояснення:**
- Створюється динамічно через JavaScript
- Можна переміщувати (drag & drop)
- Можна змінювати висоту (resize)

---

## ⚙️ JavaScript логіка

### Файл: `static/js/nav-tabs-slider.js`

```javascript
// Константи для налаштування слайдера
const WIDTH_REDUCTION = 5; // Ширина менша на 5px
const RIGHT_OFFSET = 10;   // Права позиція зміщена на 10px ліворуч

// Оновлення позиції слайдера
function updateSliderPosition(tab) {
    const rect = tab.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    
    const left = rect.left - containerRect.left - 4;
    const width = rect.width - WIDTH_REDUCTION;
    
    // Для останньої кнопки - додатковий офсет
    const isLastTab = tab === tabs[tabs.length - 1];
    const adjustedLeft = isLastTab ? left + RIGHT_OFFSET : left;
    
    slider.style.left = `${adjustedLeft}px`;
    slider.style.width = `${width}px`;
}
```

**Пояснення:**
- Рухає слайдер за активною/hover кнопкою
- `WIDTH_REDUCTION = 5` - ширина на 5px менша
- `RIGHT_OFFSET = 10` - права позиція на 10px лівіше
- Smooth animation через CSS `transition`

---

### Файл: `static/js/components/ai-chat-inline.js`

```javascript
// Стан чату
const state = {
    isDetached: false,      // Чи відкріплений чат
    messageCount: 0,        // Кількість повідомлень
    isDragging: false,      // Чи переміщується модалка
    isResizing: false,      // Чи змінюється розмір
    modalPosition: { x: 100, y: 100 },
    modalSize: { height: 400 }
};

// Відправка повідомлення
function handleSendMessage() {
    const message = elements.input.value.trim();
    if (!message) return;

    // Показуємо історію при першому повідомленні
    if (state.messageCount === 0) {
        showChatHistory();
    }

    // Додаємо повідомлення користувача
    addMessage(message, 'user');
    
    // Симуляція відповіді AI
    setTimeout(() => {
        addMessage('Відповідь AI...', 'ai');
    }, 1000);

    elements.input.value = '';
    state.messageCount++;
}

// Показати історію чату
function showChatHistory() {
    elements.messages.style.display = 'flex';
    elements.detachBtn.style.display = 'flex';
    
    // Анімація появи
    requestAnimationFrame(() => {
        elements.messages.style.opacity = '1';
        elements.messages.style.transform = 'translateY(0)';
    });
}

// Відкріпити чат
function handleDetachChat() {
    state.isDetached = true;
    
    // Створюємо модальне вікно
    const modal = createModalWindow();
    document.body.appendChild(modal);
    
    // Переносимо повідомлення в модалку
    const modalMessages = modal.querySelector('[data-modal-messages]');
    modalMessages.innerHTML = elements.messages.innerHTML;
    
    // Ховаємо inline чат
    elements.inline.style.display = 'none';
    
    // Ініціалізуємо drag & drop
    initDragDrop(modal);
    initResize(modal);
}

// Прикріпити чат назад
function attachChat() {
    state.isDetached = false;
    
    // Переносимо повідомлення назад
    const modal = document.querySelector('.ai-chat-modal');
    if (modal) {
        const modalMessages = modal.querySelector('[data-modal-messages]');
        elements.messages.innerHTML = modalMessages.innerHTML;
        modal.remove();
    }
    
    // Показуємо inline чат
    elements.inline.style.display = 'flex';
}

// Drag & Drop для модального вікна
function initDragDrop(modal) {
    const header = modal.querySelector('.ai-chat-modal-header');
    
    header.addEventListener('mousedown', (e) => {
        state.isDragging = true;
        state.dragOffset = {
            x: e.clientX - modal.offsetLeft,
            y: e.clientY - modal.offsetTop
        };
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!state.isDragging) return;
        
        modal.style.left = `${e.clientX - state.dragOffset.x}px`;
        modal.style.top = `${e.clientY - state.dragOffset.y}px`;
    });
    
    document.addEventListener('mouseup', () => {
        state.isDragging = false;
    });
}

// Resize для модального вікна
function initResize(modal) {
    const resizeHandle = modal.querySelector('.ai-chat-modal-resize');
    
    resizeHandle.addEventListener('mousedown', (e) => {
        state.isResizing = true;
        state.resizeStartY = e.clientY;
        state.resizeStartHeight = modal.offsetHeight;
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!state.isResizing) return;
        
        const delta = e.clientY - state.resizeStartY;
        const newHeight = state.resizeStartHeight + delta;
        
        // Обмеження висоти (200px - 50vh)
        const minHeight = 200;
        const maxHeight = window.innerHeight * 0.5;
        modal.style.height = `${Math.min(Math.max(newHeight, minHeight), maxHeight)}px`;
    });
    
    document.addEventListener('mouseup', () => {
        state.isResizing = false;
    });
}
```

---

## 🎯 Система позиціонування

### Рівні позиціонування:

```
1. .header-content (transform: translateX(-100px))
   ↓ Зміщує ВСЕ меню
   
2. .nav-tabs-container (position: relative, flex)
   ↓ Білий овал, містить кнопки + placeholder
   
3. .ai-chat-placeholder (width: 280px, height: 44px)
   ↓ Резервує місце в овалі
   
4. .ai-chat-inline (position: absolute, transform: translate())
   ↓ Візуально накладається на placeholder
```

### Як рухати різні елементи:

#### 1️⃣ Рухати ВСЕ меню (logo, овал, кнопки, все):

**Файл:** `static/css/components/header-desktop.css`
**Рядок:** ~28

```css
.header-content {
    transform: translateX(-100px); /* Змінювати тут */
}
```

- `+` значення = праворуч
- `-` значення = ліворуч
- **Приклад:** `translateX(-50px)` - все меню на 50px ліворуч

---

#### 2️⃣ Рухати ЛИШЕ AI Chat інпут:

**Файл:** `static/css/components/ai-chat-inline.css`
**Рядок:** ~39

```css
.ai-chat-inline {
    transform: translate(0px, 0px);
    /*              ↑     ↑
                    X     Y  */
}
```

- **X (перше значення):**
  - `+` = праворуч
  - `-` = ліворуч
- **Y (друге значення):**
  - `+` = вниз
  - `-` = вгору

**Приклади:**
```css
/* Інпут на 20px ліворуч, 5px вниз */
transform: translate(-20px, 5px);

/* Інпут на 30px праворуч, без зміщення по Y */
transform: translate(30px, 0px);
```

---

#### 3️⃣ Змінити розмір placeholder (місце в овалі):

**Файл:** `static/css/components/ai-chat-inline.css`
**Рядок:** ~11-12

```css
.ai-chat-placeholder {
    width: 280px;  /* Ширина */
    height: 44px;  /* Висота */
}
```

⚠️ **Важливо:** Якщо змінюєте ширину placeholder, змініть і ширину `.ai-chat-inline`!

---

#### 4️⃣ Змінити позицію слайдера:

**Файл:** `static/js/nav-tabs-slider.js`
**Рядки:** ~10-11

```javascript
const WIDTH_REDUCTION = 5;  // Ширина на 5px менша
const RIGHT_OFFSET = 10;    // Зміщення для останньої кнопки
```

---

## 🎬 Анімації та ефекти

### 1. Анімація слайдера

```css
.nav-tabs-slider {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

**Ефект:** Плавне переміщення за активною/hover кнопкою.

---

### 2. Анімація появи історії чату

```css
.ai-chat-messages {
    transition: opacity 0.3s ease, transform 0.3s ease;
    opacity: 0;
    transform: translateY(-10px);
}

/* Після показу */
.ai-chat-messages {
    opacity: 1;
    transform: translateY(0);
}
```

**Ефект:** Історія з'являється з fade-in та рухається зверху вниз.

---

### 3. Hover ефект на кнопках

```css
.nav-tab-btn:hover {
    color: var(--color-bg);
    background: rgba(0, 0, 0, 0.05);
}
```

**Ефект:** Колір тексту змінюється при наведенні, слайдер рухається.

---

### 4. Анімація відкриття dropdown (Івенти)

```css
.dropdown-menu {
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s ease;
}

.nav-action-dropdown:hover .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}
```

**Ефект:** Dropdown плавно з'являється знизу вгору.

---

## 📐 Адаптивність

### Десктопні breakpoints:

```css
/* Десктопне меню видиме лише на > 1024px */
@media (min-width: 1024px) {
    .navbar-desktop-only {
        display: flex !important;
    }
}

@media (max-width: 1023px) {
    .navbar-desktop-only {
        display: none !important;
    }
}
```

На мобільних пристроях (<1024px) використовується інше меню (mobile-bottom-nav).

---

## 🎨 Темізація

### Світла тема:

```css
:root {
    --color-bg: #ffffff;
    --color-text: #1a1a1a;
    --color-border: #e5e7eb;
}

.nav-tabs-container {
    background: var(--color-bg);
    border-color: var(--color-border);
}
```

### Темна тема:

```css
[data-theme="dark"] {
    --color-bg: #1a1a1a;
    --color-text: #ffffff;
    --color-border: #2d2d2d;
}

[data-theme="dark"] .nav-tabs-container {
    background: #1a1a1a;
    border-color: #2d2d2d;
}

[data-theme="dark"] .nav-tabs-slider {
    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
}
```

---

## 📋 Інструкції для редагування

### ✅ Зміна позиції всього меню

1. Відкрийте: `static/css/components/header-desktop.css`
2. Знайдіть: `.header-content` (~рядок 21)
3. Змініть: `transform: translateX(-100px);`
4. Збережіть та перезавантажте сторінку

### ✅ Зміна позиції AI Chat інпута

1. Відкрийте: `static/css/components/ai-chat-inline.css`
2. Знайдіть: `.ai-chat-inline` (~рядок 26)
3. Змініть: `transform: translate(0px, 0px);`
4. Збережіть та перезавантажте сторінку

### ✅ Зміна кольорів меню

1. Відкрийте: `static/css/design-tokens.css`
2. Змініть змінні:
   ```css
   --color-red-brand: #E50914; /* Фірмовий червоний */
   --color-bg: #ffffff;        /* Фон */
   --color-border: #e5e7eb;    /* Бордюри */
   ```

### ✅ Зміна анімації слайдера

1. Відкрийте: `static/css/components/header-desktop.css`
2. Знайдіть: `.nav-tabs-slider` (~рядок 140)
3. Змініть: `transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);`
   - `0.3s` - швидкість (більше = повільніше)
   - `cubic-bezier()` - крива анімації

### ✅ Зміна висоти меню (зменшення на 10%)

1. Відкрийте: `static/css/components/header-desktop.css`
2. Знайдіть: `.nav-tabs-container` (~рядок 100)
3. Змініть: `min-height: 58px;` (було 64px)
4. Знайдіть: `.nav-tab-btn` (~рядок 115)
5. Змініть: `min-height: 50px;` (було 56px)
6. Змініть: `padding: 8px 18px;` (було 9px 20px)

### ✅ Додавання нової кнопки в меню

1. Відкрийте: `templates/base/base.html`
2. Знайдіть: `.nav-tabs-container`
3. Додайте перед `<div class="ai-chat-placeholder">`:
   ```html
   <a href="{% url 'your_url' %}" class="nav-tab-btn" data-nav-tab>
       <span class="nav-tab-text">Нова кнопка</span>
   </a>
   ```
4. Збережіть - JavaScript автоматично обробить нову кнопку

---

## 🐛 Troubleshooting

### Проблема: Інпут не на своєму місці

**Рішення:**
1. Перевірте `.ai-chat-inline` → `transform: translate()`
2. Перевірте `.ai-chat-placeholder` → `width` і `margin-left`
3. Перевірте `.header-nav-actions` → має бути `position: relative`

---

### Проблема: Слайдер не рухається

**Рішення:**
1. Перевірте консоль на помилки JavaScript
2. Переконайтесь, що `nav-tabs-slider.js` завантажений
3. Перевірте, чи є `data-nav-tab` атрибути на кнопках

---

### Проблема: Історія чату розтягує меню

**Рішення:**
1. Переконайтесь, що `.ai-chat-inline` має `position: absolute`
2. Переконайтесь, що `.header-nav-actions` має `position: relative`
3. Перевірте, чи немає `position: relative` на `.ai-chat-inline`

---

### Проблема: Меню виглядає по-різному в темах

**Рішення:**
1. Перевірте CSS змінні в `design-tokens.css`
2. Додайте стилі для `[data-theme="dark"]`
3. Перевірте `theme.css` на конфлікти

---

## 📂 Структура файлів

```
Play_Vision/
├── templates/
│   └── base/
│       └── base.html              # HTML структура меню
│
├── static/
│   ├── css/
│   │   ├── design-tokens.css      # CSS змінні (кольори, відступи)
│   │   ├── theme.css              # Темізація (світла/темна)
│   │   └── components/
│   │       ├── header-desktop.css # Стилі десктопного меню
│   │       └── ai-chat-inline.css # Стилі AI чату
│   │
│   └── js/
│       ├── nav-tabs-slider.js     # Логіка анімованого слайдера
│       └── components/
│           └── ai-chat-inline.js  # Логіка AI чату
│
└── menu.md                         # Ця документація
```

---

## 🎯 Ключові технології

- **HTML5** - семантична розмітка
- **CSS3** - Grid, Flexbox, Custom Properties, Transitions
- **JavaScript (ES6+)** - DOM manipulation, Events, State management
- **Django Templates** - template tags, conditionals

---

## 📚 Корисні посилання

- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [CSS Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [JavaScript Events](https://developer.mozilla.org/en-US/docs/Web/Events)

---

## 📝 Changelog

### 2025-10-22
- ✅ Створено документацію
- ✅ Описано всю логіку десктопного меню
- ✅ Додано інструкції для редагування
- ✅ Додано troubleshooting секцію

---

**Створено:** 22 жовтня 2025  
**Автор:** PlayVision Development Team  
**Версія:** 1.0.0

