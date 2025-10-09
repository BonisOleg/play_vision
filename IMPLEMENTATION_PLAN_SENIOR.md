# 🚀 ПЛАН ІМПЛЕМЕНТАЦІЇ ЗМІН (SENIOR FULL-STACK)

## 📋 ЗАГАЛЬНА ІНФОРМАЦІЯ

**Дата створення:** 9 жовтня 2025  
**Підхід:** DRY (Don't Repeat Yourself) + Clean Architecture  
**Принципи:**
- ✅ Максимально використовувати існуючий код
- ✅ Уникати дублювання
- ✅ Без inline стилів
- ✅ Без !important в CSS
- ✅ Компонентний підхід
- ✅ Поетапне тестування

---

## 🎯 ФАЗИ ІМПЛЕМЕНТАЦІЇ

### PHASE 0: ПІДГОТОВКА (1 год)
### PHASE 1: BACKEND & DATABASE (2-3 год)
### PHASE 2: ГЛОБАЛЬНІ КОМПОНЕНТИ (1-2 год)
### PHASE 3: ГОЛОВНА СТОРІНКА (3-4 год)
### PHASE 4: ХАБ ЗНАНЬ (2-3 год)
### PHASE 5: ІВЕНТИ (1 год)
### PHASE 6: ОСОБИСТИЙ КАБІНЕТ (2-3 год)
### PHASE 7: ТЕСТУВАННЯ & ОПТИМІЗАЦІЯ (2-3 год)

**ЗАГАЛЬНИЙ ЧАС:** 14-20 годин

---

## 📦 PHASE 0: ПІДГОТОВКА

### 0.1 Git Setup
```bash
# Створити нову гілку
git checkout -b feature/screenshot-changes

# Створити бекап
git tag backup-before-changes-$(date +%Y%m%d)
```

### 0.2 Database Backup
```bash
# Бекап бази даних
python3 manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Або для PostgreSQL
pg_dump playvision > backup_$(date +%Y%m%d).sql
```

### 0.3 Створити структуру нових файлів
```bash
# CSS
touch static/css/components/scroll-popup.css
touch static/css/components/loyalty-rules.css

# JavaScript
touch static/js/scroll-popup.js

# Templates
mkdir -p templates/loyalty
touch templates/loyalty/rules.html
touch templates/partials/scroll-popup.html
```

### 0.4 Checklist залежностей
- [ ] Alpine.js встановлений
- [ ] HTMX встановлений
- [ ] Django міграції в актуальному стані

---

## 🗄️ PHASE 1: BACKEND & DATABASE (2-3 год)

### 1.1 Оновити модель Tag (інтереси)

**Файл:** `apps/content/models.py`

**Існуюча модель Tag (рядки 34-50):**
```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Додати поле для порядку:**
```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)  # НОВИЙ
    tag_type = models.CharField(max_length=20, choices=[          # НОВИЙ
        ('interest', 'Інтерес'),
        ('category', 'Категорія'),
        ('general', 'Загальний'),
    ], default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['display_order', 'name']  # ЗМІНЕНИЙ
```

**Створити міграцію:**
```bash
python3 manage.py makemigrations content --name add_tag_display_order
```

### 1.2 Створити модель MonthlyQuote

**Файл:** `apps/content/models.py`

**Додати після моделі Material:**
```python
class MonthlyQuote(models.Model):
    """
    Цитата експерта, яка міняється раз на місяць
    """
    expert_name = models.CharField(max_length=100, verbose_name='Імʼя експерта')
    expert_role = models.CharField(max_length=150, verbose_name='Посада')
    expert_photo = models.ImageField(
        upload_to='experts/quotes/', 
        blank=True,
        verbose_name='Фото експерта'
    )
    quote_text = models.TextField(verbose_name='Текст цитати')
    month = models.DateField(
        unique=True,
        verbose_name='Місяць',
        help_text='Перше число місяця (напр. 2025-10-01)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    
    # Кешування
    last_displayed = models.DateTimeField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'monthly_quotes'
        verbose_name = 'Цитата місяця'
        verbose_name_plural = 'Цитати місяця'
        ordering = ['-month']
        indexes = [
            models.Index(fields=['-month', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.expert_name} - {self.month.strftime('%B %Y')}"
    
    @classmethod
    def get_current_quote(cls):
        """Отримати цитату поточного місяця"""
        from django.utils import timezone
        from django.core.cache import cache
        
        cache_key = 'current_monthly_quote'
        quote = cache.get(cache_key)
        
        if not quote:
            today = timezone.now().date()
            current_month_start = today.replace(day=1)
            
            quote = cls.objects.filter(
                month=current_month_start,
                is_active=True
            ).first()
            
            if quote:
                # Кешувати до кінця місяця
                cache.set(cache_key, quote, 60*60*24*31)
        
        return quote
    
    def save(self, *args, **kwargs):
        # Автоматично встановити перше число місяця
        if self.month:
            self.month = self.month.replace(day=1)
        super().save(*args, **kwargs)
```

**Створити міграцію:**
```bash
python3 manage.py makemigrations content --name add_monthly_quote_model
```

### 1.3 Оновити Course model (додати training_types)

**Файл:** `apps/content/models.py`

**В існуючій моделі Course додати:**
```python
class Course(models.Model):
    # ... існуючі поля ...
    
    # НОВИЙ БЛОК
    training_specialization = models.CharField(
        max_length=30,
        choices=[
            ('', 'Не вказано'),
            ('goalkeeper', 'Тренер воротарів'),
            ('youth', 'Дитячий тренер'),
            ('fitness', 'Тренер ЗФП'),
            ('professional', 'Тренер професійних команд'),
        ],
        blank=True,
        default='',
        verbose_name='Спеціалізація тренера',
        help_text='Тільки для курсів категорії "Тренерство"'
    )
```

**Створити міграцію:**
```bash
python3 manage.py makemigrations content --name add_course_training_specialization
```

### 1.4 Створити data migration для інтересів

**Файл:** `apps/content/migrations/0XXX_populate_interests_tags.py`

```python
from django.db import migrations

def populate_interests(apps, schema_editor):
    Tag = apps.get_model('content', 'Tag')
    
    # Видалити старі теги інтересів
    Tag.objects.filter(tag_type='interest').delete()
    
    # Створити нові у правильному порядку
    interests = [
        (1, 'training', 'Тренерство'),
        (2, 'analytics', 'Аналітика і скаутинг'),
        (3, 'fitness', 'ЗФП'),
        (4, 'management', 'Менеджмент'),
        (5, 'psychology', 'Психологія'),
        (6, 'nutrition', 'Нутриціологія'),
        (7, 'player', 'Футболіст'),
        (8, 'parent', 'Батько'),
    ]
    
    for order, slug, name in interests:
        Tag.objects.create(
            name=name,
            slug=slug,
            tag_type='interest',
            display_order=order
        )

def reverse_populate(apps, schema_editor):
    Tag = apps.get_model('content', 'Tag')
    Tag.objects.filter(tag_type='interest').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0XXX_add_tag_display_order'),  # Попередня міграція
    ]
    
    operations = [
        migrations.RunPython(populate_interests, reverse_populate),
    ]
```

### 1.5 Оновити admin.py для нових моделей

**Файл:** `apps/content/admin.py`

```python
from django.contrib import admin
from .models import MonthlyQuote

@admin.register(MonthlyQuote)
class MonthlyQuoteAdmin(admin.ModelAdmin):
    list_display = ['expert_name', 'month', 'is_active', 'views_count']
    list_filter = ['is_active', 'month']
    search_fields = ['expert_name', 'expert_role', 'quote_text']
    date_hierarchy = 'month'
    readonly_fields = ['views_count', 'last_displayed', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Експерт', {
            'fields': ('expert_name', 'expert_role', 'expert_photo')
        }),
        ('Цитата', {
            'fields': ('quote_text', 'month', 'is_active')
        }),
        ('Статистика', {
            'fields': ('views_count', 'last_displayed', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
```

### 1.6 Оновити CourseListView

**Файл:** `apps/content/views.py`

**Існуючий метод get_queryset() (рядки 18-50):**

```python
def get_queryset(self):
    queryset = Course.objects.filter(
        is_published=True
    ).select_related('category').prefetch_related('tags')
    
    # Category filter
    category_slug = self.request.GET.get('category')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    # ВИДАЛИТИ: Difficulty filter
    # difficulty = self.request.GET.get('difficulty')
    # if difficulty:
    #     queryset = queryset.filter(difficulty=difficulty)
    
    # Tag filter
    tag = self.request.GET.get('tag')
    if tag:
        queryset = queryset.filter(tags__slug=tag)
    
    # ВИДАЛИТИ: Price filter
    # price_filter = self.request.GET.get('price')
    # if price_filter == 'free':
    #     queryset = queryset.filter(is_free=True)
    # elif price_filter == 'paid':
    #     queryset = queryset.filter(is_free=False)
    
    # ДОДАТИ: Interest filter
    interest = self.request.GET.get('interest')
    if interest:
        queryset = queryset.filter(tags__slug=interest, tags__tag_type='interest')
    
    # ДОДАТИ: Training specialization filter
    training_spec = self.request.GET.get('training_type')
    if training_spec:
        queryset = queryset.filter(training_specialization=training_spec)
    
    # Sorting
    sort = self.request.GET.get('sort', '-created_at')
    if sort in ['price', '-price', 'title', '-title', '-created_at', 'view_count']:
        queryset = queryset.order_by(sort)
    
    return queryset
```

**Оновити get_context_data():**

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Існуючі
    from .models import Category, Tag
    context['categories'] = Category.objects.filter(is_active=True)
    
    # ЗАМІНИТИ: отримувати лише теги-інтереси
    context['interests'] = Tag.objects.filter(
        tag_type='interest'
    ).order_by('display_order')
    
    # Featured courses (найголовніші)
    context['featured_courses'] = Course.objects.filter(
        is_published=True,
        is_featured=True
    )[:6]
    
    # ДОДАТИ: Monthly quote
    from .models import MonthlyQuote
    context['monthly_quote'] = MonthlyQuote.get_current_quote()
    
    # Current filters
    context['current_category'] = self.request.GET.get('category', '')
    context['current_interest'] = self.request.GET.get('interest', '')
    context['current_training_type'] = self.request.GET.get('training_type', '')
    
    return context
```

### 1.7 Оновити EventListView

**Файл:** `apps/events/views.py`

**В методі get_queryset() видалити price filter (рядки 38-43):**

```python
def get_queryset(self):
    queryset = Event.objects.filter(
        status='published',
        start_datetime__gt=timezone.now()
    ).select_related('organizer').prefetch_related('speakers', 'tags')
    
    # Filter by type
    event_type = self.request.GET.get('type')
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    
    # Search
    search = self.request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(speakers__first_name__icontains=search) |
            Q(speakers__last_name__icontains=search)
        ).distinct()
    
    # ВИДАЛИТИ price filter
    # price_filter = self.request.GET.get('price')
    # if price_filter == 'free':
    #     queryset = queryset.filter(is_free=True)
    # elif price_filter == 'paid':
    #     queryset = queryset.filter(is_free=False)
    
    # Filter by date
    date_filter = self.request.GET.get('date')
    now = timezone.now()
    if date_filter == 'today':
        queryset = queryset.filter(start_datetime__date=now.date())
    elif date_filter == 'week':
        week_end = now + timezone.timedelta(days=7)
        queryset = queryset.filter(start_datetime__range=[now, week_end])
    elif date_filter == 'month':
        month_end = now + timezone.timedelta(days=30)
        queryset = queryset.filter(start_datetime__range=[now, month_end])
    
    # Ordering
    order = self.request.GET.get('order', 'start_datetime')
    if order in ['start_datetime', '-start_datetime', 'price', '-price', 'title']:
        queryset = queryset.order_by(order)
    
    return queryset
```

### 1.8 Запустити міграції

```bash
# Перевірити міграції
python3 manage.py makemigrations --dry-run

# Застосувати
python3 manage.py migrate

# Створити суперюзера якщо потрібно
python3 manage.py createsuperuser
```

### 1.9 Створити тестові дані через admin

```python
# python3 manage.py shell

from apps.content.models import MonthlyQuote
from datetime import date

MonthlyQuote.objects.create(
    expert_name="Пеп Гвардіола",
    expert_role='Тренер "Манчестер Сіті"',
    quote_text="Навчання ніколи не закінчується. Кожен день ми можемо дізнатися щось нове.",
    month=date(2025, 10, 1),
    is_active=True
)
```

---

## 🧩 PHASE 2: ГЛОБАЛЬНІ КОМПОНЕНТИ (1-2 год)

### 2.1 Оновити іконку кошика

**Файл:** `templates/base/base.html`

**Замість існуючого SVG (рядки 155-161):**

```html
<!-- ЗАМІНИТИ на нову іконку від клієнта -->
<a href="{% url 'cart:cart' %}" class="navbar-icon cart-icon navbar-desktop-only"
    aria-label="Кошик">
    <svg class="icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2">
        <!-- ВСТАВИТИ НОВИЙ SVG ВІД КЛІЄНТА -->
    </svg>
    <span class="cart-count" data-cart-count>{{ cart_items_count|default:0 }}</span>
</a>
```

### 2.2 Видалити кнопку "Play vision" з навігації

**Файл:** `templates/base/base.html`

**Видалити рядки 85-88 (якщо є така кнопка):**

```html
<!-- ВИДАЛИТИ ЦЕ -->
<!-- <a href="..." class="navbar-brand">
    <span>Play Vision</span>
</a> -->
```

### 2.3 Створити компонент Scroll Popup

**Файл:** `templates/partials/scroll-popup.html`

```html
<!-- Scroll Popup для підписки -->
<div id="scroll-popup" class="scroll-popup" x-data="scrollPopup()" x-show="showPopup" 
     x-transition:enter="popup-enter" x-transition:leave="popup-leave" style="display: none;">
    <div class="popup-overlay" @click="closePopup()"></div>
    
    <div class="popup-content">
        <button class="popup-close" @click="closePopup()" aria-label="Закрити">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
        
        <div class="popup-body">
            <h2 class="popup-title">Готовий приєднатись до спільноти Play vision?</h2>
            
            {% if user.is_authenticated %}
                <!-- Для зареєстрованих -->
                <p class="popup-description">
                    Оформи підписку та отримай <strong>+30 балів лояльності</strong>!
                </p>
                <div class="popup-actions">
                    <a href="{% url 'subscriptions:plans' %}" class="btn btn-primary btn-large">
                        Перейти до підписки
                    </a>
                </div>
            {% else %}
                <!-- Для гостей -->
                <p class="popup-description">
                    Зареєструйся та отримай <strong>10% знижку</strong> на першу покупку!
                </p>
                <form class="popup-register-form" @submit.prevent="handleRegister">
                    <div class="form-group">
                        <input type="email" name="email" placeholder="Ваш email" required
                               class="form-control" x-model="formData.email">
                    </div>
                    <div class="form-group">
                        <input type="password" name="password" placeholder="Пароль" required
                               class="form-control" x-model="formData.password">
                    </div>
                    <button type="submit" class="btn btn-primary btn-large" :disabled="loading">
                        <span x-show="!loading">Зареєструватись</span>
                        <span x-show="loading">Завантаження...</span>
                    </button>
                </form>
                <p class="popup-footer-text">
                    Вже є акаунт? <a href="{% url 'accounts:login' %}">Увійти</a>
                </p>
            {% endif %}
        </div>
    </div>
</div>
```

**Файл:** `static/css/components/scroll-popup.css`

```css
/* Scroll Popup Styles */
.scroll-popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.popup-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(5px);
}

.popup-content {
    position: relative;
    background: white;
    border-radius: 16px;
    max-width: 500px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
}

.popup-close {
    position: absolute;
    top: 16px;
    right: 16px;
    background: transparent;
    border: none;
    color: var(--color-text-light);
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    transition: all 0.3s ease;
    z-index: 10;
}

.popup-close:hover {
    background: var(--color-bg-gray);
    color: var(--color-text);
    transform: rotate(90deg);
}

.popup-body {
    padding: 48px 40px 40px;
}

.popup-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 16px;
    line-height: 1.3;
}

.popup-description {
    font-size: 1rem;
    color: var(--color-text-light);
    margin-bottom: 32px;
    line-height: 1.6;
}

.popup-description strong {
    color: var(--color-primary);
    font-weight: 600;
}

.popup-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.popup-register-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.popup-register-form .form-group {
    margin-bottom: 0;
}

.popup-footer-text {
    margin-top: 20px;
    text-align: center;
    font-size: 0.9rem;
    color: var(--color-text-light);
}

.popup-footer-text a {
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 600;
}

.popup-footer-text a:hover {
    text-decoration: underline;
}

/* Animations */
.popup-enter {
    animation: popupFadeIn 0.3s ease-out;
}

.popup-leave {
    animation: popupFadeOut 0.2s ease-in;
}

@keyframes popupFadeIn {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes popupFadeOut {
    from {
        opacity: 1;
        transform: translateY(0);
    }
    to {
        opacity: 0;
        transform: translateY(-20px);
    }
}

/* Mobile */
@media (max-width: 768px) {
    .popup-body {
        padding: 40px 24px 32px;
    }
    
    .popup-title {
        font-size: 1.5rem;
    }
}
```

**Файл:** `static/js/scroll-popup.js`

```javascript
/**
 * Scroll Popup Component
 * Показує popup при скролі до кінця сторінки
 */

function scrollPopup() {
    return {
        showPopup: false,
        loading: false,
        formData: {
            email: '',
            password: ''
        },
        
        init() {
            // Перевірити чи popup вже був показаний
            const popupShown = localStorage.getItem('subscription_popup_shown');
            const popupDismissed = sessionStorage.getItem('popup_dismissed');
            
            if (popupShown || popupDismissed) {
                return;
            }
            
            // Відстежувати скрол
            let scrollTimeout;
            window.addEventListener('scroll', () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    this.checkScroll();
                }, 200);
            });
        },
        
        checkScroll() {
            // Перевірити чи користувач доскролив до 80% сторінки
            const scrollPercentage = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight;
            
            if (scrollPercentage >= 0.8 && !this.showPopup) {
                this.openPopup();
            }
        },
        
        openPopup() {
            this.showPopup = true;
            document.body.style.overflow = 'hidden';
            
            // Зберегти що popup був показаний
            localStorage.setItem('subscription_popup_shown', 'true');
        },
        
        closePopup() {
            this.showPopup = false;
            document.body.style.overflow = '';
            sessionStorage.setItem('popup_dismissed', 'true');
        },
        
        async handleRegister(event) {
            if (this.loading) return;
            
            this.loading = true;
            
            try {
                const response = await fetch('/accounts/api/quick-register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        email: this.formData.email,
                        password: this.formData.password,
                        source: 'scroll_popup',
                        discount_code: 'FIRST10'  // 10% знижка
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Перенаправити на сторінку підтвердження
                    window.location.href = data.redirect_url || '/';
                } else {
                    alert(data.message || 'Помилка реєстрації');
                }
            } catch (error) {
                console.error('Registration error:', error);
                alert('Помилка мережі. Спробуйте пізніше.');
            } finally {
                this.loading = false;
            }
        },
        
        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        }
    };
}
```

**Підключити в base.html:**

```html
<!-- В блоці head -->
<link rel="stylesheet" href="{% static 'css/components/scroll-popup.css' %}">

<!-- Перед закриттям body -->
<script src="{% static 'js/scroll-popup.js' %}"></script>

<!-- Включити partial на головній сторінці -->
{% block extra_content %}
    {% include 'partials/scroll-popup.html' %}
{% endblock %}
```

---

## 🏠 PHASE 3: ГОЛОВНА СТОРІНКА (3-4 год)

### 3.1 Оновити HERO секцію (карусель)

**Файл:** `templates/pages/home.html`

**Існуюча структура (рядки 15-44):**

```html
<section class="fullscreen-section hero-section" x-data="heroCarousel()">
    <div class="section-bg">
        <video class="section-bg-video" muted loop preload="metadata">
            <source src="{% static 'videos/hero-bg.mp4' %}" type="video/mp4">
        </video>
    </div>
    <div class="section-overlay section-overlay--gradient"></div>

    <div class="section-content">
        <div class="hero-badge">ГОЛОВНЕ ЗАРАЗ</div>
        <h1 class="hero-title" x-text="slides[currentSlide].title"></h1>
        <p class="hero-subtitle" x-text="slides[currentSlide].subtitle"></p>

        <div class="hero-buttons">
            <a :href="slides[currentSlide].ctaUrl" class="btn btn-primary">
                Дізнатись більше
            </a>
        </div>

        <div class="hero-slider-dots">
            <template x-for="(slide, index) in slides" :key="index">
                <button class="slider-dot" 
                        :class="{'active': currentSlide === index}"
                        @click="currentSlide = index"></button>
            </template>
        </div>
    </div>
</section>
```

**JavaScript (додати в static/js/home.js):**

```javascript
function heroCarousel() {
    return {
        currentSlide: 0,
        slides: [
            {
                title: 'Продуктивна практика у футбольних клубах',
                subtitle: 'Реальні кейси, стажування та менторинг з професіоналами індустрії',
                ctaUrl: '/about/'
            },
            {
                title: 'Ми відкрились!',
                subtitle: 'Приєднуйтесь до спільноти футбольних професіоналів',
                ctaUrl: '/about/'
            },
            {
                title: 'Івенти',
                subtitle: 'Вебінари, майстер-класи та форуми від експертів',
                ctaUrl: '/events/'
            },
            {
                title: 'Хаб знань — долучайся першим',
                subtitle: 'Ексклюзивні курси та матеріали для фахівців',
                ctaUrl: '/hub/'
            },
            {
                title: 'Ментор-коучинг',
                subtitle: 'Індивідуальний підхід до розвитку кожного футболіста',
                ctaUrl: '/mentor-coaching/'
            },
            {
                title: 'Про нас',
                subtitle: 'Дізнайтеся більше про нашу місію та команду',
                ctaUrl: '/about/'
            },
            {
                title: 'Напрямки діяльності',
                subtitle: '4 ключових напрямки комплексного розвитку',
                ctaUrl: '/about/#directions'
            }
        ],
        
        init() {
            // Автоматична прокрутка кожні 5 секунд
            setInterval(() => {
                this.nextSlide();
            }, 5000);
        },
        
        nextSlide() {
            this.currentSlide = (this.currentSlide + 1) % this.slides.length;
        },
        
        prevSlide() {
            this.currentSlide = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
        }
    };
}
```

**CSS (static/css/components/home.css):**

```css
/* Додати стиль для білих рамок */
.hero-section .section-content {
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 20px;
    padding: 60px 40px;
    backdrop-filter: blur(10px);
    background: rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
    .hero-section .section-content {
        border-width: 2px;
        padding: 40px 20px;
        border-radius: 16px;
    }
}
```

### 3.2 Замінити "3 напрямки" на "6 курсів"

**Файл:** `templates/pages/home.html`

**Замінити секцію (рядки 46-77):**

```html
<!-- 2. COURSES CAROUSEL SECTION -->
<section class="fullscreen-section courses-carousel-section">
    <div class="section-bg">
        <img class="section-bg-image" src="{% static 'images/courses-bg.jpg' %}" alt="Курси">
    </div>
    <div class="section-overlay section-overlay--light"></div>

    <div class="section-content">
        <h2 class="section-title">6 найголовніших курсів</h2>
        
        <div class="courses-carousel-wrapper" x-data="coursesCarousel()">
            <button class="carousel-nav carousel-nav-prev" @click="prevSlide()" 
                    :disabled="currentIndex === 0">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M15 18l-6-6 6-6"/>
                </svg>
            </button>
            
            <div class="courses-carousel">
                <div class="courses-carousel-track" 
                     :style="`transform: translateX(-${currentIndex * slideWidth}%)`">
                    {% for course in featured_courses|slice:":6" %}
                    <div class="course-slide">
                        <div class="course-card-modern">
                            <div class="course-image">
                                {% if course.thumbnail %}
                                <img src="{{ course.thumbnail.url }}" alt="{{ course.title }}">
                                {% else %}
                                <div class="course-image-placeholder"></div>
                                {% endif %}
                            </div>
                            <div class="course-content">
                                <span class="course-category">{{ course.category.name }}</span>
                                <h3 class="course-title">{{ course.title }}</h3>
                                <p class="course-description">{{ course.short_description|truncatewords:15 }}</p>
                                <a href="{{ course.get_absolute_url }}" class="course-link">
                                    Детальніше →
                                </a>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <button class="carousel-nav carousel-nav-next" @click="nextSlide()"
                    :disabled="currentIndex >= maxIndex">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 18l6-6-6-6"/>
                </svg>
            </button>
        </div>
    </div>
</section>
```

**JavaScript (додати в static/js/home.js):**

```javascript
function coursesCarousel() {
    return {
        currentIndex: 0,
        slidesPerView: 3,
        totalSlides: 6,
        
        get slideWidth() {
            return 100 / this.slidesPerView;
        },
        
        get maxIndex() {
            return Math.max(0, this.totalSlides - this.slidesPerView);
        },
        
        init() {
            // Adaptive slides per view
            this.updateSlidesPerView();
            window.addEventListener('resize', () => this.updateSlidesPerView());
        },
        
        updateSlidesPerView() {
            const width = window.innerWidth;
            if (width < 768) {
                this.slidesPerView = 1;
            } else if (width < 1024) {
                this.slidesPerView = 2;
            } else {
                this.slidesPerView = 3;
            }
        },
        
        nextSlide() {
            if (this.currentIndex < this.maxIndex) {
                this.currentIndex++;
            }
        },
        
        prevSlide() {
            if (this.currentIndex > 0) {
                this.currentIndex--;
            }
        }
    };
}
```

**CSS (додати в static/css/components/home.css):**

```css
/* Courses Carousel */
.courses-carousel-section {
    background: var(--color-bg-gray);
}

.courses-carousel-wrapper {
    position: relative;
    max-width: 1200px;
    margin: 0 auto;
}

.carousel-nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: white;
    border: none;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    z-index: 10;
    transition: all 0.3s ease;
}

.carousel-nav:hover:not(:disabled) {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-50%) scale(1.05);
}

.carousel-nav:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.carousel-nav-prev {
    left: -60px;
}

.carousel-nav-next {
    right: -60px;
}

.courses-carousel {
    overflow: hidden;
    padding: 20px 0;
}

.courses-carousel-track {
    display: flex;
    transition: transform 0.5s ease;
}

.course-slide {
    flex: 0 0 33.333%;
    padding: 0 15px;
}

.course-card-modern {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.course-card-modern:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.course-image {
    width: 100%;
    height: 200px;
    overflow: hidden;
    background: var(--color-bg-gray);
}

.course-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.course-image-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.course-content {
    padding: 24px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.course-category {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.course-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 12px;
    line-height: 1.3;
}

.course-description {
    font-size: 0.9rem;
    color: var(--color-text-light);
    line-height: 1.5;
    margin-bottom: 20px;
    flex: 1;
}

.course-link {
    color: var(--color-primary);
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.course-link:hover {
    text-decoration: underline;
}

/* Responsive */
@media (max-width: 1024px) {
    .course-slide {
        flex: 0 0 50%;
    }
    
    .carousel-nav-prev {
        left: -40px;
    }
    
    .carousel-nav-next {
        right: -40px;
    }
}

@media (max-width: 768px) {
    .course-slide {
        flex: 0 0 100%;
    }
    
    .carousel-nav-prev,
    .carousel-nav-next {
        width: 40px;
        height: 40px;
    }
    
    .carousel-nav-prev {
        left: 0;
    }
    
    .carousel-nav-next {
        right: 0;
    }
}
```

### 3.3 Додати секцію Ментор-коучинг

**Файл:** `templates/pages/home.html`

**Додати після секції курсів:**

```html
<!-- 3. MENTOR-COACHING SECTION -->
<section class="fullscreen-section mentor-coaching-section">
    <div class="section-bg">
        <img class="section-bg-image" src="{% static 'images/mentor-bg.jpg' %}" alt="Ментор-коучинг">
    </div>
    <div class="section-overlay section-overlay--dark"></div>

    <div class="section-content">
        <h2 class="section-title">Ментор-коучинг</h2>
        <h3 class="section-subtitle">Екосистема комплексного розвитку футболіста</h3>
        
        <div class="hexagon-scheme">
            <!-- Центр -->
            <div class="hexagon hexagon-center">
                <img src="{% static 'images/playvision-logo.svg' %}" alt="Play Vision" class="center-logo">
            </div>
            
            <!-- 4 напрямки -->
            <div class="hexagon hexagon-1">
                <div class="hexagon-content">
                    <div class="hexagon-icon">📅</div>
                    <h4>Івенти</h4>
                </div>
            </div>
            
            <div class="hexagon hexagon-2">
                <div class="hexagon-content">
                    <div class="hexagon-icon">👨‍🏫</div>
                    <h4>Ментор-коучінг</h4>
                </div>
            </div>
            
            <div class="hexagon hexagon-3">
                <div class="hexagon-content">
                    <div class="hexagon-icon">📚</div>
                    <h4>Хаб знань</h4>
                </div>
            </div>
            
            <div class="hexagon hexagon-4">
                <div class="hexagon-content">
                    <div class="hexagon-icon">💡</div>
                    <h4>Інновації і технології</h4>
                </div>
            </div>
        </div>
        
        <div class="mentor-cta">
            <a href="/mentor-coaching/" class="btn btn-primary btn-large">
                Дізнатись більше
            </a>
        </div>
    </div>
</section>
```

**CSS (додати в static/css/components/home.css):**

```css
/* Mentor-Coaching Section */
.mentor-coaching-section {
    background: var(--color-bg);
    text-align: center;
    color: white;
}

.section-subtitle {
    font-size: 1.25rem;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 60px;
}

.hexagon-scheme {
    position: relative;
    width: 100%;
    max-width: 600px;
    height: 500px;
    margin: 0 auto 60px;
}

.hexagon {
    position: absolute;
    width: 150px;
    height: 150px;
    background: white;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.hexagon:hover {
    transform: scale(1.1);
    box-shadow: 0 8px 32px rgba(255, 107, 53, 0.3);
}

.hexagon-center {
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 180px;
    height: 180px;
    background: var(--color-primary);
}

.center-logo {
    max-width: 100px;
    height: auto;
}

.hexagon-1 {
    left: 50%;
    top: 0;
    transform: translateX(-50%);
}

.hexagon-2 {
    right: 0;
    top: 35%;
}

.hexagon-3 {
    left: 0;
    top: 35%;
}

.hexagon-4 {
    left: 50%;
    bottom: 0;
    transform: translateX(-50%);
}

.hexagon-content {
    text-align: center;
}

.hexagon-icon {
    font-size: 2rem;
    margin-bottom: 8px;
}

.hexagon h4 {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-text);
    margin: 0;
}

.mentor-cta {
    margin-top: 40px;
}

/* Responsive */
@media (max-width: 768px) {
    .hexagon-scheme {
        height: 400px;
        max-width: 400px;
    }
    
    .hexagon {
        width: 100px;
        height: 100px;
    }
    
    .hexagon-center {
        width: 120px;
        height: 120px;
    }
    
    .center-logo {
        max-width: 60px;
    }
    
    .hexagon-icon {
        font-size: 1.5rem;
    }
    
    .hexagon h4 {
        font-size: 0.75rem;
    }
}
```

### 3.4 Змінити "З ким ти працюєш" → "Команда професіоналів"

**Файл:** `templates/pages/home.html`

**Оновити рядок 141:**

```html
<h2 class="section-title">Команда професіоналів</h2>
```

**Додати опис експертів (чекаємо від клієнта):**

```html
<div class="expert-card">
    <div class="expert-photo">
        <img src="{% static 'images/expert-otte.jpg' %}" alt="Dr. Fabian Otte">
    </div>
    <h3 class="expert-name">Dr. Fabian Otte</h3>
    <p class="expert-specialization">Coaching Principles, Skill Acquisition</p>
    <!-- ДОДАТИ ОПИС -->
    <p class="expert-description">
        <!-- Текст від клієнта -->
    </p>
    <a href="/experts/otte/" class="expert-link">Огляд профілю →</a>
</div>
```

### 3.5 Видалити секцію "Наша структура та цінності"

**Файл:** `templates/pages/home.html`

**Видалити рядки 181-236:**

```html
<!-- ВИДАЛИТИ ВСЮ СЕКЦІЮ -->
<!-- <section class="fullscreen-section values-section">
    ...
</section> -->
```

**Файл:** `static/css/components/home.css`

**Видалити рядки 363-415:**

```css
/* ВИДАЛИТИ */
/* .values-section { ... } */
```

### 3.6 Підключити popup на головній

**Файл:** `templates/pages/home.html`

**В кінці файлу перед {% endblock %}:**

```html
{% block extra_content %}
    {% include 'partials/scroll-popup.html' %}
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/home.js' %}"></script>
{% endblock %}
```

---

## 📚 PHASE 4: ХАБ ЗНАНЬ (2-3 год)

### 4.1 Додати кнопку закриття банера

**Файл:** `templates/hub/course_list.html`

**Оновити рядки 37-48:**

```html
<div class="subscription-banner" id="subscription-banner" x-data="{ bannerVisible: true }" x-show="bannerVisible">
    <button class="banner-close-btn" @click="bannerVisible = false; closeBanner()" 
            aria-label="Закрити">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
    </button>
    <div class="container">
        <div class="subscription-banner-content">
            <h2>Оформи підписку, стань частиною спільноти фахівців!</h2>
            <p>Отримай доступ до всіх курсів та матеріалів від провідних експертів</p>
            <a href="{% url 'core:coming_soon' %}?page=subscription" class="btn btn-primary">
                Оформити підписку
            </a>
        </div>
    </div>
</div>
```

**CSS (static/css/components/hub.css):**

```css
/* Додати після .subscription-banner */
.subscription-banner {
    position: relative; /* ДОДАТИ */
}

.banner-close-btn {
    position: absolute;
    top: 16px;
    right: 20px;
    background: transparent;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    opacity: 0.8;
    transition: opacity 0.3s ease;
    padding: 8px;
    line-height: 1;
    z-index: 10;
}

.banner-close-btn:hover {
    opacity: 1;
}

.banner-close-btn svg {
    display: block;
}
```

**JavaScript (додати в static/js/hub.js або створити):**

```javascript
function closeBanner() {
    localStorage.setItem('subscription-banner-closed', 'true');
}

// Перевірити при завантаженні
document.addEventListener('DOMContentLoaded', () => {
    const bannerClosed = localStorage.getItem('subscription-banner-closed');
    if (bannerClosed === 'true') {
        const banner = document.getElementById('subscription-banner');
        if (banner) {
            banner.style.display = 'none';
        }
    }
});
```

### 4.2 Видалити "Найближчі події"

**Файл:** `templates/hub/course_list.html`

**Видалити рядки 50-140:**

```html
<!-- ВИДАЛИТИ БЛОК -->
<!-- <section class="upcoming-events-section">
    ...
</section> -->
```

### 4.3 Замінити цитати на одну "Цитата місяця"

**Файл:** `templates/hub/course_list.html`

**Замінити рядки 163-244:**

```html
<!-- Monthly Expert Quote -->
<section class="monthly-quote-section" role="region" aria-label="Цитата місяця">
    <div class="container">
        <h2 class="section-title">Цитата місяця</h2>

        {% if monthly_quote %}
        <div class="single-quote">
            <div class="expert-avatar">
                {% if monthly_quote.expert_photo %}
                <img src="{{ monthly_quote.expert_photo.url }}" alt="{{ monthly_quote.expert_name }}"
                     class="expert-photo">
                {% else %}
                <div class="expert-photo-placeholder">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                    </svg>
                </div>
                {% endif %}
                <div class="expert-info">
                    <span class="expert-name">{{ monthly_quote.expert_name }}</span>
                    <span class="expert-role">{{ monthly_quote.expert_role }}</span>
                </div>
            </div>
            <blockquote class="quote-text">
                {{ monthly_quote.quote_text }}
            </blockquote>
        </div>
        {% else %}
        <div class="no-quote">
            <p>Цитату місяця ще не додано</p>
        </div>
        {% endif %}
    </div>
</section>
```

**CSS (static/css/components/hub.css):**

```css
/* Monthly Quote */
.monthly-quote-section {
    padding: 60px 0;
    background: var(--hub-bg-gray);
}

.single-quote {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    padding: 40px;
    box-shadow: var(--hub-shadow);
}

.expert-avatar {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 30px;
}

.expert-photo,
.expert-photo-placeholder {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
}

.expert-photo-placeholder {
    background: var(--hub-bg-gray);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--hub-text-light);
}

.expert-info {
    flex: 1;
}

.expert-name {
    display: block;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--hub-text);
    margin-bottom: 4px;
}

.expert-role {
    display: block;
    font-size: 0.9rem;
    color: var(--hub-text-light);
}

.quote-text {
    font-size: 1.125rem;
    line-height: 1.7;
    color: var(--hub-text);
    font-style: italic;
    margin: 0;
    padding-left: 30px;
    border-left: 4px solid var(--hub-primary);
}

.no-quote {
    text-align: center;
    padding: 40px;
    color: var(--hub-text-light);
}

/* Responsive */
@media (max-width: 768px) {
    .single-quote {
        padding: 30px 20px;
    }
    
    .expert-avatar {
        flex-direction: column;
        text-align: center;
    }
    
    .quote-text {
        font-size: 1rem;
        padding-left: 20px;
    }
}
```

### 4.4 Оновити "Головні матеріали" → "Освітні продукти"

**Файл:** `templates/hub/course_list.html`

**Оновити рядок 285:**

```html
<h2 class="section-title">Освітні продукти</h2>
```

**Змінити логіку відображення (рядки 283-350):**

```html
<section class="educational-products">
    <div class="container">
        <h2 class="section-title">Освітні продукти</h2>
        
        <div class="products-grid">
            {% for course in courses %}
            <div class="product-card {% if course.is_featured %}featured{% endif %}">
                {% if course.is_featured %}
                <span class="featured-badge">ТОП-ПРОДУКТ</span>
                {% endif %}
                
                <div class="product-image">
                    {% if course.thumbnail %}
                    <img src="{{ course.thumbnail.url }}" alt="{{ course.title }}">
                    {% else %}
                    <div class="product-image-placeholder"></div>
                    {% endif %}
                </div>
                
                <div class="product-content">
                    <span class="product-category">{{ course.category.name }}</span>
                    <h3 class="product-title">{{ course.title }}</h3>
                    <p class="product-description">{{ course.short_description|truncatewords:20 }}</p>
                    
                    <div class="product-footer">
                        <div class="product-price">
                            {% if course.is_free %}
                            <span class="price-free">Безкоштовно</span>
                            {% else %}
                            <span class="price-amount">{{ course.price }} ₴</span>
                            {% endif %}
                        </div>
                        <a href="{{ course.get_absolute_url }}" class="btn btn-outline btn-small">
                            Детальніше
                        </a>
                    </div>
                </div>
            </div>
            {% empty %}
            <div class="no-products">
                <p>Курси поки що недоступні</p>
            </div>
            {% endfor %}
        </div>
        
        <!-- Pagination -->
        {% if is_paginated %}
        <div class="pagination">
            {% if page_obj.has_previous %}
            <a href="?page={{ page_obj.previous_page_number }}" class="pagination-link">Попередня</a>
            {% endif %}
            
            <span class="pagination-current">
                Сторінка {{ page_obj.number }} з {{ page_obj.paginator.num_pages }}
            </span>
            
            {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}" class="pagination-link">Наступна</a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</section>
```

**CSS (static/css/components/hub.css):**

```css
/* Educational Products */
.educational-products {
    padding: 60px 0;
    background: white;
}

.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 40px;
}

.product-card {
    background: white;
    border: 2px solid var(--hub-border);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    position: relative;
}

.product-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--hub-shadow-hover);
}

.product-card.featured {
    border: 3px solid var(--hub-primary);
    box-shadow: 0 8px 32px rgba(255, 107, 53, 0.15);
}

.featured-badge {
    position: absolute;
    top: 16px;
    right: 16px;
    background: var(--hub-primary);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    z-index: 5;
}

.product-image {
    width: 100%;
    height: 200px;
    overflow: hidden;
    background: var(--hub-bg-gray);
}

.product-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.product-image-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.product-content {
    padding: 24px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.product-category {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--hub-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.product-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--hub-text);
    margin-bottom: 12px;
    line-height: 1.4;
}

.product-description {
    font-size: 0.9rem;
    color: var(--hub-text-light);
    line-height: 1.6;
    margin-bottom: 20px;
    flex: 1;
}

.product-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-top: auto;
}

.product-price {
    flex: 1;
}

.price-free {
    color: #28a745;
    font-weight: 600;
    font-size: 1rem;
}

.price-amount {
    color: var(--hub-text);
    font-weight: 700;
    font-size: 1.25rem;
}

.no-products {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    color: var(--hub-text-light);
}

/* Pagination */
.pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    margin-top: 60px;
}

.pagination-link {
    padding: 10px 20px;
    background: var(--hub-primary);
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
}

.pagination-link:hover {
    background: var(--hub-primary-dark);
    transform: translateY(-2px);
}

.pagination-current {
    color: var(--hub-text-light);
    font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
    .products-grid {
        grid-template-columns: 1fr;
        gap: 20px;
    }
}
```

### 4.5 Оновити фільтри

**Файл:** `templates/hub/course_list.html`

**Замінити блок фільтрів (рядки 395-468):**

```html
<div class="filters-content scrollable" id="filters-content">
    <form method="get" id="filterForm">
        {% if request.GET.q %}
        <input type="hidden" name="q" value="{{ request.GET.q }}">
        {% endif %}

        <!-- Category Filter (залишити) -->
        <div class="filter-group">
            <h4>За напрямками</h4>
            <div class="filter-options">
                {% for category in categories %}
                <label class="filter-option">
                    <input type="radio" name="category" value="{{ category.slug }}" 
                           {% if current_category == category.slug %}checked{% endif %}>
                    <span>{{ category.name }}</span>
                </label>
                {% endfor %}
            </div>
        </div>

        <!-- ВИДАЛИТИ: Difficulty Filter -->
        <!-- ВИДАЛИТИ: Price Filter -->
        <!-- ВИДАЛИТИ: Duration Filter -->

        <!-- ДОДАТИ: Interest Filters -->
        <div class="filter-group">
            <h4>Інтереси</h4>
            <div class="filter-options">
                {% for interest in interests %}
                <label class="filter-option">
                    <input type="checkbox" name="interest" value="{{ interest.slug }}"
                           {% if current_interest == interest.slug %}checked{% endif %}>
                    <span>{{ interest.name }}</span>
                </label>
                {% endfor %}
            </div>
        </div>

        <!-- ДОДАТИ: Training Specialization (з під-фільтрами) -->
        <div class="filter-group" x-data="{ expanded: false }">
            <h4>
                <label class="filter-option filter-option-parent">
                    <input type="checkbox" @change="expanded = !expanded">
                    <span>Тренерство</span>
                </label>
            </h4>
            
            <div class="sub-filters" x-show="expanded" x-transition>
                <label class="filter-option sub-filter">
                    <input type="checkbox" name="training_type" value="goalkeeper">
                    <span>Тренер воротарів</span>
                </label>
                <label class="filter-option sub-filter">
                    <input type="checkbox" name="training_type" value="youth">
                    <span>Дитячий тренер</span>
                </label>
                <label class="filter-option sub-filter">
                    <input type="checkbox" name="training_type" value="fitness">
                    <span>Тренер ЗФП</span>
                </label>
                <label class="filter-option sub-filter">
                    <input type="checkbox" name="training_type" value="professional">
                    <span>Тренер професійних команд</span>
                </label>
            </div>
        </div>

        <!-- ДОДАТИ: Інші фільтри -->
        <div class="filter-group">
            <h4>Менеджмент</h4>
            <label class="filter-option">
                <input type="checkbox" name="interest" value="management">
                <span>Менеджмент</span>
            </label>
        </div>

        <div class="filter-actions">
            <button type="submit" class="btn btn-primary btn-block">
                Застосувати
            </button>
            <button type="button" class="btn btn-outline btn-block" @click="clearFilters()">
                Скинути все
            </button>
        </div>
    </form>
</div>
```

**CSS для скролінгу (додати в hub.css):**

```css
.filters-content.scrollable {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 10px;
}

.filters-content.scrollable::-webkit-scrollbar {
    width: 6px;
}

.filters-content.scrollable::-webkit-scrollbar-track {
    background: var(--hub-bg-gray);
    border-radius: 3px;
}

.filters-content.scrollable::-webkit-scrollbar-thumb {
    background: var(--hub-primary);
    border-radius: 3px;
}

.filters-content.scrollable::-webkit-scrollbar-thumb:hover {
    background: var(--hub-primary-dark);
}

.sub-filters {
    margin-left: 20px;
    margin-top: 10px;
    padding-left: 15px;
    border-left: 2px solid var(--hub-border);
}

.sub-filter {
    font-size: 0.9rem;
}
```

---

## 📅 PHASE 5: ІВЕНТИ (1 год)

### 5.1 Обмежити календар (1 подія на день)

**Файл:** `static/js/events.js`

**Оновити функцію generateVisibleDays() (рядки 247-328):**

```javascript
generateVisibleDays() {
    this.visibleDays = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    console.log(`🗓️ Generating visible days for week: ${this.currentWeekStart.toDateString()}`);
    console.log(`📋 Total events available: ${this.allEvents.length}`);

    for (let i = 0; i < 7; i++) {
        const date = new Date(this.currentWeekStart);
        date.setDate(this.currentWeekStart.getDate() + i);
        date.setHours(0, 0, 0, 0);

        // Find events for this specific date
        const dayEvents = this.allEvents.filter(event => {
            const eventDate = new Date(event.start_datetime);
            eventDate.setHours(0, 0, 0, 0);
            const match = eventDate.getTime() === date.getTime();

            if (match) {
                console.log(`🎯 Found event "${event.title}" for ${date.toDateString()}`);
            }

            return match;
        }).slice(0, 1); // ⚠️ ОБМЕЖЕННЯ: лише 1 подія

        // Apply filters
        const filteredEvents = dayEvents.filter(event => {
            let matchesFilter = true;

            if (this.selectedType !== 'all') {
                matchesFilter = matchesFilter && event.type === this.selectedType;
            }

            if (this.selectedFormat !== 'all') {
                matchesFilter = matchesFilter && event.format === this.selectedFormat;
            }

            return matchesFilter;
        });

        this.visibleDays.push({
            date: date.toISOString(),
            dayNumber: date.getDate(),
            dayName: date.toLocaleDateString('uk-UA', { weekday: 'short' }),
            events: filteredEvents,
            isToday: date.getTime() === today.getTime(),
            isPast: date < today,
            isWeekend: date.getDay() === 0 || date.getDay() === 6
        });
    }

    this.updateSidebarEvents();
}
```

**HTML Template (перевірити рядки 81-98 в event_list.html):**

Переконатись що відображається тільки перша подія:

```html
<div class="day-events">
    <template x-for="event in day.events" :key="event.id">
        <!-- Буде показано лише 1 подію завдяки slice(0, 1) вище -->
        <a :href="event.url" class="event-card">
            <div class="event-type-badge" x-text="event.type_display"></div>
            <div class="event-main-info">
                <h4 class="event-title" x-text="event.title"></h4>
                <div class="event-time" x-text="event.time"></div>
            </div>
        </a>
    </template>
</div>
```

### 5.2 Видалити фільтр ціни

**Файл:** `templates/events/event_list.html`

**Видалити рядки 247-267:**

```html
<!-- ВИДАЛИТИ БЛОК -->
<!-- <div class="sidebar-section">
    <h3 class="sidebar-title">Ціна</h3>
    <div class="filter-group">
        <label class="filter-option">
            <input type="radio" name="price" value="all">
            <span class="filter-label">Всі події</span>
        </label>
        <label class="filter-option">
            <input type="radio" name="price" value="free">
            <span class="filter-label">Безкоштовні</span>
        </label>
        <label class="filter-option">
            <input type="radio" name="price" value="paid">
            <span class="filter-label">Платні</span>
        </label>
    </div>
</div> -->
```

**Файл:** `apps/events/views.py`

**Видалити код фільтрації по ціні (якщо є):**

```python
# ВИДАЛИТИ або закоментувати
# price_filter = self.request.GET.get('price')
# if price_filter == 'free':
#     queryset = queryset.filter(is_free=True)
# elif price_filter == 'paid':
#     queryset = queryset.filter(is_free=False)
```

---

## 👤 PHASE 6: ОСОБИСТИЙ КАБІНЕТ (2-3 год)

### 6.1 Оновити список інтересів

**Файл:** `templates/account/cabinet.html`

**Замінити рядки 81-89:**

```html
<div class="interests-section">
    <label>Напрямки (інтереси)</label>
    <div class="interests-list">
        {% for interest in interests %}
        <label class="interest-item">
            <input type="checkbox" 
                   name="interests" 
                   value="{{ interest.id }}"
                   {% if interest in user.profile.interests.all %}checked{% endif %}>
            <span class="interest-label">
                <span class="interest-number">{{ forloop.counter }}.</span>
                {{ interest.name }}
            </span>
        </label>
        {% endfor %}
    </div>
</div>
```

**CSS (static/css/components/cabinet.css):**

```css
/* Interests Section */
.interests-section {
    margin-bottom: 24px;
}

.interests-section > label {
    display: block;
    font-weight: 500;
    color: var(--color-text);
    margin-bottom: 12px;
    font-size: 14px;
}

.interests-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.interest-item {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    background: white;
    border: 2px solid var(--color-border);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.interest-item:hover {
    border-color: var(--color-primary);
    background: rgba(255, 107, 53, 0.05);
}

.interest-item input[type="checkbox"] {
    margin-right: 12px;
    width: 18px;
    height: 18px;
    cursor: pointer;
}

.interest-item input[type="checkbox"]:checked ~ .interest-label {
    color: var(--color-primary);
    font-weight: 600;
}

.interest-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--color-text);
    transition: all 0.3s ease;
}

.interest-number {
    font-weight: 700;
    color: var(--color-text-light);
    min-width: 20px;
}

.interest-item input[type="checkbox"]:checked ~ .interest-label .interest-number {
    color: var(--color-primary);
}
```

**Backend (apps/accounts/cabinet_views.py):**

**Додати інтереси в контекст:**

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # ... існуючий код ...
    
    # ДОДАТИ: Інтереси у правильному порядку
    from apps.content.models import Tag
    context['interests'] = Tag.objects.filter(
        tag_type='interest'
    ).order_by('display_order')
    
    return context
```

### 6.2 Виправити кнопку "ЗБЕРЕГТИ"

**Файл:** `templates/account/cabinet.html`

**Замінити рядок 91:**

```html
<button type="submit" class="btn-save">ЗБЕРЕГТИ</button>
```

### 6.3 Перевірити функцію завантаження фото

**Файл:** `static/js/cabinet.js`

**Функція handleAvatarUpload (рядки 178-212) виглядає правильно.**

**Додати валідацію розміру файлу в backend:**

**Файл:** `apps/accounts/cabinet_views.py`

**Оновити UpdateProfileView (рядки 256-301):**

```python
class UpdateProfileView(LoginRequiredMixin, View):
    """AJAX оновлення профілю"""
    
    def post(self, request):
        try:
            profile = getattr(request.user, 'profile', None)
            if not profile:
                from apps.accounts.models import Profile
                profile = Profile.objects.create(user=request.user)
            
            # Отримати дані з POST
            data = {
                'first_name': request.POST.get('first_name', '').strip(),
                'last_name': request.POST.get('last_name', '').strip(),
                'birth_date': request.POST.get('birth_date', '').strip(),
                'profession': request.POST.get('profession', '').strip(),
            }
            
            # Видалити пусті значення
            data = {k: v for k, v in data.items() if v}
            
            # Оновити профіль
            for field, value in data.items():
                setattr(profile, field, value)
            
            # ⚠️ ПОКРАЩЕНА ОБРОБКА АВАТАРА
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                
                # Валідація розміру (5MB)
                MAX_SIZE = 5 * 1024 * 1024
                if avatar_file.size > MAX_SIZE:
                    return JsonResponse({
                        'success': False,
                        'message': 'Файл занадто великий (максимум 5MB)'
                    })
                
                # Валідація типу
                ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
                if avatar_file.content_type not in ALLOWED_TYPES:
                    return JsonResponse({
                        'success': False,
                        'message': 'Дозволені лише JPEG, PNG, WEBP'
                    })
                
                # Видалити старий аватар
                if profile.avatar:
                    profile.avatar.delete(save=False)
                
                # Зберегти новий
                profile.avatar = avatar_file
            
            # Обробити інтереси
            if 'interests' in request.POST:
                interest_ids = request.POST.getlist('interests')
                profile.interests.set(interest_ids)
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Профіль успішно оновлено',
                'avatar_url': profile.get_avatar_url() if profile.avatar else None
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка оновлення профілю: {str(e)}'
            })
```

### 6.4 Програма лояльності - додати кнопку "Правила"

**Файл:** `templates/account/tabs/loyalty.html`

**Додати після рядка 108:**

```html
    </div>
</div>

<!-- НОВИЙ БЛОК -->
<div class="loyalty-rules-section">
    <div class="info-card">
        <h3>Детальна інформація</h3>
        <p>Ознайомтеся з повними правилами Програми лояльності</p>
        <a href="{% url 'loyalty:rules' %}" class="btn btn-outline btn-large">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <line x1="10" y1="9" x2="8" y2="9"/>
            </svg>
            Правила Програми Лояльності
        </a>
    </div>
</div>

<!-- Як заробляти бали -->
```

**CSS (додати в static/css/components/cabinet.css):**

```css
/* Loyalty Rules Section */
.loyalty-rules-section {
    margin: 40px 0;
}

.loyalty-rules-section .info-card {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
}

.loyalty-rules-section .info-card h3 {
    color: white;
}

.loyalty-rules-section .info-card p {
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 24px;
}

.loyalty-rules-section .btn-outline {
    background: white;
    color: #667eea;
    border-color: white;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.loyalty-rules-section .btn-outline:hover {
    background: rgba(255, 255, 255, 0.9);
    transform: translateY(-2px);
}
```

### 6.5 Створити сторінку "Правила Програми Лояльності"

**Файл:** `templates/loyalty/rules.html`

```html
{% extends 'base/base.html' %}
{% load static %}

{% block title %}Правила Програми Лояльності - Play Vision{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/components/loyalty-rules.css' %}">
{% endblock %}

{% block content %}
<div class="loyalty-rules-page">
    <div class="container">
        <!-- Hero Section -->
        <div class="rules-hero">
            <h1 class="page-title">Правила Програми Лояльності</h1>
            <p class="page-subtitle">
                Дізнайтеся, як накопичувати бали, отримувати знижки та користуватися перевагами
            </p>
        </div>

        <!-- Navigation -->
        <nav class="rules-navigation">
            <a href="#general" class="nav-link">Загальні положення</a>
            <a href="#earning" class="nav-link">Як накопичувати</a>
            <a href="#tiers" class="nav-link">Рівні</a>
            <a href="#benefits" class="nav-link">Переваги</a>
            <a href="#expiry" class="nav-link">Термін дії</a>
        </nav>

        <!-- Content Sections -->
        <section id="general" class="rules-section">
            <h2 class="section-title">1. Загальні положення</h2>
            <div class="section-content">
                <p>
                    Програма лояльності Play Vision - це система винагород для наших клієнтів,
                    яка дозволяє отримувати бали за активність та обмінювати їх на знижки.
                </p>
                <ul>
                    <li>Програма доступна для всіх зареєстрованих користувачів</li>
                    <li>Участь у програмі безкоштовна</li>
                    <li>Бали нараховуються автоматично</li>
                    <li>Знижки застосовуються при оформленні замовлення</li>
                </ul>
            </div>
        </section>

        <section id="earning" class="rules-section">
            <h2 class="section-title">2. Як накопичувати бали</h2>
            <div class="section-content">
                <div class="earning-grid">
                    <div class="earning-card">
                        <div class="earning-icon">🛒</div>
                        <h3>Покупки</h3>
                        <p>1 бал за кожну 10₴</p>
                        <span class="earning-detail">Бали нараховуються після підтвердження платежу</span>
                    </div>
                    
                    <div class="earning-card">
                        <div class="earning-icon">📝</div>
                        <h3>Заповнення профілю</h3>
                        <p>50 балів одноразово</p>
                        <span class="earning-detail">За повністю заповнений профіль</span>
                    </div>
                    
                    <div class="earning-card">
                        <div class="earning-icon">🎓</div>
                        <h3>Завершення курсів</h3>
                        <p>10-30 балів за курс</p>
                        <span class="earning-detail">Залежно від складності курсу</span>
                    </div>
                    
                    <div class="earning-card">
                        <div class="earning-icon">📅</div>
                        <h3>Відвідування івентів</h3>
                        <p>20 балів за подію</p>
                        <span class="earning-detail">За кожний відвіданий івент</span>
                    </div>
                    
                    <div class="earning-card">
                        <div class="earning-icon">🎂</div>
                        <h3>День народження</h3>
                        <p>100 балів щорічно</p>
                        <span class="earning-detail">Автоматично у день народження</span>
                    </div>
                    
                    <div class="earning-card">
                        <div class="earning-icon">👥</div>
                        <h3>Реферальна програма</h3>
                        <p>5% від покупок друга</p>
                        <span class="earning-detail">За кожного запрошеного користувача</span>
                    </div>
                </div>
            </div>
        </section>

        <section id="tiers" class="rules-section">
            <h2 class="section-title">3. Рівні лояльності</h2>
            <div class="section-content">
                {% if loyalty_tiers %}
                <div class="tiers-grid">
                    {% for tier in loyalty_tiers %}
                    <div class="tier-card tier-{{ tier.name|lower }}">
                        <div class="tier-badge">{{ tier.name }}</div>
                        <div class="tier-requirements">
                            {% if tier.points_required == 0 %}
                            Початковий рівень
                            {% else %}
                            {{ tier.points_required }}+ балів
                            {% endif %}
                        </div>
                        <div class="tier-discount">
                            Знижка {{ tier.discount_percentage }}%
                        </div>
                        <div class="tier-benefits-list">
                            <h4>Переваги:</h4>
                            <ul>
                                {% for benefit in tier.benefits %}
                                <li>{{ benefit }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p>Інформація про рівні лояльності завантажується...</p>
                {% endif %}
            </div>
        </section>

        <section id="benefits" class="rules-section">
            <h2 class="section-title">4. Знижки та переваги</h2>
            <div class="section-content">
                <div class="benefits-list">
                    <div class="benefit-item">
                        <div class="benefit-icon">💎</div>
                        <div class="benefit-content">
                            <h3>Накопичувальна знижка</h3>
                            <p>Чим вище рівень - тим більша знижка на всі продукти та послуги</p>
                        </div>
                    </div>
                    
                    <div class="benefit-item">
                        <div class="benefit-icon">🎁</div>
                        <div class="benefit-content">
                            <h3>Спеціальні пропозиції</h3>
                            <p>Ексклюзивні знижки та акції тільки для учасників програми</p>
                        </div>
                    </div>
                    
                    <div class="benefit-item">
                        <div class="benefit-icon">🎫</div>
                        <div class="benefit-content">
                            <h3>Пріоритет на івенти</h3>
                            <p>Ранній доступ до реєстрації на популярні заходи</p>
                        </div>
                    </div>
                    
                    <div class="benefit-item">
                        <div class="benefit-icon">📧</div>
                        <div class="benefit-content">
                            <h3>Персональні пропозиції</h3>
                            <p>Рекомендації курсів та івентів на основі ваших інтересів</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="expiry" class="rules-section">
            <h2 class="section-title">5. Термін дії балів</h2>
            <div class="section-content">
                <div class="expiry-info">
                    <div class="info-block">
                        <h3>Термін дії балів</h3>
                        <p>Бали діють протягом <strong>12 місяців</strong> з моменту нарахування.</p>
                        <p>Бали, які не були використані протягом цього періоду, анулюються автоматично.</p>
                    </div>
                    
                    <div class="info-block">
                        <h3>Відстеження балів</h3>
                        <p>Ви завжди можете переглянути свій баланс та історію нарахувань в особистому кабінеті.</p>
                        <p>Система автоматично нагадує про бали, які скоро згорають.</p>
                    </div>
                    
                    <div class="info-block">
                        <h3>Збереження рівня</h3>
                        <p>Ваш рівень лояльності зберігається протягом року при умові активності.</p>
                        <p>Якщо протягом 12 місяців не було жодної покупки - рівень може знизитись.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA Section -->
        <section class="rules-cta">
            <div class="cta-content">
                <h2>Готові розпочати?</h2>
                <p>Приєднуйтесь до програми лояльності та отримуйте бонуси вже сьогодні!</p>
                <div class="cta-buttons">
                    {% if user.is_authenticated %}
                    <a href="{% url 'cabinet:loyalty' %}" class="btn btn-primary btn-large">
                        Переглянути мій баланс
                    </a>
                    {% else %}
                    <a href="{% url 'accounts:register' %}" class="btn btn-primary btn-large">
                        Зареєструватись
                    </a>
                    <a href="{% url 'accounts:login' %}" class="btn btn-outline btn-large">
                        Увійти
                    </a>
                    {% endif %}
                </div>
            </div>
        </section>

        <!-- Back to Cabinet -->
        <div class="back-link">
            <a href="{% url 'cabinet:loyalty' %}">← Повернутись до кабінету</a>
        </div>
    </div>
</div>
{% endblock %}
```

**CSS:** `static/css/components/loyalty-rules.css`

```css
/* Loyalty Rules Page */
.loyalty-rules-page {
    min-height: 100vh;
    background: var(--color-bg-gray);
    padding: 40px 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Hero */
.rules-hero {
    text-align: center;
    padding: 60px 0;
    background: white;
    border-radius: 16px;
    margin-bottom: 40px;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 16px;
}

.page-subtitle {
    font-size: 1.125rem;
    color: var(--color-text-light);
    max-width: 600px;
    margin: 0 auto;
}

/* Navigation */
.rules-navigation {
    display: flex;
    justify-content: center;
    gap: 24px;
    flex-wrap: wrap;
    padding: 24px;
    background: white;
    border-radius: 12px;
    margin-bottom: 40px;
}

.rules-navigation .nav-link {
    padding: 10px 20px;
    border-radius: 8px;
    text-decoration: none;
    color: var(--color-text);
    font-weight: 500;
    transition: all 0.3s ease;
}

.rules-navigation .nav-link:hover {
    background: var(--color-primary);
    color: white;
}

/* Sections */
.rules-section {
    background: white;
    border-radius: 16px;
    padding: 40px;
    margin-bottom: 30px;
}

.section-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 3px solid var(--color-primary);
}

.section-content {
    color: var(--color-text);
    line-height: 1.7;
}

.section-content p {
    margin-bottom: 16px;
}

.section-content ul {
    margin: 20px 0;
    padding-left: 30px;
}

.section-content ul li {
    margin-bottom: 12px;
}

/* Earning Grid */
.earning-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    margin-top: 30px;
}

.earning-card {
    background: var(--color-bg-gray);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
}

.earning-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.earning-icon {
    font-size: 3rem;
    margin-bottom: 16px;
}

.earning-card h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 8px;
}

.earning-card p {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: 12px;
}

.earning-detail {
    display: block;
    font-size: 0.875rem;
    color: var(--color-text-light);
}

/* Tiers Grid */
.tiers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    margin-top: 30px;
}

.tier-card {
    border-radius: 12px;
    padding: 32px 24px;
    text-align: center;
    border: 3px solid;
    transition: all 0.3s ease;
}

.tier-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.tier-bronze {
    border-color: #cd7f32;
    background: linear-gradient(135deg, #fff5ee 0%, #ffeedd 100%);
}

.tier-silver {
    border-color: #c0c0c0;
    background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
}

.tier-gold {
    border-color: #ffd700;
    background: linear-gradient(135deg, #fffacd 0%, #ffeaa7 100%);
}

.tier-platinum {
    border-color: #e5e4e2;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.tier-badge {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 16px;
}

.tier-requirements {
    font-size: 1rem;
    color: var(--color-text-light);
    margin-bottom: 20px;
}

.tier-discount {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: 24px;
}

.tier-benefits-list {
    text-align: left;
}

.tier-benefits-list h4 {
    font-size: 1rem;
    margin-bottom: 12px;
    color: var(--color-text);
}

.tier-benefits-list ul {
    list-style: none;
    padding: 0;
}

.tier-benefits-list li {
    padding: 8px 0;
    padding-left: 24px;
    position: relative;
}

.tier-benefits-list li:before {
    content: '✓';
    position: absolute;
    left: 0;
    color: var(--color-primary);
    font-weight: 700;
}

/* Benefits List */
.benefits-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-top: 30px;
}

.benefit-item {
    display: flex;
    gap: 20px;
    align-items: flex-start;
    padding: 24px;
    background: var(--color-bg-gray);
    border-radius: 12px;
}

.benefit-icon {
    font-size: 2.5rem;
    flex-shrink: 0;
}

.benefit-content h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 8px;
}

.benefit-content p {
    color: var(--color-text-light);
    margin: 0;
}

/* Expiry Info */
.expiry-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    margin-top: 30px;
}

.info-block {
    padding: 24px;
    background: var(--color-bg-gray);
    border-radius: 12px;
    border-left: 4px solid var(--color-primary);
}

.info-block h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 12px;
}

.info-block p {
    font-size: 0.95rem;
    color: var(--color-text-light);
    margin-bottom: 12px;
}

.info-block p strong {
    color: var(--color-primary);
    font-weight: 600;
}

/* CTA Section */
.rules-cta {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    color: white;
    border-radius: 16px;
    padding: 60px 40px;
    text-align: center;
    margin: 40px 0;
}

.cta-content h2 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 16px;
}

.cta-content p {
    font-size: 1.125rem;
    opacity: 0.95;
    margin-bottom: 32px;
}

.cta-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
}

.cta-buttons .btn-outline {
    background: transparent;
    border: 2px solid white;
    color: white;
}

.cta-buttons .btn-outline:hover {
    background: white;
    color: var(--color-primary);
}

/* Back Link */
.back-link {
    text-align: center;
    padding: 30px 0;
}

.back-link a {
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
}

.back-link a:hover {
    text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
    .rules-hero {
        padding: 40px 20px;
    }
    
    .page-title {
        font-size: 2rem;
    }
    
    .rules-navigation {
        flex-direction: column;
        gap: 8px;
    }
    
    .rules-section {
        padding: 24px 20px;
    }
    
    .section-title {
        font-size: 1.5rem;
    }
    
    .earning-grid {
        grid-template-columns: 1fr;
    }
    
    .tiers-grid {
        grid-template-columns: 1fr;
    }
    
    .benefit-item {
        flex-direction: column;
        text-align: center;
    }
    
    .expiry-info {
        grid-template-columns: 1fr;
    }
    
    .rules-cta {
        padding: 40px 20px;
    }
    
    .cta-buttons {
        flex-direction: column;
    }
    
    .cta-buttons .btn {
        width: 100%;
    }
}
```

**URL routing:**

**Файл:** `apps/loyalty/urls.py`

```python
from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('rules/', views.LoyaltyRulesView.as_view(), name='rules'),
    # ... інші URL
]
```

**View:**

**Файл:** `apps/loyalty/views.py`

```python
from django.views.generic import TemplateView
from .models import LoyaltyTier

class LoyaltyRulesView(TemplateView):
    template_name = 'loyalty/rules.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loyalty_tiers'] = LoyaltyTier.objects.filter(
            is_active=True
        ).order_by('points_required')
        return context
```

### 6.6 Історія оплат - перевірити таблицю

**Файл:** `templates/account/tabs/payments.html`

**Структура вже правильна (рядки 44-116)!** Просто перевірити що все працює.

---

## 🧪 PHASE 7: ТЕСТУВАННЯ & ОПТИМІЗАЦІЯ (2-3 год)

### 7.1 Checklist тестування

#### Backend Testing

```bash
# 1. Перевірити міграції
python3 manage.py showmigrations
python3 manage.py migrate --check

# 2. Запустити тести
python3 manage.py test apps.content
python3 manage.py test apps.events
python3 manage.py test apps.accounts

# 3. Перевірити admin
python3 manage.py check --deploy
```

#### Frontend Testing

**Файл:** `test_checklist.md`

```markdown
## Тестування Frontend

### Глобальні компоненти
- [ ] Іконка кошика відображається правильно
- [ ] Scroll popup з'являється при скролі
- [ ] Popup закривається при кліку на overlay
- [ ] Форма реєстрації в popup працює

### Головна сторінка
- [ ] Hero карусель працює (7 слайдів)
- [ ] Автоматична прокрутка працює
- [ ] 6 курсів відображаються в каруселі
- [ ] Навігація курсів (prev/next) працює
- [ ] Секція ментор-коучинг відображається
- [ ] Шестикутники позиціонуються правильно
- [ ] Секція "Команда професіоналів" оновлена
- [ ] Секція цінностей видалена

### Хаб знань
- [ ] Банер підписки має кнопку закриття
- [ ] Банер закривається та не з'являється знову
- [ ] Секція "Найближчі події" видалена
- [ ] "Цитата місяця" відображається правильно
- [ ] Заголовок "Освітні продукти" відображається
- [ ] Featured продукти виділені візуально
- [ ] Фільтри "Складність/Ціна/Тривалість" видалені
- [ ] Новий фільтр "Тренерство" з під-фільтрами працює
- [ ] Фільтри "Аналітика" та "Менеджмент" працюють
- [ ] Скрол фільтрів працює

### Івенти
- [ ] Календар показує 1 подію на день
- [ ] Фільтр "Ціна" видалений
- [ ] Навігація календаря працює

### Кабінет
- [ ] Інтереси відображаються у правильній послідовності (1-8)
- [ ] Кнопка "ЗБЕРЕГТИ" (не "Зберти")
- [ ] Завантаження фото працює
- [ ] Валідація фото (розмір, тип) працює
- [ ] Програма лояльності відображається
- [ ] Кнопка "Правила ПЛ" веде на правильну сторінку
- [ ] Історія оплат відображається табличкою

### Сторінка "Правила ПЛ"
- [ ] Всі секції відображаються
- [ ] Навігація по секціях працює
- [ ] Картки earning відображаються
- [ ] Рівні лояльності відображаються
- [ ] CTA кнопки працюють
- [ ] Повернення до кабінету працює
```

#### Mobile Testing (iOS Safari)

```markdown
## iOS Safari Testing

### Загальні
- [ ] Viewport налаштований правильно
- [ ] Скрол працює плавно
- [ ] Touch events працюють
- [ ] Жести (swipe) працюють

### Специфічні для iOS
- [ ] 100vh не обрізає контент
- [ ] Sticky елементи працюють
- [ ] Input не масштабує сторінку
- [ ] Date picker працює нативно
- [ ] File input (фото) працює

### Адаптивність
- [ ] iPhone SE (375px)
- [ ] iPhone 12/13 (390px)
- [ ] iPhone 12/13 Pro Max (428px)
- [ ] iPad (768px)
- [ ] iPad Pro (1024px)
```

### 7.2 Оптимізація Performance

**Файл:** `apps/content/views.py`

**Додати кешування для MonthlyQuote:**

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 60 * 24), name='dispatch')  # 24 години
class CourseListView(ListView):
    # ... existing code ...
    pass
```

**Додати select_related та prefetch_related:**

```python
def get_queryset(self):
    queryset = Course.objects.filter(
        is_published=True
    ).select_related(
        'category'
    ).prefetch_related(
        'tags',
        'instructor'
    )
    # ... rest of code
```

### 7.3 CSS оптимізація

**Перевірити дублювання:**

```bash
# Знайти дублікати в CSS
grep -r "\.btn-primary" static/css/

# Перевірити !important
grep -r "!important" static/css/

# Перевірити inline styles
grep -r "style=" templates/
```

**Консолідувати повторювані стилі в base.css:**

```css
/* Базові кнопки (без дублювання) */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s ease;
    cursor: pointer;
    border: 2px solid transparent;
}

.btn-primary {
    background: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
}

.btn-primary:hover {
    background: var(--color-primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}

.btn-outline {
    background: transparent;
    border-color: var(--color-primary);
    color: var(--color-primary);
}

.btn-outline:hover {
    background: var(--color-primary);
    color: white;
}

.btn-large {
    padding: 16px 32px;
    font-size: 1.125rem;
}

.btn-small {
    padding: 8px 16px;
    font-size: 0.875rem;
}

.btn-block {
    width: 100%;
}
```

### 7.4 JavaScript оптимізація

**Використовувати debounce для скролу:**

```javascript
// Utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Використання
const handleScroll = debounce(() => {
    checkScroll();
}, 200);

window.addEventListener('scroll', handleScroll);
```

### 7.5 Final Checklist перед запуском

```markdown
## Pre-Launch Checklist

### Code Quality
- [ ] Немає console.log() у production коді
- [ ] Немає закоментованого коду
- [ ] Немає TODO коментарів
- [ ] Всі import використовуються
- [ ] Немає unused змінних

### Security
- [ ] CSRF токени на всіх формах
- [ ] Валідація на backend
- [ ] Sanitization user input
- [ ] Permissions перевірені

### Performance
- [ ] Images оптимізовані
- [ ] CSS minified
- [ ] JS minified
- [ ] Lazy loading для images
- [ ] Caching налаштований

### SEO
- [ ] Meta tags додані
- [ ] Open Graph теги
- [ ] Canonical URLs
- [ ] Sitemap оновлений

### Accessibility
- [ ] Alt tags на images
- [ ] ARIA labels
- [ ] Keyboard navigation
- [ ] Color contrast OK

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (iOS + macOS)
- [ ] Edge (latest)
```

### 7.6 Deploy процес

```bash
#!/bin/bash
# deploy.sh

# 1. Backup
echo "Creating backup..."
python3 manage.py dumpdata > backup_$(date +%Y%m%d).json

# 2. Pull changes
echo "Pulling changes..."
git pull origin feature/screenshot-changes

# 3. Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# 4. Collect static
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# 5. Migrate
echo "Running migrations..."
python3 manage.py migrate

# 6. Restart server
echo "Restarting server..."
sudo systemctl restart gunicorn

echo "✅ Deploy complete!"
```

### 7.7 Rollback план

```bash
#!/bin/bash
# rollback.sh

# 1. Revert git
git reset --hard HEAD~1

# 2. Restore database
python3 manage.py flush --noinput
python3 manage.py loaddata backup_YYYYMMDD.json

# 3. Migrate back
python3 manage.py migrate content zero
python3 manage.py migrate events zero

# 4. Restart
sudo systemctl restart gunicorn
```

---

## 📊 SUMMARY & NEXT STEPS

### Загальний час виконання:
- Phase 0: Підготовка - **1 год**
- Phase 1: Backend & Database - **2-3 год**
- Phase 2: Глобальні компоненти - **1-2 год**
- Phase 3: Головна сторінка - **3-4 год**
- Phase 4: Хаб знань - **2-3 год**
- Phase 5: Івенти - **1 год**
- Phase 6: Кабінет - **2-3 год**
- Phase 7: Тестування - **2-3 год**

**TOTAL: 14-20 годин**

### Критичний шлях:
1. ✅ Backend зміни (міграції, моделі)
2. ✅ Глобальні компоненти (popup, іконки)
3. ✅ Головна сторінка (найбільше змін)
4. ✅ Хаб знань (фільтри, продукти)
5. ✅ Кабінет (інтереси, програма лояльності)
6. ✅ Тестування на всіх пристроях

### Команди для швидкого старту:

```bash
# Clone та setup
git checkout -b feature/screenshot-changes
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Міграції
python3 manage.py makemigrations
python3 manage.py migrate

# Тестовий сервер
python3 manage.py runserver

# Production
./deploy.sh
```

### Наступні кроки після імплементації:

1. **Отримати від клієнта:**
   - Нову іконку кошика (SVG)
   - Описи експертів команди
   - Презентацію програми лояльності
   - Деталі механіки рефок

2. **Додаткові покращення:**
   - A/B тестування popup
   - Аналітика відвідувань
   - Performance моніторинг
   - User feedback форма

3. **Документація:**
   - Оновити README
   - Створити user guide для адміна
   - Документувати API endpoints

---

**СТАТУС:** ✅ План готовий до виконання  
**АВТОР:** Senior Full-Stack Developer  
**ДАТА:** 9 жовтня 2025

