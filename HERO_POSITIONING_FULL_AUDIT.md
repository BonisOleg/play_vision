# ПОВНИЙ АУДИТ ПОЗИЦІОНУВАННЯ HERO БЛОКУ
## Всі правила, конфлікти та дублі

---

## 1. КОНТЕЙНЕР `.hero-section.hero-bordered .section-content.hero-new-design`

### Основне позиціонування (Desktop):
**Файл:** `static/css/components/home.css:38-52`
```css
.hero-section.hero-bordered .section-content.hero-new-design {
    border: none;
    background: transparent;
    backdrop-filter: none;
    width: 80%;
    max-width: 1400px;
    padding: 0 0 90px;
    text-align: left;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    height: 100%;
    min-height: 100%;
}
```

### Конфлікт з `section-base.css:186-192`:
**Файл:** `static/css/components/section-base.css:186-192`
```css
.hero-section.hero-bordered .section-content {
    border: none;
    border-radius: 0;
    padding: 3rem;  /* ⚠️ КОНФЛІКТ: перезаписує padding: 0 0 90px */
    backdrop-filter: none;
    background: transparent;
}
```
**Проблема:** Менш специфічний селектор `.hero-section.hero-bordered .section-content` має `padding: 3rem`, але більш специфічний `.hero-section.hero-bordered .section-content.hero-new-design` має `padding: 0 0 90px`. Оскільки більш специфічний селектор йде пізніше в каскаді, він перезаписує.

### Базове позиціонування з `section-base.css:62-77`:
**Файл:** `static/css/components/section-base.css:62-77`
```css
.hero-section .section-content,
.about-hero .section-content,
.mentoring-hero .section-content {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    max-width: 1400px;
    height: 100%;
    z-index: var(--z-content);
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 2rem var(--spacing-xl);
}
```
**Проблема:** Це правило встановлює `justify-content: center`, але `.hero-new-design` перезаписує на `justify-content: flex-end`.

### Tablet (769px - 1024px):
**Файл:** `static/css/components/home.css:74-77`
```css
@media (min-width: 769px) and (max-width: 1024px) {
    .section-content.hero-new-design {
        width: 90%;
        padding: 1rem 1.5rem 0.75rem;
    }
}
```

**Конфлікт з `section-base.css:140-150`:**
**Файл:** `static/css/components/section-base.css:140-150`
```css
@media (min-width: 768px) and (max-width: 1024px) {
    .hero-section .section-content,
    .about-hero .section-content,
    .mentoring-hero .section-content {
        width: 90%;
        padding: 1rem 1.5rem;
    }
    
    .hero-section .section-content {
        padding: 0.5rem 1.5rem 1.5rem;  /* ⚠️ КОНФЛІКТ: різні padding */
    }
}
```
**Проблема:** Два різні медіа-запити з різними breakpoints (768px vs 769px) та різними padding.

### Mobile (max-width: 767px):
**Файл:** `static/css/components/home.css:97-103`
```css
@media (max-width: 767px) {
    .hero-section.hero-bordered .section-content.hero-new-design {
        left: 5px;
        transform: none;  /* ⚠️ КОНФЛІКТ: перезаписує transform: translateX(-50%) */
        width: calc(100% - 5px);
        padding: 0.75rem 1rem 1.5rem 0;
        justify-content: flex-end;
    }
}
```

**Конфлікт з `section-base.css:162-173`:**
**Файл:** `static/css/components/section-base.css:162-173`
```css
@media (max-width: 767px) {
    .hero-section .section-content,
    .about-hero .section-content,
    .mentoring-hero .section-content {
        width: 95%;
        padding: 0.5rem 0.75rem 0.5rem;
        justify-content: flex-end;
    }
    
    .hero-section .section-content {
        padding: 0.25rem 0.75rem 1rem;  /* ⚠️ КОНФЛІКТ: різні padding */
    }
}
```

---

## 2. ЗАГОЛОВОК `.hero-title` та `.hero-new-design .hero-title`

### Desktop - Загальний стиль:
**Файл:** `static/css/components/home.css:174-183`
```css
.hero-title {
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: var(--spacing-lg);
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
    text-shadow: 0 4px 8px var(--shadow-alpha-80), 0 2px 4px var(--shadow-alpha-60);
}
```

### Desktop - NEW DESIGN (перезаписує загальний):
**Файл:** `static/css/components/home.css:186-196`
```css
.hero-new-design .hero-title {
    font-size: clamp(2.5rem, 4vw, 3.5rem);
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: var(--spacing-md);
    max-width: 600px;
    margin-left: 0;  /* ⚠️ Змінює з auto на 0 */
    margin-right: 0;  /* ⚠️ Змінює з auto на 0 */
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
    color: #ffffff;
}
```

### ⚠️ КОНФЛІКТИ з іншими файлами:

**1. `static/css/main.css:606-608` (Tablet):**
```css
@media (min-width: 769px) and (max-width: 1024px) {
    .hero-title {
        font-size: clamp(2rem, 4vw, 3rem);  /* ⚠️ КОНФЛІКТ: менш специфічний селектор */
    }
}
```
**Проблема:** Менш специфічний селектор `.hero-title` може конфліктувати з `.hero-new-design .hero-title`.

**2. `static/css/components/home.css:65-67` (Tablet):**
```css
@media (min-width: 769px) and (max-width: 1024px) {
    .hero-title {
        font-size: clamp(2rem, 4vw, 3rem);  /* ⚠️ ДУБЛЬ з main.css */
    }
}
```

**3. `static/css/components/home.css:79-82` (Tablet - NEW DESIGN):**
```css
@media (min-width: 769px) and (max-width: 1024px) {
    .hero-new-design .hero-title {
        font-size: 2rem; /* 70% від 2.5rem */
        margin-bottom: -1rem;
    }
}
```

**4. `static/css/components/home.css:105-110` (Mobile - NEW DESIGN):**
```css
@media (max-width: 767px) {
    .hero-new-design .hero-title {
        font-size: 1.5rem; /* 60% від 2.5rem */
        margin-bottom: -1rem;
        line-height: 1.2;
        max-width: 70%;
    }
}
```

**5. `static/css/components/hub-hero.css:77-88` (Hub Hero - КОНФЛІКТ):**
```css
.hero-title {
    color: #FFFFFF;
    font-size: 2.5rem;
    font-weight: 700;
    text-align: left;
    margin-top: 5px;
    padding-top: 40px;
    margin-bottom: -20px;
    text-shadow: none;
    min-height: 80px;
    overflow: hidden;
}
```
**Проблема:** Це правило для Hub сторінки, але може впливати на Home Hero, якщо клас `.hero-title` використовується без контексту.

**6. `static/css/accessibility.css:120-125` (High Contrast):**
```css
@media (prefers-contrast: high) {
    .hero-title,
    h1,
    h2,
    h3 {
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);  /* ⚠️ Може перезаписати text-shadow */
    }
}
```

### Dark Theme:
**Файл:** `static/css/components/home.css:636-640`
```css
[data-theme="dark"] {
    .hero-title,
    .hero-subtitle {
        color: white;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.8);
    }
}
```

---

## 3. ПІДЗАГОЛОВОК `.hero-subtitle` та `.hero-new-design .hero-subtitle`

### Desktop - Загальний стиль:
**Файл:** `static/css/components/home.css:198-206`
```css
.hero-subtitle {
    font-size: clamp(1.125rem, 2vw, 1.5rem);
    margin-bottom: var(--spacing-xxl);
    opacity: 0.9;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    text-shadow: 0 2px 4px var(--shadow-alpha-70);
}
```

### Desktop - NEW DESIGN (перезаписує загальний):
**Файл:** `static/css/components/home.css:209-219`
```css
.hero-new-design .hero-subtitle {
    font-size: clamp(1rem, 1.5vw, 1.25rem);
    margin-bottom: var(--spacing-xl);
    opacity: 0.85;
    max-width: 550px;
    margin-left: 0;  /* ⚠️ Змінює з auto на 0 */
    margin-right: 0;  /* ⚠️ Змінює з auto на 0 */
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
    color: #e0e0e0;
    line-height: 1.5;
}
```

### ⚠️ КОНФЛІКТИ з іншими файлами:

**1. `static/css/components/home.css:84-87` (Tablet - NEW DESIGN):**
```css
@media (min-width: 769px) and (max-width: 1024px) {
    .hero-new-design .hero-subtitle {
        font-size: 1rem; /* 80% від 1.25rem */
        margin-bottom: 0.3rem;
    }
}
```

**2. `static/css/components/home.css:112-117` (Mobile - NEW DESIGN):**
```css
@media (max-width: 767px) {
    .hero-new-design .hero-subtitle {
        font-size: 0.875rem; /* 70% від 1.25rem */
        margin-bottom: 0.3rem;
        line-height: 1.4;
        max-width: 50%;
    }
}
```

**3. `static/css/components/hub-hero.css:90-100` (Hub Hero - КОНФЛІКТ):**
```css
.hero-subtitle {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.9);
    margin-top: 0;
    margin-bottom: -30px;
    text-align: left;
    text-shadow: none;
    min-height: 50px;
    overflow: hidden;
    padding-top: 40px;
}
```
**Проблема:** Це правило для Hub сторінки, але може впливати на Home Hero.

**4. `static/css/components/loyalty-rules.css:64-68` (Loyalty - КОНФЛІКТ):**
```css
.hero-subtitle {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 40px;
}
```
**Проблема:** Менш специфічний селектор може впливати на Home Hero.

**5. `static/css/components/loyalty-rules.css:604-606` (Mobile):**
```css
@media (max-width: 767px) {
    .hero-subtitle {
        font-size: 16px;
    }
}
```

---

## 4. КНОПКА `.hero-btn-new` та контейнер `.hero-buttons`

### Контейнер `.hero-buttons` - Desktop:
**Файл:** `static/css/components/home.css:221-227`
```css
.hero-buttons {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: var(--spacing-xxl);
}
```

### Контейнер `.hero-buttons` - NEW DESIGN (перезаписує):
**Файл:** `static/css/components/home.css:230-233`
```css
.hero-new-design .hero-buttons {
    justify-content: flex-start;  /* ⚠️ Змінює з center на flex-start */
    margin-bottom: var(--spacing-lg);
}
```

### Кнопка `.hero-btn-new` - Desktop:
**Файл:** `static/css/components/home.css:237-255`
```css
.hero-btn-new {
    background: #e9e9e9;
    color: #000000;
    border: none;
    padding: 8px 14px 8px 16px;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 50px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 11px;
    text-decoration: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    white-space: nowrap;
    min-height: 54px;
    overflow: visible;
}
```

### ⚠️ КОНФЛІКТИ:

**1. `static/css/components/home.css:69-71` (Tablet):**
```css
@media (min-width: 769px) and (max-width: 1024px) {
    .hero-buttons {
        gap: var(--spacing-sm);
    }
}
```

**2. `static/css/components/home.css:89-92` (Tablet - NEW DESIGN):**
```css
@media (min-width: 769px) and (max-width: 1024px) {
    .hero-btn-new {
        padding: 10px 18px;
        font-size: 0.95rem;
    }
}
```

**3. `static/css/components/home.css:119-135` (Mobile - NEW DESIGN):**
```css
@media (max-width: 767px) {
    .hero-new-design .hero-buttons {
        gap: 0.5rem;
        margin-bottom: 0;
        display: flex;
        align-items: center;
    }

    .hero-btn-new {
        padding: 8px 14px;
        font-size: 0.875rem;
        min-height: auto;
    }

    .hero-btn-new .btn-logo-space {
        width: 10px;
        height: 10px;
    }
}
```

**4. `static/css/components/home.css:520-525` (Mobile - ДУБЛЬ):**
```css
@media (max-width: 767px) {
    .hero-buttons,
    .cta-buttons {
        flex-direction: column;  /* ⚠️ КОНФЛІКТ: змінює на column */
        align-items: center;
        gap: var(--spacing-md);
    }
}
```
**Проблема:** Це правило перезаписує `.hero-new-design .hero-buttons` з `display: flex` на `flex-direction: column`, що конфліктує з правилом вище.

**5. `static/css/components/hub-hero.css:111-117` (Hub Hero - КОНФЛІКТ):**
```css
.hero-buttons {
    display: flex;
    gap: var(--spacing-md);
    margin-bottom: 0;
    margin-left: auto;
    flex-shrink: 0;
}
```

**6. iOS Safari оптимізація:**
**Файл:** `static/css/components/home.css:583-591`
```css
@supports (-webkit-touch-callout: none) {
    .hero-btn-new {
        -webkit-appearance: none;
        -webkit-tap-highlight-color: transparent;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        user-select: none;
        appearance: none;
        cursor: pointer;
    }
}
```

**7. Dark Theme:**
**Файл:** `static/css/components/home.css:642-652`
```css
[data-theme="dark"] {
    .hero-btn-new {
        background: #e9e9e9;
        color: #000000;
    }

    .hero-btn-new:hover {
        background: #e9e9e9;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        text-decoration: none;
    }
}
```

---

## 5. ТОЧКИ СЛАЙДЕРА `.hero-slider-dots` та `.slider-dot`

### Контейнер `.hero-slider-dots` - Desktop:
**Файл:** `static/css/components/home.css:281-286`
```css
.hero-slider-dots {
    display: flex;
    justify-content: center;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-xl);
}
```

### Контейнер `.hero-slider-dots` - NEW DESIGN (перезаписує):
**Файл:** `static/css/components/home.css:289-293`
```css
.hero-new-design .hero-slider-dots {
    justify-content: flex-start;  /* ⚠️ Змінює з center на flex-start */
    margin-top: var(--spacing-md);
    margin-left: 0;
}
```

### Окремі точки `.slider-dot` - Desktop:
**Файл:** `static/css/components/home.css:295-309`
```css
.slider-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    transition: all 0.3s ease;
}

.slider-dot.active {
    background: var(--color-primary);
    width: 24px;
    border-radius: 4px;
}
```

### ⚠️ КОНФЛІКТИ:

**1. `static/css/components/home.css:138-155` (Mobile - NEW DESIGN):**
```css
@media (max-width: 767px) {
    .hero-new-design .hero-slider-dots {
        margin-top: 0;
        margin-left: auto;  /* ⚠️ Змінює з 0 на auto */
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .slider-dot {
        width: 8px;
        height: 8px;
        border-width: 1px;
    }
    
    .slider-dot.active {
        width: 20px;
        border-radius: 4px;
    }
}
```

**2. `static/css/components/home.css:311-321` (Mobile - ДУБЛЬ):**
```css
@media (max-width: 767px) {
    .slider-dot {
        width: 6px;  /* ⚠️ КОНФЛІКТ: різні значення (6px vs 8px) */
        height: 6px;
    }
    
    .slider-dot.active {
        width: 18px;  /* ⚠️ КОНФЛІКТ: різні значення (18px vs 20px) */
        border-radius: 3px;
    }
}
```
**Проблема:** Два різні медіа-запити для `.slider-dot` з різними значеннями. Останній перезаписує перший.

**3. `static/css/components/hub-hero.css:120-144` (Hub Hero - КОНФЛІКТ):**
```css
.hero-slider-dots {
    display: flex;
    justify-content: flex-start;
    gap: var(--spacing-sm);
    margin-top: 0;
    margin-left: 0;
    flex-shrink: 0;
}

.slider-dot {
    width: 12px;  /* ⚠️ КОНФЛІКТ: різні значення (12px vs 8px) */
    height: 12px;
    border-radius: 50%;
    border: 2px solid var(--accent-dark);  /* ⚠️ КОНФЛІКТ: border: none vs border: 2px */
    background: var(--silver-white);
    cursor: pointer;
    transition: all 0.3s ease;
}

.slider-dot.active {
    background: var(--color-primary);
    border-color: var(--color-primary);
    width: 32px;  /* ⚠️ КОНФЛІКТ: різні значення (32px vs 24px) */
    border-radius: 6px;
}
```
**Проблема:** Це правило для Hub сторінки, але може впливати на Home Hero, якщо класи використовуються без контексту.

**4. `static/css/components/hub-hero.css:308-310` (Mobile):**
```css
@media (max-width: 767px) {
    .hero-slider-dots {
        margin-top: 0;
    }
}
```

**5. iOS Safari оптимізація:**
**Файл:** `static/css/components/home.css:581`
```css
@supports (-webkit-touch-callout: none) {
    .slider-dot {
        -webkit-appearance: none;
        -webkit-tap-highlight-color: transparent;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        user-select: none;
        appearance: none;
        cursor: pointer;
    }
}
```

---

## 6. ДОДАТКОВІ КОНФЛІКТИ

### Конфлікт `.hero-section` width:
**Файл:** `static/css/components/home.css:160-170`
```css
.hero-section {
    width: 80%;
    max-width: 1400px;
    margin: 30px auto;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    color: white;
    text-align: center;
    position: relative;
}
```

**Конфлікт з `section-base.css:96-99`:**
```css
.hero-section {
    position: relative;
    overflow: hidden;
}
```

**Конфлікт з медіа-запитами:**
- `home.css:56-59` (Tablet): `width: 90%`
- `home.css:488-492` (max-width: 1024px): `width: 90%`
- `home.css:505-510` (Mobile): `width: 95%`

---

## 7. ПОРЯДОК ЗАСТОСУВАННЯ (КАСКАД)

### Пріоритет селекторів (від найнижчого до найвищого):

1. `.hero-title` (специфічність: 0,1,0)
2. `.hero-new-design .hero-title` (специфічність: 0,2,0) ✅ Перезаписує
3. `@media` всередині `.hero-new-design .hero-title` (специфічність: 0,2,0 + медіа) ✅ Перезаписує
4. `[data-theme="dark"] .hero-title` (специфічність: 0,2,0) ✅ Перезаписує

### Проблемні місця:

1. **Дубль медіа-запитів для `.slider-dot`** (рядки 146-155 та 311-321 в `home.css`)
2. **Конфлікт `.hero-buttons`** між `.hero-new-design .hero-buttons` та загальним правилом в рядку 520
3. **Конфлікт padding** між `section-base.css:186-192` та `home.css:38-52`
4. **Конфлікт transform** між `section-base.css:68` та `home.css:99`

---

## 8. РЕКОМЕНДАЦІЇ

1. **Видалити дублі:**
   - `.hero-title` в `main.css:606-608` (дубль з `home.css:65-67`)
   - `.slider-dot` медіа-запит в `home.css:311-321` (дубль з 146-155)

2. **Уточнити селектори:**
   - Додати контекст для Hub Hero стилів (наприклад, `.hub-hero-section .hero-title`)
   - Додати контекст для Loyalty стилів

3. **Узгодити breakpoints:**
   - Вирішити конфлікт між `768px` та `769px` breakpoints

4. **Узгодити padding:**
   - Вирішити конфлікт між `section-base.css` та `home.css` для `.hero-bordered .section-content`

---

## ВИСНОВОК

Знайдено:
- **8 конфліктів** між різними файлами
- **3 дублі** правил
- **2 конфлікти** всередині одного файлу (`home.css`)
- **Проблеми з каскадом** через різну специфічність селекторів

Всі правила зібрані та структуровані вище.

