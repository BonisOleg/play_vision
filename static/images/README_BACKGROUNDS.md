# 🎨 Інструкції для фонових зображень та відео

## 📝 Загальна інформація

Головна сторінка використовує систему fullscreen секцій з підтримкою фонових зображень та відео. Кожна секція може мати різні типи фонів та оверлеїв.

## 🖼️ Рекомендовані розміри зображень

### Фонові зображення:
- **Розмір**: 1920×1080px (Full HD)
- **Формат**: JPG для фото, PNG для графіки
- **Розмір файлу**: до 2MB (оптимізовані)
- **Співвідношення**: 16:9

### Фонові відео:
- **Розмір**: 1920×1080px 
- **Формат**: MP4 (H.264 codec)
- **Тривалість**: 10-30 секунд (loop)
- **Розмір файлу**: до 10MB
- **FPS**: 30fps

## 📁 Структура файлів

```
static/images/
├── hero-bg.jpg          # Фон для Hero секції
├── directions-bg.jpg    # Фон для Напрямків
├── courses-bg.jpg       # Фон для Курсів
├── experts-bg.jpg       # Фон для Експертів
├── values-bg.jpg        # Фон для Цінностей
└── cta-bg.jpg          # Фон для CTA секції

static/videos/
└── hero-bg.mp4         # Відео для Hero секції
```

## 🎯 Як замінити фон секції

### 1. Зображення
Просто замініть файл у папці `static/images/` на новий з тією ж назвою.

### 2. Відео
```html
<!-- У шаблоні home.html -->
<div class="section-bg">
    <video class="section-bg-video" autoplay muted loop>
        <source src="{% static 'videos/hero-bg.mp4' %}" type="video/mp4">
        <!-- Fallback image -->
        <img class="section-bg-image" src="{% static 'images/hero-bg.jpg' %}" alt="Fallback">
    </video>
</div>
```

### 3. Градієнт замість зображення
```html
<!-- Видаліть section-bg блок і додайте стилі -->
<section class="fullscreen-section hero-section" style="background: linear-gradient(135deg, #ff6b35 0%, #1a1a1a 100%);">
```

## 🎨 Типи оверлеїв

### Готові класи оверлеїв:
```css
.section-overlay--light    /* Світлий (білий 90%) */
.section-overlay--dark     /* Темний (чорний 60%) */
.section-overlay--primary  /* Основний колір (помаранчевий 80%) */
.section-overlay--gradient /* Градієнт (чорний → помаранчевий) */
```

### Зміна оверлею:
```html
<!-- Замініть клас на потрібний -->
<div class="section-overlay section-overlay--dark"></div>
```

### Кастомний оверлей:
```html
<div class="section-overlay" style="background: rgba(255, 0, 0, 0.3);"></div>
```

## 📱 Адаптивність

### Автоматична оптимізація:
- На мобільних пристроях відео відключається (показується fallback зображення)
- Зображення автоматично масштабуються через `object-fit: cover`
- Оверлеї стають більш контрастними на малих екранах

### iOS Safari оптимізація:
- Відео автоматично призупиняється для економії батареї
- Використовуються webkit префікси для height calculations
- Підтримка touch gestures

## 🚀 Приклади використання

### 1. Секція тільки з зображенням:
```html
<section class="fullscreen-section">
    <div class="section-bg">
        <img class="section-bg-image" src="{% static 'images/my-bg.jpg' %}" alt="Background">
    </div>
    <div class="section-overlay section-overlay--dark"></div>
    <!-- контент -->
</section>
```

### 2. Секція з відео + fallback:
```html
<section class="fullscreen-section">
    <div class="section-bg">
        <video class="section-bg-video" autoplay muted loop>
            <source src="{% static 'videos/my-video.mp4' %}" type="video/mp4">
            <img class="section-bg-image" src="{% static 'images/my-fallback.jpg' %}" alt="Fallback">
        </video>
    </div>
    <div class="section-overlay section-overlay--gradient"></div>
    <!-- контент -->
</section>
```

### 3. Секція з градієнтом (без зображення):
```html
<section class="fullscreen-section" style="background: linear-gradient(45deg, #ff6b35, #1a1a1a);">
    <!-- контент напряму без section-bg -->
</section>
```

### 4. Секція з кольором:
```html
<section class="fullscreen-section" style="background-color: #f5f5f5;">
    <!-- контент напряму -->
</section>
```

## ⚡ Поради з оптимізації

1. **Стискайте зображення** перед завантаженням (tinypng.com)
2. **Використовуйте WebP** для сучасних браузерів
3. **Lazy loading** для зображень не в viewport
4. **Прогресивний JPEG** для великих фото
5. **Короткі відео** (до 30 секунд) для кращої продуктивності

## 🔧 Налаштування продуктивності

### У production:
- Додайте `loading="lazy"` до зображень
- Використовуйте CDN для медіа файлів
- Стискайте відео через ffmpeg
- Додайте preload для критичних зображень

```html
<!-- Приклад оптимізованого зображення -->
<img class="section-bg-image" 
     src="{% static 'images/hero-bg.webp' %}" 
     alt="Hero Background"
     loading="lazy"
     decoding="async">
```
