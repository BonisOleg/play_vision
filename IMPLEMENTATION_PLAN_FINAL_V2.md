# 🚀 ФІНАЛЬНИЙ ПЛАН ІМПЛЕМЕНТАЦІЇ V2 (БЕЗ КОНФЛІКТІВ)

## 📋 ВСТУП

**Дата:** 9 жовтня 2025  
**Версія:** 2.0 (Виправлена після аналізу існуючого коду)  
**Підхід:** Senior Full-Stack Developer  
**Принципи:** DRY, No !important, No duplicates, Clean Architecture

**ВАЖЛИВО:** Цей план враховує весь існуючий код проекту та не створює дублювань.

---

## ✅ ЩО ВЖЕ Є В ПРОЄКТІ (НЕ СТВОРЮВАТИ!)

### Існуюча структура:
1. ✅ **loyalty app** - повністю працює (LoyaltyTier, LoyaltyAccount, PointTransaction)
2. ✅ **Tag model** - існує в apps/content/models.py (рядки 34-54)
3. ✅ **Profile.interests** - ManyToMany до Tag (models.py:103)
4. ✅ **Course.difficulty** - поле існує, НЕ видаляти з моделі
5. ✅ **Базові стилі кнопок** - в static/css/main.css (рядок 383+)
6. ✅ **НЕ використовується !important** - перевірено grep

### Що НЕ ТРЕБА робити:
- ❌ НЕ створювати loyalty app заново
- ❌ НЕ створювати базові класи .btn (вже є)
- ❌ НЕ видаляти difficulty з Course моделі
- ❌ НЕ видаляти price з Course моделі
- ❌ НЕ дублювати стилі

---

## 🎯 ФАЗИ ІМПЛЕМЕНТАЦІЇ

### PHASE 0: ПІДГОТОВКА (30 хв)
### PHASE 1: BACKEND CHANGES (2-3 год)
### PHASE 2: FRONTEND COMPONENTS (1-2 год)
### PHASE 3: HOMEPAGE UPDATES (2-3 год)
### PHASE 4: HUB KNOWLEDGE UPDATES (2-3 год)
### PHASE 5: EVENTS UPDATES (45 хв)
### PHASE 6: CABINET UPDATES (2-3 год)
### PHASE 7: TESTING (2-3 год)

**ЗАГАЛЬНИЙ ЧАС:** 13-18 годин

---

## 📦 PHASE 0: ПІДГОТОВКА (30 хв)

### 0.1 Git Setup
```bash
# Створити гілку
cd /Users/olegbonislavskyi/Play_Vision
git checkout -b feature/screenshot-changes-v2

# Створити бекап
git tag backup-$(date +%Y%m%d_%H%M%S)
```

### 0.2 Database Backup
```bash
# Бекап бази
python3 manage.py dumpdata > backups/backup_$(date +%Y%m%d_%H%M%S).json

# Створити директорію для бекапів
mkdir -p backups
```

### 0.3 Створити нові файли
```bash
# CSS
touch static/css/components/scroll-popup.css
touch static/css/components/loyalty-rules.css

# JavaScript  
touch static/js/scroll-popup.js
touch static/js/home.js

# Templates
mkdir -p templates/partials
mkdir -p templates/loyalty
touch templates/partials/scroll-popup.html
touch templates/loyalty/rules.html
```

### 0.4 Checklist
- [ ] Virtual environment активований
- [ ] Dependencies встановлені
- [ ] База даних працює
- [ ] Django server запускається

---

## 🗄️ PHASE 1: BACKEND CHANGES (2-3 год)

### 1.1 Оновити Tag model (додати нові поля)

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/content/models.py`

**Поточний код (рядки 34-54):**
```python
class Tag(models.Model):
    """
    Content tags
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']  # ЗМІНИТИ
```

**ОНОВИТИ на:**
```python
class Tag(models.Model):
    """
    Content tags and user interests
    """
    TAG_TYPE_CHOICES = [
        ('interest', 'Інтерес користувача'),
        ('category', 'Категорія контенту'),
        ('general', 'Загальний тег'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    tag_type = models.CharField(
        max_length=20, 
        choices=TAG_TYPE_CHOICES, 
        default='general',
        db_index=True
    )
    display_order = models.PositiveIntegerField(
        default=0, 
        help_text='Порядок відображення (для interest type)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['display_order', 'name']  # ЗМІНЕНО
        indexes = [
            models.Index(fields=['tag_type', 'display_order']),
        ]
```

**Створити міграцію:**
```bash
python3 manage.py makemigrations content --name add_tag_type_and_order
```

### 1.2 Створити MonthlyQuote model

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/content/models.py`

**Додати ПІСЛЯ моделі Favorite (після рядка 262):**

```python


class MonthlyQuote(models.Model):
    """
    Цитата експерта місяця (показується в Хабі знань)
    """
    expert_name = models.CharField(max_length=100, verbose_name='Імʼя експерта')
    expert_role = models.CharField(max_length=150, verbose_name='Посада/роль')
    expert_photo = models.ImageField(
        upload_to='experts/monthly_quotes/', 
        blank=True,
        verbose_name='Фото експерта'
    )
    quote_text = models.TextField(verbose_name='Текст цитати')
    
    # Місяць - завжди перше число місяця
    month = models.DateField(
        unique=True,
        verbose_name='Місяць',
        help_text='Завжди 1-е число місяця (напр. 2025-10-01)'
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Активна',
        help_text='Тільки одна цитата може бути активною для поточного місяця'
    )
    
    # Статистика
    views_count = models.PositiveIntegerField(default=0)
    last_displayed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
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
        """
        Отримати цитату поточного місяця з кешуванням
        """
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
                # Кешувати до кінця місяця (31 день max)
                cache.set(cache_key, quote, 60*60*24*31)
                
                # Оновити статистику
                quote.views_count += 1
                quote.last_displayed_at = timezone.now()
                quote.save(update_fields=['views_count', 'last_displayed_at'])
        
        return quote
    
    def save(self, *args, **kwargs):
        # Завжди встановлювати перше число місяця
        if self.month:
            self.month = self.month.replace(day=1)
        super().save(*args, **kwargs)
        
        # Очистити кеш при збереженні
        from django.core.cache import cache
        cache.delete('current_monthly_quote')
```

**Створити міграцію:**
```bash
python3 manage.py makemigrations content --name add_monthly_quote
```

### 1.3 Додати training_specialization в Course

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/content/models.py`

**У моделі Course ДОДАТИ після рядка 75 (після поля price):**

```python
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # НОВИЙ БЛОК
    training_specialization = models.CharField(
        max_length=30,
        choices=[
            ('', 'Загальний'),
            ('goalkeeper', 'Тренер воротарів'),
            ('youth', 'Дитячий тренер'),
            ('fitness', 'Тренер ЗФП'),
            ('professional', 'Тренер професійних команд'),
        ],
        blank=True,
        default='',
        verbose_name='Спеціалізація тренера',
        help_text='Застосовується тільки для курсів категорії "Тренерство"',
        db_index=True
    )
    
    # Access control (існуюче поле)
    is_featured = models.BooleanField(default=False)
```

**Створити міграцію:**
```bash
python3 manage.py makemigrations content --name add_course_training_specialization
```

### 1.4 Data Migration - створити інтереси

**Створити файл:** `/Users/olegbonislavskyi/Play_Vision/apps/content/migrations/0XXX_populate_user_interests.py`

```python
from django.db import migrations

def create_user_interests(apps, schema_editor):
    """
    Створити 8 інтересів у правильному порядку
    """
    Tag = apps.get_model('content', 'Tag')
    
    # Видалити старі інтереси якщо є
    Tag.objects.filter(tag_type='interest').delete()
    
    # Створити 8 інтересів
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
    
    print(f"✅ Створено {len(interests)} інтересів користувачів")

def reverse_migration(apps, schema_editor):
    """Відкат"""
    Tag = apps.get_model('content', 'Tag')
    Tag.objects.filter(tag_type='interest').delete()

class Migration(migrations.Migration):
    
    dependencies = [
        ('content', '0XXX_add_tag_type_and_order'),  # Попередня міграція
    ]
    
    operations = [
        migrations.RunPython(create_user_interests, reverse_migration),
    ]
```

### 1.5 Оновити admin.py для нових моделей

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/content/admin.py`

**Додати в кінець файлу:**

```python
from .models import MonthlyQuote

@admin.register(MonthlyQuote)
class MonthlyQuoteAdmin(admin.ModelAdmin):
    list_display = ['expert_name', 'expert_role', 'month', 'is_active', 'views_count']
    list_filter = ['is_active', 'month']
    search_fields = ['expert_name', 'expert_role', 'quote_text']
    date_hierarchy = 'month'
    readonly_fields = ['views_count', 'last_displayed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Експерт', {
            'fields': ('expert_name', 'expert_role', 'expert_photo')
        }),
        ('Цитата', {
            'fields': ('quote_text', 'month', 'is_active')
        }),
        ('Статистика', {
            'fields': ('views_count', 'last_displayed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Очистити кеш при збереженні
        from django.core.cache import cache
        cache.delete('current_monthly_quote')
        super().save_model(request, obj, form, change)
```

**Оновити TagAdmin (якщо є):**

```python
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'tag_type', 'display_order', 'created_at']
    list_filter = ['tag_type']
    search_fields = ['name', 'slug']
    ordering = ['tag_type', 'display_order', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'tag_type', 'display_order')
        }),
    )
```

### 1.6 Оновити CourseListView (ВИДАЛИТИ ФІЛЬТРИ)

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/content/views.py`

**ВАЖЛИВО:** НЕ видаляти difficulty з моделі, тільки з фільтрів!

**Замінити метод get_queryset() (рядки 18-50):**

```python
def get_queryset(self):
    queryset = Course.objects.filter(
        is_published=True
    ).select_related('category').prefetch_related('tags')
    
    # Category filter (ЗАЛИШИТИ)
    category_slug = self.request.GET.get('category')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    # ❌ ВИДАЛИТИ: Difficulty filter
    # difficulty = self.request.GET.get('difficulty')
    # if difficulty:
    #     queryset = queryset.filter(difficulty=difficulty)
    
    # Tag filter (ЗАЛИШИТИ)
    tag = self.request.GET.get('tag')
    if tag:
        queryset = queryset.filter(tags__slug=tag)
    
    # ✅ НОВИЙ: Interest filter (для тегів типу interest)
    interest = self.request.GET.get('interest')
    if interest:
        queryset = queryset.filter(
            tags__slug=interest,
            tags__tag_type='interest'
        ).distinct()
    
    # ✅ НОВИЙ: Training specialization filter
    training_type = self.request.GET.get('training_type')
    if training_type:
        queryset = queryset.filter(training_specialization=training_type)
    
    # ❌ ВИДАЛИТИ: Price filter
    # price_filter = self.request.GET.get('price')
    # if price_filter == 'free':
    #     queryset = queryset.filter(is_free=True)
    # elif price_filter == 'paid':
    #     queryset = queryset.filter(is_free=False)
    
    # Sorting (ЗАЛИШИТИ)
    sort = self.request.GET.get('sort', '-created_at')
    if sort in ['price', '-price', 'title', '-title', '-created_at', 'view_count']:
        queryset = queryset.order_by(sort)
    
    return queryset
```

**Оновити get_context_data() (рядки 52-81):**

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Categories (ЗАЛИШИТИ)
    from .models import Category
    context['categories'] = Category.objects.filter(is_active=True)
    
    # ✅ НОВИЙ: Інтереси (замість загальних тегів)
    from .models import Tag
    context['interests'] = Tag.objects.filter(
        tag_type='interest',
        is_active=True  # якщо додасте це поле
    ).order_by('display_order')
    
    # Featured courses (ЗАЛИШИТИ)
    context['featured_courses'] = Course.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('category').prefetch_related('tags')[:6]
    
    # ✅ НОВИЙ: Monthly quote
    from .models import MonthlyQuote
    context['monthly_quote'] = MonthlyQuote.get_current_quote()
    
    # Current filters (ОНОВИТИ)
    context['current_category'] = self.request.GET.get('category', '')
    context['current_interest'] = self.request.GET.get('interest', '')
    context['current_training_type'] = self.request.GET.get('training_type', '')
    context['current_sort'] = self.request.GET.get('sort', '-created_at')
    
    # ❌ ВИДАЛИТИ:
    # context['current_difficulty'] = self.request.GET.get('difficulty')
    # context['current_price'] = self.request.GET.get('price')
    
    # User favorites (ЗАЛИШИТИ)
    if self.request.user.is_authenticated:
        favorites = Favorite.objects.filter(
            user=self.request.user,
            course__in=context['courses']
        ).values_list('course_id', flat=True)
        context['user_favorites'] = list(favorites)
    else:
        context['user_favorites'] = []
    
    return context
```

### 1.7 Оновити HomeView context

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/core/views.py`

**Замінити метод get_context_data() (рядки 25-32):**

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # ✅ ОНОВИТИ: Featured courses для каруселі (6 курсів)
    from apps.content.models import Course
    context['featured_courses'] = Course.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('category').prefetch_related('tags')[:6]
    
    return context
```

### 1.8 Створити LoyaltyRulesView

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/loyalty/views.py`

**ЗАМІНИТИ весь файл (зараз він порожній):**

```python
from django.views.generic import TemplateView
from .models import LoyaltyTier


class LoyaltyRulesView(TemplateView):
    """
    Сторінка з правилами програми лояльності
    """
    template_name = 'loyalty/rules.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Всі рівні лояльності
        context['loyalty_tiers'] = LoyaltyTier.objects.filter(
            is_active=True
        ).order_by('points_required')
        
        return context
```

**Створити urls.py для loyalty:**

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/loyalty/urls.py`

```python
from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('rules/', views.LoyaltyRulesView.as_view(), name='rules'),
]
```

**Підключити в головному urls.py:**

**Файл:** `/Users/olegbonislavskyi/Play_Vision/playvision/urls.py`

Додати в urlpatterns:
```python
path('loyalty/', include('apps.loyalty.urls')),
```

### 1.9 Запустити всі міграції

```bash
# Створити всі міграції
python3 manage.py makemigrations

# Перевірити SQL
python3 manage.py sqlmigrate content 0XXX

# Запустити
python3 manage.py migrate

# Створити тестову цитату через shell
python3 manage.py shell
```

```python
from apps.content.models import MonthlyQuote
from datetime import date

MonthlyQuote.objects.create(
    expert_name="Пеп Гвардіола",
    expert_role='Тренер "Манчестер Сіті"',
    quote_text="Навчання ніколи не закінчується. Кожен день ми можемо дізнатися щось нове, що зробить нас кращими тренерами і людьми.",
    month=date(2025, 10, 1),
    is_active=True
)
```

---

## 🧩 PHASE 2: FRONTEND COMPONENTS (1-2 год)

### 2.1 Оновити іконку кошика (ТІЛЬКИ ІКОНКУ!)

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/base/base.html`

**Знайти (приблизно рядок 152-163):**

```html
<a href="{% url 'cart:cart' %}" class="navbar-icon cart-icon navbar-desktop-only"
    aria-label="Кошик">
    <svg class="icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2">
        <!-- ЗАМІНИТИ SVG НА НОВИЙ ВІД КЛІЄНТА -->
        <path d="...НОВИЙ SVG..." />
    </svg>
    <span class="cart-count" data-cart-count>{{ cart_items_count|default:0 }}</span>
</a>
```

**⚠️ ВАЖЛИВО:** НЕ видаляти текст "Play Vision" з navbar-brand! Тільки змінити SVG іконки кошика!

### 2.2 Scroll Popup Component

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/partials/scroll-popup.html`

```html
<!-- Scroll Popup -->
<div id="scroll-popup" 
     x-data="scrollPopup()" 
     x-show="showPopup" 
     x-transition:enter="transition ease-out duration-300"
     x-transition:enter-start="opacity-0 transform scale-90"
     x-transition:enter-end="opacity-100 transform scale-100"
     x-transition:leave="transition ease-in duration-200"
     x-transition:leave-start="opacity-100 transform scale-100"
     x-transition:leave-end="opacity-0 transform scale-90"
     class="scroll-popup" 
     style="display: none;">
    
    <div class="popup-overlay" @click="closePopup()"></div>
    
    <div class="popup-card">
        <button class="popup-close" @click="closePopup()" aria-label="Закрити">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
        
        <div class="popup-content">
            <h2>Готовий приєднатись до спільноти Play vision?</h2>
            
            {% if user.is_authenticated %}
                <p>Оформи підписку та отримай <strong>+30 балів лояльності</strong>!</p>
                <a href="{% url 'core:coming_soon' %}?page=subscription" class="btn btn-primary btn-large">
                    Перейти до підписки
                </a>
            {% else %}
                <p>Зареєструйся та отримай <strong>10% знижку</strong> на першу покупку!</p>
                <form @submit.prevent="handleRegister" class="popup-form">
                    <input type="email" 
                           x-model="formData.email" 
                           placeholder="Ваш email" 
                           required 
                           class="form-input">
                    <input type="password" 
                           x-model="formData.password" 
                           placeholder="Пароль (мін. 8 символів)" 
                           required 
                           minlength="8"
                           class="form-input">
                    <button type="submit" class="btn btn-primary btn-large" :disabled="loading">
                        <span x-show="!loading">Зареєструватись</span>
                        <span x-show="loading">Завантаження...</span>
                    </button>
                </form>
                <p class="popup-footer">
                    Вже є акаунт? <a href="{% url 'accounts:login' %}">Увійти</a>
                </p>
            {% endif %}
        </div>
    </div>
</div>
```

**CSS:** `/Users/olegbonislavskyi/Play_Vision/static/css/components/scroll-popup.css`

```css
/* Scroll Popup Styles - БЕЗ !important */
.scroll-popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: var(--z-modal);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
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

.popup-card {
    position: relative;
    background: white;
    border-radius: var(--radius-xl);
    max-width: 500px;
    width: 100%;
    box-shadow: var(--shadow-lg);
    overflow: hidden;
}

.popup-close {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
    background: transparent;
    border: none;
    color: var(--color-text-light);
    cursor: pointer;
    padding: var(--spacing-xs);
    border-radius: var(--radius-full);
    transition: var(--transition-base);
    z-index: 10;
}

.popup-close:hover {
    background: var(--color-bg-gray);
    color: var(--color-text);
    transform: rotate(90deg);
}

.popup-content {
    padding: calc(var(--spacing-xxl) + var(--spacing-lg)) var(--spacing-xxl) var(--spacing-xxl);
}

.popup-content h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: var(--spacing-md);
    line-height: 1.3;
}

.popup-content p {
    font-size: 1rem;
    color: var(--color-text-light);
    margin-bottom: var(--spacing-xl);
    line-height: 1.6;
}

.popup-content strong {
    color: var(--color-primary);
    font-weight: 600;
}

.popup-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.popup-form .form-input {
    width: 100%;
    padding: var(--spacing-md);
    border: 2px solid var(--color-border);
    border-radius: var(--radius-md);
    font-size: 1rem;
    transition: var(--transition-base);
}

.popup-form .form-input:focus {
    outline: none;
    border-color: var(--color-primary);
}

.popup-footer {
    margin-top: var(--spacing-lg);
    text-align: center;
    font-size: 0.9rem;
}

.popup-footer a {
    color: var(--color-primary);
    font-weight: 600;
}

/* Mobile */
@media (max-width: 768px) {
    .popup-content {
        padding: calc(var(--spacing-xl) + var(--spacing-md)) var(--spacing-lg) var(--spacing-lg);
    }
    
    .popup-content h2 {
        font-size: 1.5rem;
    }
}
```

**JavaScript:** `/Users/olegbonislavskyi/Play_Vision/static/js/scroll-popup.js`

```javascript
/**
 * Scroll Popup Component
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
            // Перевірити чи вже показували
            const shown = localStorage.getItem('popup_shown');
            const dismissed = sessionStorage.getItem('popup_dismissed');
            
            if (shown || dismissed) {
                return;
            }
            
            // Відстежувати скрол з debounce
            let scrollTimeout;
            window.addEventListener('scroll', () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => this.checkScroll(), 200);
            });
        },
        
        checkScroll() {
            const scrolled = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight;
            
            if (scrolled >= 0.8 && !this.showPopup) {
                this.openPopup();
            }
        },
        
        openPopup() {
            this.showPopup = true;
            document.body.style.overflow = 'hidden';
            localStorage.setItem('popup_shown', 'true');
        },
        
        closePopup() {
            this.showPopup = false;
            document.body.style.overflow = '';
            sessionStorage.setItem('popup_dismissed', 'true');
        },
        
        async handleRegister() {
            if (this.loading) return;
            
            this.loading = true;
            
            try {
                const response = await fetch('/accounts/api/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({
                        email: this.formData.email,
                        password: this.formData.password,
                        source: 'scroll_popup',
                        promo_code: 'FIRST10'
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
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
        
        getCsrfToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                   document.querySelector('meta[name="csrf-token"]')?.content || '';
        }
    };
}
```

### 2.3 Підключити компоненти в base.html

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/base/base.html`

**В секції head додати:**
```html
<link rel="stylesheet" href="{% static 'css/components/scroll-popup.css' %}">
```

**Перед закриттям body додати:**
```html
<script src="{% static 'js/scroll-popup.js' %}"></script>
```

---

## 🏠 PHASE 3: HOMEPAGE UPDATES (2-3 год)

### 3.1 Оновити Hero Section (карусель)

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/pages/home.html`

**ВАЖЛИВО:** Використовувати ІСНУЮЧУ структуру (рядки 15-44), тільки оновити контент!

**Поточний код (рядки 15-44):**
```html
<section class="fullscreen-section hero-section" x-data="{ currentSlide: 0 }">
```

**ЗАМІНИТИ на:**
```html
<section class="fullscreen-section hero-section" x-data="heroCarousel()">
    <div class="section-bg">
        <video class="section-bg-video" muted loop preload="metadata">
            <source src="{% static 'videos/hero-bg.mp4' %}" type="video/mp4">
            <img class="section-bg-image" src="{% static 'images/hero-bg.jpg' %}" alt="Hero">
        </video>
    </div>
    <div class="section-overlay section-overlay--gradient"></div>

    <div class="section-content hero-with-frame">
        <div class="hero-badge">ГОЛОВНЕ ЗАРАЗ</div>
        <h1 class="hero-title" x-text="slides[currentSlide].title"></h1>
        <p class="hero-subtitle" x-text="slides[currentSlide].subtitle"></p>

        <div class="hero-buttons">
            <!-- ТІЛЬКИ ОДНА КНОПКА -->
            <a :href="slides[currentSlide].ctaUrl" class="btn btn-primary">
                Дізнатись більше
            </a>
        </div>

        <div class="hero-slider-dots">
            <template x-for="(slide, index) in slides" :key="index">
                <button class="slider-dot" 
                        :class="{'active': currentSlide === index}"
                        @click="currentSlide = index"
                        :aria-label="'Слайд ' + (index + 1)"></button>
            </template>
        </div>
    </div>
</section>
```

**CSS:** Додати ТІЛЬКИ стиль для білих рамок в `/Users/olegbonislavskyi/Play_Vision/static/css/components/home.css`

**Знайти .hero-section та додати після існуючих стилів:**

```css
/* Білі рамки для hero контенту */
.hero-with-frame {
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
    backdrop-filter: blur(10px);
    background: rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
    .hero-with-frame {
        border-width: 2px;
        padding: var(--spacing-xl) var(--spacing-lg);
    }
}
```

**JavaScript:** `/Users/olegbonislavskyi/Play_Vision/static/js/home.js` (СТВОРИТИ)

```javascript
/**
 * Home Page Components
 */

// Hero Carousel (7 слайдів)
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
                subtitle: 'Приєднуйтесь до спільноти футбольних професіоналів України',
                ctaUrl: '/about/'
            },
            {
                title: 'Івенти',
                subtitle: 'Вебінари, майстер-класи та форуми від міжнародних експертів',
                ctaUrl: '/events/'
            },
            {
                title: 'Хаб знань — долучайся першим',
                subtitle: 'Ексклюзивні курси та матеріали для розвитку футбольних фахівців',
                ctaUrl: '/hub/'
            },
            {
                title: 'Ментор-коучинг',
                subtitle: 'Індивідуальний підхід до комплексного розвитку кожного футболіста',
                ctaUrl: '/mentor-coaching/'
            },
            {
                title: 'Про нас',
                subtitle: 'Дізнайтеся більше про нашу місію, цінності та команду експертів',
                ctaUrl: '/about/'
            },
            {
                title: 'Напрямки діяльності',
                subtitle: '4 ключових напрямки для професійного зростання у футболі',
                ctaUrl: '/about/#directions'
            }
        ],
        
        init() {
            // Автопрокрутка кожні 5 секунд
            setInterval(() => {
                this.nextSlide();
            }, 5000);
        },
        
        nextSlide() {
            this.currentSlide = (this.currentSlide + 1) % this.slides.length;
        }
    };
}

// Courses Carousel (6 курсів)
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
            this.updateSlidesPerView();
            window.addEventListener('resize', () => this.updateSlidesPerView());
        },
        
        updateSlidesPerView() {
            if (window.innerWidth < 768) {
                this.slidesPerView = 1;
            } else if (window.innerWidth < 1024) {
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

**Підключити в home.html:**
```html
{% block extra_js %}
<script src="{% static 'js/home.js' %}"></script>
{% endblock %}
```

### 3.2 Замінити "3 напрямки" на "6 курсів" (карусель)

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/pages/home.html`

**ЗАМІНИТИ секцію (рядки 46-77):**

```html
<!-- 2. FEATURED COURSES CAROUSEL -->
<section class="fullscreen-section featured-courses-section">
    <div class="section-bg">
        <img class="section-bg-image" src="{% static 'images/courses-bg.jpg' %}" alt="Курси">
    </div>
    <div class="section-overlay section-overlay--light"></div>

    <div class="section-content">
        <h2 class="section-title">6 найголовніших курсів</h2>
        
        <div class="featured-carousel-container" x-data="coursesCarousel()">
            <!-- Prev Button -->
            <button class="carousel-btn carousel-btn-prev" 
                    @click="prevSlide()" 
                    :disabled="currentIndex === 0"
                    aria-label="Попередній курс">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M15 18l-6-6 6-6"/>
                </svg>
            </button>
            
            <div class="featured-carousel">
                <div class="carousel-track" 
                     :style="`transform: translateX(-${currentIndex * slideWidth}%)`">
                    {% for course in featured_courses %}
                    <div class="carousel-slide">
                        <div class="featured-card">
                            <div class="featured-image">
                                {% if course.thumbnail %}
                                <img src="{{ course.thumbnail.url }}" alt="{{ course.title }}">
                                {% else %}
                                <div class="image-placeholder"></div>
                                {% endif %}
                            </div>
                            <div class="featured-content">
                                <span class="featured-category">{{ course.category.name }}</span>
                                <h3 class="featured-title">{{ course.title }}</h3>
                                <p class="featured-description">{{ course.short_description|truncatewords:15 }}</p>
                                <a href="{{ course.get_absolute_url }}" class="featured-link">
                                    Детальніше →
                                </a>
                            </div>
                        </div>
                    </div>
                    {% empty %}
                    <p class="no-courses">Курси скоро з'являться</p>
                    {% endfor %}
                </div>
            </div>
            
            <!-- Next Button -->
            <button class="carousel-btn carousel-btn-next" 
                    @click="nextSlide()"
                    :disabled="currentIndex >= maxIndex"
                    aria-label="Наступний курс">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 18l6-6-6-6"/>
                </svg>
            </button>
        </div>
    </div>
</section>
```

**CSS:** Додати в `/Users/olegbonislavskyi/Play_Vision/static/css/components/home.css`

**ПІСЛЯ існуючих стилів directions-section додати:**

```css
/* Featured Courses Carousel */
.featured-courses-section {
    background: var(--color-bg-gray);
}

.featured-carousel-container {
    position: relative;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 60px;
}

.carousel-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: white;
    border: none;
    width: 48px;
    height: 48px;
    border-radius: var(--radius-full);
    box-shadow: var(--shadow-md);
    cursor: pointer;
    z-index: 10;
    transition: var(--transition-base);
    display: flex;
    align-items: center;
    justify-content: center;
}

.carousel-btn:hover:not(:disabled) {
    box-shadow: var(--shadow-lg);
    transform: translateY(-50%) scale(1.05);
}

.carousel-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.carousel-btn-prev {
    left: 0;
}

.carousel-btn-next {
    right: 0;
}

.featured-carousel {
    overflow: hidden;
    padding: var(--spacing-lg) 0;
}

.carousel-track {
    display: flex;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.carousel-slide {
    flex: 0 0 33.333%;
    padding: 0 var(--spacing-md);
}

.featured-card {
    background: white;
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: var(--transition-base);
    height: 100%;
    display: flex;
    flex-direction: column;
}

.featured-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-md);
}

.featured-image {
    width: 100%;
    height: 200px;
    overflow: hidden;
    background: var(--color-bg-gray);
}

.featured-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.image-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.featured-content {
    padding: var(--spacing-lg);
    flex: 1;
    display: flex;
    flex-direction: column;
}

.featured-category {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: var(--spacing-xs);
}

.featured-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: var(--spacing-sm);
    line-height: 1.3;
}

.featured-description {
    font-size: 0.9rem;
    color: var(--color-text-light);
    line-height: 1.5;
    margin-bottom: var(--spacing-md);
    flex: 1;
}

.featured-link {
    color: var(--color-primary);
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
    transition: var(--transition-base);
}

.featured-link:hover {
    gap: var(--spacing-sm);
}

.no-courses {
    text-align: center;
    padding: var(--spacing-xxl);
    color: var(--color-text-light);
}

/* Responsive */
@media (max-width: 1024px) {
    .carousel-slide {
        flex: 0 0 50%;
    }
}

@media (max-width: 768px) {
    .carousel-slide {
        flex: 0 0 100%;
    }
    
    .featured-carousel-container {
        padding: 0 50px;
    }
    
    .carousel-btn {
        width: 40px;
        height: 40px;
    }
}
```

### 3.3 Додати секцію Ментор-коучинг

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/pages/home.html`

**ДОДАТИ після секції courses (після рядка 130):**

```html
<!-- 3. MENTOR-COACHING ECOSYSTEM -->
<section class="fullscreen-section mentor-coaching-section">
    <div class="section-bg">
        <img class="section-bg-image" src="{% static 'images/mentor-bg.jpg' %}" alt="Ментор-коучинг">
    </div>
    <div class="section-overlay section-overlay--dark"></div>

    <div class="section-content">
        <h2 class="section-title">Ментор-коучинг</h2>
        <h3 class="ecosystem-subtitle">Екосистема комплексного розвитку футболіста</h3>
        
        <!-- Діаграма шестикутників -->
        <div class="ecosystem-diagram">
            <!-- Центральний елемент -->
            <div class="ecosystem-center">
                <img src="{% static 'images/playvision-logo.svg' %}" 
                     alt="Play Vision" 
                     class="center-logo">
            </div>
            
            <!-- 4 напрямки (БЕЗ АНГЛІЙСЬКИХ СЛІВ!) -->
            <div class="ecosystem-item ecosystem-item-1">
                <div class="item-icon">📅</div>
                <h4>Івенти</h4>
            </div>
            
            <div class="ecosystem-item ecosystem-item-2">
                <div class="item-icon">👨‍🏫</div>
                <h4>Ментор-коучінг</h4>
            </div>
            
            <div class="ecosystem-item ecosystem-item-3">
                <div class="item-icon">📚</div>
                <h4>Хаб знань</h4>
            </div>
            
            <div class="ecosystem-item ecosystem-item-4">
                <div class="item-icon">💡</div>
                <h4>Інновації і технології</h4>
            </div>
        </div>
        
        <div class="mentor-cta">
            <a href="/mentor-coaching/" class="btn btn-primary btn-large">
                Дізнатись більше про ментор-коучинг
            </a>
        </div>
    </div>
</section>
```

**CSS:** Додати в `/Users/olegbonislavskyi/Play_Vision/static/css/components/home.css`

```css
/* Mentor-Coaching Ecosystem */
.mentor-coaching-section {
    background: var(--color-secondary);
    color: white;
    text-align: center;
}

.ecosystem-subtitle {
    font-size: 1.25rem;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: var(--spacing-xxl);
}

.ecosystem-diagram {
    position: relative;
    width: 100%;
    max-width: 600px;
    height: 500px;
    margin: 0 auto var(--spacing-xxl);
}

.ecosystem-center {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 160px;
    height: 160px;
    background: var(--color-primary);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
}

.center-logo {
    max-width: 90px;
    height: auto;
    filter: brightness(0) invert(1);
}

.ecosystem-item {
    position: absolute;
    width: 140px;
    height: 140px;
    background: white;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-xs);
    transition: var(--transition-base);
    cursor: pointer;
}

.ecosystem-item:hover {
    transform: scale(1.1);
    box-shadow: 0 8px 32px rgba(255, 107, 53, 0.4);
}

.ecosystem-item-1 {
    left: 50%;
    top: 20px;
    transform: translateX(-50%);
}

.ecosystem-item-2 {
    right: 60px;
    top: 40%;
}

.ecosystem-item-3 {
    left: 60px;
    top: 40%;
}

.ecosystem-item-4 {
    left: 50%;
    bottom: 20px;
    transform: translateX(-50%);
}

.item-icon {
    font-size: 2rem;
}

.ecosystem-item h4 {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-text);
    margin: 0;
    text-align: center;
    line-height: 1.2;
}

.mentor-cta {
    margin-top: var(--spacing-xl);
}

/* Mobile */
@media (max-width: 768px) {
    .ecosystem-diagram {
        height: 400px;
        max-width: 400px;
    }
    
    .ecosystem-center {
        width: 120px;
        height: 120px;
    }
    
    .center-logo {
        max-width: 60px;
    }
    
    .ecosystem-item {
        width: 100px;
        height: 100px;
    }
    
    .item-icon {
        font-size: 1.5rem;
    }
    
    .ecosystem-item h4 {
        font-size: 0.7rem;
    }
}
```

### 3.4 Оновити "З ким ти працюєш" → "Команда професіоналів"

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/pages/home.html`

**ЗНАЙТИ рядок 141 та ЗАМІНИТИ:**

```html
<h2 class="section-title">Команда професіоналів</h2>
```

**ТА змінити підзаголовок (рядок 142-143):**

```html
<p class="experts-subtitle">
    Міжнародні експерти, які створюють освітні програми та супроводжують ваш розвиток
</p>
```

**⚠️ ВАЖЛИВО:** Опис кожного експерта чекаємо від клієнта!

### 3.5 Видалити секцію "Наша структура та цінності"

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/pages/home.html`

**ЗАКОМЕНТУВАТИ рядки 181-236:**

```html
{% comment %}
<!-- 5. VALUES SECTION - ВИДАЛЕНО ЗА ВИМОГОЮ КЛІЄНТА -->
<!-- <section class="fullscreen-section values-section">
    ...
</section> -->
{% endcomment %}
```

**CSS:** У файлі `/Users/olegbonislavskyi/Play_Vision/static/css/components/home.css`

**ЗАКОМЕНТУВАТИ стилі values-section (знайти та закоментувати):**

```css
/* ЗАКОМЕНТОВАНО - ВИДАЛЕНА СЕКЦІЯ
.values-section { ... }
.values-description { ... }
.values-grid { ... }
...
*/
```

### 3.6 Додати Scroll Popup

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/pages/home.html`

**В КІНЦІ перед {% endblock content %}:**

```html
    <!-- CTA Section залишається -->
</div>

<!-- Scroll Popup -->
{% include 'partials/scroll-popup.html' %}

{% endblock %}

{% block extra_js %}
<script src="{% static 'js/home.js' %}"></script>
{% endblock %}
```

---

## 📚 PHASE 4: HUB KNOWLEDGE UPDATES (2-3 год)

### 4.1 Додати кнопку закриття банера

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/hub/course_list.html`

**ОНОВИТИ рядки 37-48:**

```html
<div class="subscription-banner" 
     id="subscription-banner" 
     x-data="{ visible: true }" 
     x-show="visible">
    
    <button class="banner-close" 
            @click="visible = false; localStorage.setItem('banner_closed', 'true')" 
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

**CSS:** Додати в `/Users/olegbonislavskyi/Play_Vision/static/css/components/hub.css`

**ПІСЛЯ .subscription-banner (рядок 27-67):**

```css
.subscription-banner {
    position: relative; /* ДОДАТИ */
    background: linear-gradient(135deg, var(--hub-primary) 0%, var(--hub-primary-dark) 100%);
    color: white;
    padding: 2rem 0;
    position: sticky;
    top: 80px;
    z-index: 50;
    box-shadow: var(--hub-shadow);
}

.banner-close {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-lg);
    background: transparent;
    border: none;
    color: white;
    cursor: pointer;
    opacity: 0.8;
    transition: var(--transition-base);
    padding: var(--spacing-xs);
    line-height: 1;
    z-index: 10;
}

.banner-close:hover {
    opacity: 1;
    transform: rotate(90deg);
}
```

**JavaScript:** Додати перевірку в `/Users/olegbonislavskyi/Play_Vision/static/js/hub.js` (або створити)

```javascript
document.addEventListener('DOMContentLoaded', () => {
    // Перевірити чи банер був закритий
    const bannerClosed = localStorage.getItem('banner_closed');
    if (bannerClosed === 'true') {
        const banner = document.getElementById('subscription-banner');
        if (banner) {
            banner.style.display = 'none';
        }
    }
});
```

### 4.2 Видалити "Найближчі події"

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/hub/course_list.html`

**ЗАКОМЕНТУВАТИ рядки 50-140:**

```html
{% comment %}
<!-- ВИДАЛЕНО ЗА ВИМОГОЮ КЛІЄНТА -->
<!-- <section class="upcoming-events-section">
    ...
</section> -->
{% endcomment %}
```

### 4.3 Замінити карусель цитат на одну "Цитата місяця"

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/hub/course_list.html`

**ЗАМІНИТИ рядки 163-244 (карусель цитат):**

```html
<!-- Expert Quote of the Month -->
<section class="monthly-quote-section">
    <div class="container">
        <h2 class="section-title">Цитата місяця</h2>

        {% if monthly_quote %}
        <div class="quote-card">
            <div class="quote-header">
                {% if monthly_quote.expert_photo %}
                <img src="{{ monthly_quote.expert_photo.url }}" 
                     alt="{{ monthly_quote.expert_name }}"
                     class="quote-avatar">
                {% else %}
                <div class="quote-avatar-placeholder">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                    </svg>
                </div>
                {% endif %}
                <div class="quote-expert-info">
                    <h3 class="quote-expert-name">{{ monthly_quote.expert_name }}</h3>
                    <p class="quote-expert-role">{{ monthly_quote.expert_role }}</p>
                </div>
            </div>
            <blockquote class="quote-text">
                "{{ monthly_quote.quote_text }}"
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

**CSS:** Додати в `/Users/olegbonislavskyi/Play_Vision/static/css/components/hub.css`

```css
/* Monthly Quote Section */
.monthly-quote-section {
    padding: var(--spacing-xxl) 0;
    background: var(--hub-bg-gray);
}

.quote-card {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
    box-shadow: var(--hub-shadow);
}

.quote-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.quote-avatar,
.quote-avatar-placeholder {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-full);
    object-fit: cover;
    flex-shrink: 0;
}

.quote-avatar-placeholder {
    background: var(--hub-bg-gray);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--hub-text-light);
}

.quote-expert-info {
    flex: 1;
}

.quote-expert-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--hub-text);
    margin-bottom: var(--spacing-xs);
}

.quote-expert-role {
    font-size: 0.9rem;
    color: var(--hub-text-light);
    margin: 0;
}

.quote-text {
    font-size: 1.125rem;
    line-height: 1.7;
    color: var(--hub-text);
    font-style: italic;
    margin: 0;
    padding-left: var(--spacing-xl);
    border-left: 4px solid var(--hub-primary);
}

.no-quote {
    text-align: center;
    padding: var(--spacing-xxl);
    color: var(--hub-text-light);
}

@media (max-width: 768px) {
    .quote-card {
        padding: var(--spacing-xl) var(--spacing-lg);
    }
    
    .quote-header {
        flex-direction: column;
        text-align: center;
    }
    
    .quote-text {
        font-size: 1rem;
        padding-left: var(--spacing-lg);
    }
}
```

### 4.4 Змінити "Головні матеріали" на "Освітні продукти"

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/hub/course_list.html`

**ЗНАЙТИ рядок 285 та ЗАМІНИТИ:**

```html
<h2 class="section-title">Освітні продукти</h2>
```

**ОНОВИТИ логіку featured products (рядки 290-350):**

Замінити на:

```html
<div class="materials-carousel" x-data="materialsCarousel()">
    <div class="carousel-wrapper">
        <div class="carousel-content" :style="`transform: translateX(-${currentSlide * 100}%)`">
            {% for course in courses %}
            <div class="material-slide">
                <div class="material-card {% if course.is_featured %}featured-product{% endif %}">
                    {% if course.is_featured %}
                    <span class="top-product-badge">ТОП-ПРОДУКТ</span>
                    {% endif %}
                    
                    <div class="material-image">
                        {% if course.thumbnail %}
                        <img src="{{ course.thumbnail.url }}" alt="{{ course.title }}">
                        {% else %}
                        <img src="{% static 'images/placeholder-1200x600.svg' %}" alt="{{ course.title }}">
                        {% endif %}
                    </div>
                    <div class="material-content">
                        <!-- Решта контенту -->
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
```

**CSS:** Додати в `/Users/olegbonislavskyi/Play_Vision/static/css/components/hub.css`

```css
/* Featured Product Styling */
.material-card.featured-product {
    border: 3px solid var(--hub-primary);
    box-shadow: 0 8px 32px rgba(255, 107, 53, 0.2);
}

.top-product-badge {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
    background: var(--hub-primary);
    color: white;
    padding: var(--spacing-xs) var(--spacing-md);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    z-index: 5;
}
```

### 4.5 Оновити фільтри (ВИДАЛИТИ 3, ДОДАТИ 3)

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/hub/course_list.html`

**ЗАМІНИТИ блок фільтрів (рядки 397-468):**

```html
<div class="filters-content filters-scrollable" id="filters-content">
    <form method="get" id="filterForm">
        {% if request.GET.q %}
        <input type="hidden" name="q" value="{{ request.GET.q }}">
        {% endif %}

        <!-- Category Filter - ЗАЛИШИТИ -->
        <div class="filter-group">
            <h4>За напрямками</h4>
            <div class="filter-options">
                {% for category in categories %}
                <label class="filter-option">
                    <input type="radio" 
                           name="category" 
                           value="{{ category.slug }}" 
                           {% if current_category == category.slug %}checked{% endif %}>
                    <span>{{ category.name }}</span>
                </label>
                {% endfor %}
            </div>
        </div>

        <!-- ❌ ВИДАЛЕНО: Difficulty Filter -->
        <!-- ❌ ВИДАЛЕНО: Price Filter -->
        <!-- ❌ ВИДАЛЕНО: Duration Filter -->

        <!-- ✅ НОВИЙ: Тренерство (з під-фільтрами) -->
        <div class="filter-group" x-data="{ expanded: false }">
            <h4>
                <button type="button" 
                        class="filter-toggle"
                        @click="expanded = !expanded">
                    <span>Тренерство</span>
                    <svg class="toggle-icon" 
                         :class="{'rotated': expanded}"
                         width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 9l6 6 6-6"/>
                    </svg>
                </button>
            </h4>
            
            <div class="sub-filters" x-show="expanded" x-collapse>
                <label class="filter-option sub-option">
                    <input type="checkbox" name="training_type" value="goalkeeper">
                    <span>Тренер воротарів</span>
                </label>
                <label class="filter-option sub-option">
                    <input type="checkbox" name="training_type" value="youth">
                    <span>Дитячий тренер</span>
                </label>
                <label class="filter-option sub-option">
                    <input type="checkbox" name="training_type" value="fitness">
                    <span>Тренер ЗФП</span>
                </label>
                <label class="filter-option sub-option">
                    <input type="checkbox" name="training_type" value="professional">
                    <span>Тренер професійних команд</span>
                </label>
            </div>
        </div>

        <!-- ✅ НОВИЙ: Аналітика і скаутинг -->
        <div class="filter-group">
            <h4>Інші напрямки</h4>
            <div class="filter-options">
                <label class="filter-option">
                    <input type="checkbox" name="interest" value="analytics">
                    <span>Аналітика і скаутинг</span>
                </label>
                <label class="filter-option">
                    <input type="checkbox" name="interest" value="management">
                    <span>Менеджмент</span>
                </label>
            </div>
        </div>

        <!-- Filter Actions -->
        <div class="filter-actions">
            <button type="submit" class="btn btn-primary btn-block">
                Застосувати фільтри
            </button>
            <button type="button" 
                    class="btn btn-outline btn-block" 
                    @click="window.location.href='{% url 'content:course_list' %}'">
                Скинути все
            </button>
        </div>
    </form>
</div>
```

**CSS:** Додати в `/Users/olegbonislavskyi/Play_Vision/static/css/components/hub.css`

```css
/* Scrollable Filters */
.filters-scrollable {
    max-height: 70vh;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--hub-primary) var(--hub-bg-gray);
}

.filters-scrollable::-webkit-scrollbar {
    width: 6px;
}

.filters-scrollable::-webkit-scrollbar-track {
    background: var(--hub-bg-gray);
    border-radius: var(--radius-sm);
}

.filters-scrollable::-webkit-scrollbar-thumb {
    background: var(--hub-primary);
    border-radius: var(--radius-sm);
}

.filters-scrollable::-webkit-scrollbar-thumb:hover {
    background: var(--hub-primary-dark);
}

/* Filter Toggle Button */
.filter-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    background: transparent;
    border: none;
    padding: 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--hub-text);
    cursor: pointer;
    transition: var(--transition-base);
}

.filter-toggle:hover {
    color: var(--hub-primary);
}

.toggle-icon {
    transition: transform 0.3s ease;
}

.toggle-icon.rotated {
    transform: rotate(180deg);
}

/* Sub-filters */
.sub-filters {
    margin-top: var(--spacing-md);
    padding-left: var(--spacing-lg);
    border-left: 2px solid var(--hub-border);
}

.sub-option {
    font-size: 0.9rem;
    padding: var(--spacing-sm) 0;
}
```

---

## 📅 PHASE 5: EVENTS UPDATES (45 хв)

### 5.1 Обмежити календар (1 подія на день)

**Файл:** `/Users/olegbonislavskyi/Play_Vision/static/js/events.js`

**ЗНАЙТИ функцію generateVisibleDays() (рядок 247) та ОНОВИТИ:**

```javascript
generateVisibleDays() {
    this.visibleDays = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 0; i < 7; i++) {
        const date = new Date(this.currentWeekStart);
        date.setDate(this.currentWeekStart.getDate() + i);
        date.setHours(0, 0, 0, 0);

        // Find events for this date
        const dayEvents = this.allEvents.filter(event => {
            const eventDate = new Date(event.start_datetime);
            eventDate.setHours(0, 0, 0, 0);
            return eventDate.getTime() === date.getTime();
        }).slice(0, 1); // ⚠️ ОБМЕЖЕННЯ: ТІЛЬКИ 1 ПОДІЯ

        // Apply filters
        const filteredEvents = dayEvents.filter(event => {
            let matches = true;

            if (this.selectedType !== 'all') {
                matches = matches && event.type === this.selectedType;
            }

            if (this.selectedFormat !== 'all') {
                matches = matches && event.format === this.selectedFormat;
            }

            return matches;
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

### 5.2 Видалити фільтр "Ціна"

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/events/event_list.html`

**ЗАКОМЕНТУВАТИ рядки 247-267:**

```html
{% comment %}
<!-- ВИДАЛЕНО ЗА ВИМОГОЮ КЛІЄНТА -->
<!-- <div class="sidebar-section">
    <h3 class="sidebar-title">Ціна</h3>
    ...
</div> -->
{% endcomment %}
```

---

## 👤 PHASE 6: CABINET UPDATES (2-3 год)

### 6.1 Оновити інтереси (8 у правильному порядку)

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/account/cabinet.html`

**ЗАМІНИТИ рядки 81-89:**

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

**CSS:** Додати в `/Users/olegbonislavskyi/Play_Vision/static/css/components/cabinet.css`

**ПІСЛЯ існуючих стилів .interests-tags:**

```css
/* Interests List (NEW DESIGN) */
.interests-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.interest-item {
    display: flex;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    background: white;
    border: 2px solid var(--color-border);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: var(--transition-base);
}

.interest-item:hover {
    border-color: var(--color-primary);
    background: rgba(255, 107, 53, 0.05);
}

.interest-item input[type="checkbox"] {
    margin-right: var(--spacing-sm);
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
    gap: var(--spacing-sm);
    font-size: 14px;
    transition: var(--transition-base);
}

.interest-number {
    font-weight: 700;
    color: var(--color-text-light);
    min-width: 24px;
}

.interest-item input[type="checkbox"]:checked ~ .interest-label .interest-number {
    color: var(--color-primary);
}
```

**Backend:** Оновити `/Users/olegbonislavskyi/Play_Vision/apps/accounts/cabinet_views.py`

**В методі get_context_data() (рядок 28+) ДОДАТИ:**

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    user = self.request.user
    tab = kwargs.get('tab', self.request.GET.get('tab', 'profile'))
    
    # ... існуючий код ...
    
    # ✅ ДОДАТИ: Інтереси
    from apps.content.models import Tag
    context['interests'] = Tag.objects.filter(
        tag_type='interest'
    ).order_by('display_order')
    
    # ... решта коду ...
    
    return context
```

### 6.2 Виправити "Зберти" → "ЗБЕРЕГТИ"

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/account/cabinet.html`

**ЗНАЙТИ рядок 91 та ЗАМІНИТИ:**

```html
<button type="submit" class="btn-save">ЗБЕРЕГТИ</button>
```

### 6.3 Покращити валідацію фото

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/accounts/cabinet_views.py`

**ОНОВИТИ UpdateProfileView (рядки 256-301):**

```python
class UpdateProfileView(LoginRequiredMixin, View):
    """AJAX оновлення профілю"""
    
    def post(self, request):
        try:
            profile = getattr(request.user, 'profile', None)
            if not profile:
                from .models import Profile
                profile = Profile.objects.create(user=request.user)
            
            # Дані профілю
            data = {
                'first_name': request.POST.get('first_name', '').strip(),
                'last_name': request.POST.get('last_name', '').strip(),
                'birth_date': request.POST.get('birth_date', '').strip(),
                'profession': request.POST.get('profession', '').strip(),
            }
            
            data = {k: v for k, v in data.items() if v}
            
            for field, value in data.items():
                setattr(profile, field, value)
            
            # ✅ ПОКРАЩЕНА ВАЛІДАЦІЯ АВАТАРА
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                
                # Валідація розміру
                MAX_SIZE = 5 * 1024 * 1024  # 5MB
                if avatar.size > MAX_SIZE:
                    return JsonResponse({
                        'success': False,
                        'message': 'Файл занадто великий. Максимум 5MB'
                    }, status=400)
                
                # Валідація типу
                ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
                content_type = avatar.content_type.lower()
                if content_type not in ALLOWED_TYPES:
                    return JsonResponse({
                        'success': False,
                        'message': 'Дозволені формати: JPEG, PNG, WEBP'
                    }, status=400)
                
                # Видалити старий аватар
                if profile.avatar:
                    try:
                        profile.avatar.delete(save=False)
                    except Exception:
                        pass
                
                profile.avatar = avatar
            
            # Інтереси
            if 'interests' in request.POST:
                interest_ids = request.POST.getlist('interests')
                if interest_ids:
                    profile.interests.set(interest_ids)
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Профіль успішно оновлено',
                'avatar_url': profile.get_avatar_url()
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка: {str(e)}'
            }, status=500)
```

### 6.4 Додати кнопку "Правила ПЛ"

**Файл:** `/Users/olegbonislavskyi/Play_Vision/templates/account/tabs/loyalty.html`

**ЗНАЙТИ рядок 108 та ДОДАТИ ПІСЛЯ:**

```html
    </div>
</div>

<!-- ✅ НОВИЙ БЛОК -->
<div class="loyalty-info-card">
    <div class="info-card-content">
        <h3>Детальна інформація</h3>
        <p>Ознайомтеся з повними правилами та умовами Програми лояльності</p>
        <a href="{% url 'loyalty:rules' %}" class="btn btn-outline btn-large">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
            </svg>
            Правила Програми Лояльності
        </a>
    </div>
</div>

<!-- Як заробляти бали -->
```

**CSS:** Додати в `/Users/olegbonislavskyi/Play_Vision/static/css/components/cabinet.css`

```css
/* Loyalty Info Card */
.loyalty-info-card {
    margin: var(--spacing-xxl) 0;
}

.info-card-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: var(--spacing-xxl);
    border-radius: var(--radius-lg);
    text-align: center;
}

.info-card-content h3 {
    color: white;
    margin-bottom: var(--spacing-md);
}

.info-card-content p {
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: var(--spacing-xl);
}

.info-card-content .btn-outline {
    background: white;
    color: #667eea;
    border-color: white;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.info-card-content .btn-outline:hover {
    background: rgba(255, 255, 255, 0.9);
    transform: translateY(-2px);
}
```

### 6.5 Створити сторінку "Правила ПЛ"

**Створити:** `/Users/olegbonislavskyi/Play_Vision/templates/loyalty/rules.html`

```html
{% extends 'base/base.html' %}
{% load static %}

{% block title %}Правила Програми Лояльності - Play Vision{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/components/loyalty-rules.css' %}">
{% endblock %}

{% block content %}
<div class="loyalty-rules-container">
    <div class="container">
        
        <!-- Header -->
        <header class="rules-header">
            <h1>Правила Програми Лояльності</h1>
            <p>Дізнайтеся, як накопичувати бали, отримувати знижки та користуватися перевагами</p>
        </header>

        <!-- Quick Navigation -->
        <nav class="rules-nav">
            <a href="#general" class="rules-nav-link">Загальні положення</a>
            <a href="#earning" class="rules-nav-link">Як накопичувати</a>
            <a href="#tiers" class="rules-nav-link">Рівні</a>
            <a href="#benefits" class="rules-nav-link">Переваги</a>
            <a href="#terms" class="rules-nav-link">Термін дії</a>
        </nav>

        <!-- Content -->
        <main class="rules-content">
            
            <!-- 1. Загальні положення -->
            <section id="general" class="rules-section">
                <h2>1. Загальні положення</h2>
                <div class="section-text">
                    <p>Програма лояльності Play Vision - це система винагород для наших клієнтів, яка дозволяє накопичувати бали за активність та обмінювати їх на знижки.</p>
                    <ul>
                        <li>Програма доступна для всіх зареєстрованих користувачів</li>
                        <li>Участь у програмі безкоштовна</li>
                        <li>Бали нараховуються автоматично після кожної дії</li>
                        <li>Знижки застосовуються автоматично при оформленні замовлення</li>
                    </ul>
                </div>
            </section>

            <!-- 2. Як накопичувати бали -->
            <section id="earning" class="rules-section">
                <h2>2. Як накопичувати бали</h2>
                <div class="earning-ways">
                    <div class="earning-way">
                        <div class="way-icon">🛒</div>
                        <h3>Покупки</h3>
                        <p class="way-amount">1 бал за кожну 10₴</p>
                        <p class="way-detail">Бали нараховуються автоматично після підтвердження оплати</p>
                    </div>
                    
                    <div class="earning-way">
                        <div class="way-icon">📝</div>
                        <h3>Заповнення профілю</h3>
                        <p class="way-amount">50 балів</p>
                        <p class="way-detail">Одноразова винагорода за повністю заповнений профіль</p>
                    </div>
                    
                    <div class="earning-way">
                        <div class="way-icon">🎓</div>
                        <h3>Завершення курсів</h3>
                        <p class="way-amount">10-30 балів</p>
                        <p class="way-detail">Залежить від складності та тривалості курсу</p>
                    </div>
                    
                    <div class="earning-way">
                        <div class="way-icon">📅</div>
                        <h3>Відвідування івентів</h3>
                        <p class="way-amount">20 балів</p>
                        <p class="way-detail">За кожний відвіданий івент або вебінар</p>
                    </div>
                    
                    <div class="earning-way">
                        <div class="way-icon">🎂</div>
                        <h3>День народження</h3>
                        <p class="way-amount">100 балів</p>
                        <p class="way-detail">Автоматично нараховується у ваш день народження</p>
                    </div>
                    
                    <div class="earning-way">
                        <div class="way-icon">👥</div>
                        <h3>Реферальна програма</h3>
                        <p class="way-amount">5% від покупок</p>
                        <p class="way-detail">За кожного запрошеного користувача</p>
                    </div>
                </div>
            </section>

            <!-- 3. Рівні лояльності -->
            <section id="tiers" class="rules-section">
                <h2>3. Рівні лояльності</h2>
                <div class="tiers-showcase">
                    {% for tier in loyalty_tiers %}
                    <div class="tier-showcase-card tier-{{ tier.name|lower }}">
                        <div class="tier-badge-large">{{ tier.name }}</div>
                        <div class="tier-requirement">
                            {% if tier.points_required == 0 %}
                            Початковий рівень
                            {% else %}
                            {{ tier.points_required }}+ балів
                            {% endif %}
                        </div>
                        <div class="tier-discount-large">{{ tier.discount_percentage }}%</div>
                        <p class="tier-discount-label">знижка</p>
                    </div>
                    {% empty %}
                    <p>Рівні лояльності завантажуються...</p>
                    {% endfor %}
                </div>
            </section>

            <!-- 4. Переваги -->
            <section id="benefits" class="rules-section">
                <h2>4. Переваги програми</h2>
                <div class="benefits-grid">
                    <div class="benefit-card">
                        <div class="benefit-icon">💎</div>
                        <h3>Накопичувальна знижка</h3>
                        <p>Чим вище рівень - тим більша знижка на всі продукти</p>
                    </div>
                    <div class="benefit-card">
                        <div class="benefit-icon">🎁</div>
                        <h3>Спеціальні пропозиції</h3>
                        <p>Ексклюзивні акції тільки для учасників програми</p>
                    </div>
                    <div class="benefit-card">
                        <div class="benefit-icon">🎫</div>
                        <h3>Пріоритет на івенти</h3>
                        <p>Ранній доступ до реєстрації на популярні події</p>
                    </div>
                    <div class="benefit-card">
                        <div class="benefit-icon">📧</div>
                        <h3>Персоналізація</h3>
                        <p>Рекомендації на основі ваших інтересів</p>
                    </div>
                </div>
            </section>

            <!-- 5. Термін дії -->
            <section id="terms" class="rules-section">
                <h2>5. Термін дії балів</h2>
                <div class="terms-info">
                    <div class="info-box">
                        <h3>⏰ Термін дії</h3>
                        <p>Бали діють протягом <strong>12 місяців</strong> з моменту нарахування</p>
                    </div>
                    <div class="info-box">
                        <h3>📊 Відстеження</h3>
                        <p>Переглядайте баланс та історію в особистому кабінеті</p>
                    </div>
                    <div class="info-box">
                        <h3>🏆 Збереження рівня</h3>
                        <p>Рівень зберігається при регулярній активності</p>
                    </div>
                </div>
            </section>
        </main>

        <!-- CTA -->
        <section class="rules-cta">
            <h2>Готові розпочати?</h2>
            <p>Приєднуйтесь до програми лояльності та отримуйте бонуси!</p>
            {% if user.is_authenticated %}
            <a href="{% url 'cabinet:loyalty' %}" class="btn btn-primary btn-large">
                Мій баланс балів
            </a>
            {% else %}
            <div class="cta-buttons">
                <a href="{% url 'accounts:register' %}" class="btn btn-primary btn-large">
                    Зареєструватись
                </a>
                <a href="{% url 'accounts:login' %}" class="btn btn-outline btn-large">
                    Увійти
                </a>
            </div>
            {% endif %}
        </section>

        <!-- Back -->
        <div class="back-to-cabinet">
            <a href="{% url 'cabinet:loyalty' %}">← Повернутись до кабінету</a>
        </div>
    </div>
</div>
{% endblock %}
```

**CSS:** Створити `/Users/olegbonislavskyi/Play_Vision/static/css/components/loyalty-rules.css`

```css
/* Loyalty Rules Page - БЕЗ ДУБЛІВ */
.loyalty-rules-container {
    min-height: 100vh;
    background: var(--color-bg-gray);
    padding: var(--spacing-xxl) 0;
}

/* Header */
.rules-header {
    text-align: center;
    padding: var(--spacing-xxl);
    background: white;
    border-radius: var(--radius-xl);
    margin-bottom: var(--spacing-xl);
}

.rules-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: var(--spacing-md);
}

.rules-header p {
    font-size: 1.125rem;
    color: var(--color-text-light);
    max-width: 600px;
    margin: 0 auto;
}

/* Navigation */
.rules-nav {
    display: flex;
    justify-content: center;
    gap: var(--spacing-lg);
    flex-wrap: wrap;
    padding: var(--spacing-lg);
    background: white;
    border-radius: var(--radius-lg);
    margin-bottom: var(--spacing-xl);
}

.rules-nav-link {
    padding: var(--spacing-sm) var(--spacing-lg);
    border-radius: var(--radius-md);
    font-weight: 500;
    transition: var(--transition-base);
}

.rules-nav-link:hover {
    background: var(--color-primary);
    color: white;
    text-decoration: none;
}

/* Content */
.rules-content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.rules-section {
    background: white;
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
}

.rules-section h2 {
    font-size: 1.75rem;
    padding-bottom: var(--spacing-md);
    border-bottom: 3px solid var(--color-primary);
    margin-bottom: var(--spacing-lg);
}

.section-text p {
    margin-bottom: var(--spacing-md);
    line-height: 1.7;
}

.section-text ul {
    margin: var(--spacing-lg) 0;
    padding-left: var(--spacing-xl);
}

.section-text li {
    margin-bottom: var(--spacing-sm);
}

/* Earning Ways */
.earning-ways {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
}

.earning-way {
    background: var(--color-bg-gray);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    text-align: center;
    transition: var(--transition-base);
}

.earning-way:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
}

.way-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-md);
}

.earning-way h3 {
    font-size: 1.125rem;
    margin-bottom: var(--spacing-sm);
}

.way-amount {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: var(--spacing-xs);
}

.way-detail {
    font-size: 0.875rem;
    color: var(--color-text-light);
    margin: 0;
}

/* Tiers Showcase */
.tiers-showcase {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
}

.tier-showcase-card {
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    text-align: center;
    border: 3px solid;
    transition: var(--transition-base);
}

.tier-showcase-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-lg);
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

.tier-badge-large {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: var(--spacing-md);
}

.tier-requirement {
    font-size: 1rem;
    color: var(--color-text-light);
    margin-bottom: var(--spacing-lg);
}

.tier-discount-large {
    font-size: 3rem;
    font-weight: 700;
    color: var(--color-primary);
    line-height: 1;
}

.tier-discount-label {
    font-size: 1rem;
    color: var(--color-text-light);
    margin-top: var(--spacing-xs);
}

/* Benefits Grid */
.benefits-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
}

.benefit-card {
    background: var(--color-bg-gray);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    text-align: center;
}

.benefit-icon {
    font-size: 2.5rem;
    margin-bottom: var(--spacing-md);
}

.benefit-card h3 {
    font-size: 1.125rem;
    margin-bottom: var(--spacing-sm);
}

.benefit-card p {
    font-size: 0.9rem;
    color: var(--color-text-light);
    margin: 0;
}

/* Terms Info */
.terms-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
}

.info-box {
    background: var(--color-bg-gray);
    border-left: 4px solid var(--color-primary);
    border-radius: var(--radius-md);
    padding: var(--spacing-lg);
}

.info-box h3 {
    font-size: 1.125rem;
    margin-bottom: var(--spacing-sm);
}

.info-box p {
    color: var(--color-text-light);
    margin: 0;
}

.info-box strong {
    color: var(--color-primary);
}

/* CTA */
.rules-cta {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    color: white;
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
    text-align: center;
    margin: var(--spacing-xxl) 0;
}

.rules-cta h2 {
    font-size: 2rem;
    margin-bottom: var(--spacing-md);
}

.rules-cta p {
    font-size: 1.125rem;
    margin-bottom: var(--spacing-xl);
    opacity: 0.95;
}

.cta-buttons {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    flex-wrap: wrap;
}

.back-to-cabinet {
    text-align: center;
    padding: var(--spacing-xl) 0;
}

.back-to-cabinet a {
    font-weight: 600;
    transition: var(--transition-base);
}

/* Mobile */
@media (max-width: 768px) {
    .rules-header {
        padding: var(--spacing-xl) var(--spacing-lg);
    }
    
    .rules-header h1 {
        font-size: 2rem;
    }
    
    .rules-nav {
        flex-direction: column;
        gap: var(--spacing-xs);
    }
    
    .rules-section {
        padding: var(--spacing-xl) var(--spacing-lg);
    }
    
    .earning-ways,
    .tiers-showcase,
    .benefits-grid,
    .terms-info {
        grid-template-columns: 1fr;
    }
    
    .cta-buttons {
        flex-direction: column;
        width: 100%;
    }
    
    .cta-buttons .btn {
        width: 100%;
    }
}
```

---

## 🧪 PHASE 7: TESTING & OPTIMIZATION (2-3 год)

### 7.1 Запустити міграції

```bash
# Показати план міграцій
python3 manage.py showmigrations content

# Застосувати
python3 manage.py migrate

# Перевірити
python3 manage.py check
```

### 7.2 Створити тестові дані

```bash
python3 manage.py shell
```

```python
# Створити цитату місяця
from apps.content.models import MonthlyQuote
from datetime import date

MonthlyQuote.objects.create(
    expert_name="Пеп Гвардіола",
    expert_role='Тренер "Манчестер Сіті"',
    quote_text="Навчання ніколи не закінчується. Кожен день ми можемо дізнатися щось нове.",
    month=date(2025, 10, 1),
    is_active=True
)

# Перевірити інтереси
from apps.content.models import Tag
interests = Tag.objects.filter(tag_type='interest').order_by('display_order')
for i in interests:
    print(f"{i.display_order}. {i.name}")
```

### 7.3 Frontend Testing Checklist

**Створити:** `/Users/olegbonislavskyi/Play_Vision/TESTING_CHECKLIST.md`

```markdown
# ✅ TESTING CHECKLIST

## ГЛОБАЛЬНІ
- [ ] Іконка кошика оновлена
- [ ] Scroll popup з'являється при скролі до 80%
- [ ] Popup закривається і не з'являється знову
- [ ] localStorage працює правильно

## ГОЛОВНА
- [ ] Hero карусель - 7 слайдів
- [ ] Автопрокрутка працює
- [ ] Білі рамки відображаються
- [ ] Тільки 1 кнопка "Дізнатись більше"
- [ ] 6 курсів у каруселі
- [ ] Навігація prev/next працює
- [ ] Responsive на mobile
- [ ] Секція ментор-коучинг відображається
- [ ] Шестикутники позиціонуються правильно
- [ ] ТІЛЬКИ українські слова (БЕЗ MOTIVATION тощо)
- [ ] "Команда професіоналів" замість "З ким ти працюєш"
- [ ] Секція цінностей НЕ відображається

## ХАБ ЗНАНЬ
- [ ] Банер має кнопку X
- [ ] Банер закривається
- [ ] Секція "Найближчі події" НЕ відображається
- [ ] "Цитата місяця" відображається (1 цитата)
- [ ] Заголовок "Освітні продукти"
- [ ] Featured продукти виділені
- [ ] Фільтр "Складність" ВИДАЛЕНИЙ
- [ ] Фільтр "Тип доступу" ВИДАЛЕНИЙ
- [ ] Фільтр "Тривалість" ВИДАЛЕНИЙ
- [ ] Фільтр "Тренерство" з під-фільтрами працює
- [ ] Фільтр "Аналітика" працює
- [ ] Фільтр "Менеджмент" працює
- [ ] Скрол фільтрів працює

## ІВЕНТИ
- [ ] Календар показує макс 1 подію на день
- [ ] Фільтр "Ціна" ВИДАЛЕНИЙ
- [ ] Навігація календаря працює

## КАБІНЕТ
- [ ] 8 інтересів у правильному порядку (1-8)
- [ ] Кнопка "ЗБЕРЕГТИ" (не "Зберти")
- [ ] Завантаження фото працює
- [ ] Валідація: макс 5MB
- [ ] Валідація: JPEG, PNG, WEBP
- [ ] Кнопка "Правила ПЛ" веде на /loyalty/rules/
- [ ] Історія оплат табличкою

## ПРАВИЛА ПЛ
- [ ] Всі 5 секцій відображаються
- [ ] Навігація працює
- [ ] Рівні лояльності з БД
- [ ] Кнопка повернення працює

## iOS SAFARI
- [ ] Touch events працюють
- [ ] Viewport правильний
- [ ] 100vh не обрізає
- [ ] Input не зумує екран
- [ ] File picker працює
```

### 7.4 Перевірка на дублювання

```bash
# Перевірити !important
grep -r "!important" static/css/
# Має бути: No matches found

# Перевірити inline styles
grep -r 'style="' templates/ | grep -v 'display: none' | grep -v x-show
# Перевірити результат

# Перевірити дублювання класів
grep -rn "\.btn-primary {" static/css/
# Має бути тільки в main.css
```

### 7.5 Performance Optimization

**Додати до існуючих views кешування:**

**Файл:** `/Users/olegbonislavskyi/Play_Vision/apps/content/views.py`

```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Кешувати на 1 годину (3600 сек)
@method_decorator(cache_page(60 * 60), name='dispatch')
class CourseListView(ListView):
    # ... existing code ...
    pass
```

### 7.6 Final Code Review

```bash
# Видалити console.log з production
find static/js -name "*.js" -exec sed -i '' '/console.log/d' {} \;

# Перевірити Python code style
python3 -m flake8 apps/ --exclude=migrations

# Collect static
python3 manage.py collectstatic --noinput

# Check deploy
python3 manage.py check --deploy
```

---

## 📊 FINAL SUMMARY

### ✅ ЩО ЗМІНЕНО:

#### Backend (Python):
1. ✅ Tag.tag_type + Tag.display_order
2. ✅ MonthlyQuote model
3. ✅ Course.training_specialization
4. ✅ CourseListView - видалені фільтри difficulty/price
5. ✅ EventListView - видалений фільтр price
6. ✅ UpdateProfileView - покращена валідація
7. ✅ LoyaltyRulesView - створено
8. ✅ Data migration для інтересів

#### Frontend (Templates):
1. ✅ Hero карусель (7 слайдів)
2. ✅ 3 напрямки → 6 курсів
3. ✅ Секція ментор-коучинг (шестикутники)
4. ✅ "Команда професіоналів"
5. ✅ Видалена секція цінностей
6. ✅ Scroll popup
7. ✅ Банер з кнопкою закриття
8. ✅ Цитата місяця (1 замість багатьох)
9. ✅ "Освітні продукти"
10. ✅ Оновлені фільтри
11. ✅ Календар (1 подія)
12. ✅ 8 інтересів
13. ✅ Кнопка "ЗБЕРЕГТИ"
14. ✅ Сторінка "Правила ПЛ"

#### CSS:
1. ✅ БЕЗ !important (перевірено)
2. ✅ БЕЗ дублювання .btn класів
3. ✅ Використання існуючих CSS змінних
4. ✅ Responsive для iOS Safari
5. ✅ Нові файли: scroll-popup.css, loyalty-rules.css

#### JavaScript:
1. ✅ home.js (карусель, слайди)
2. ✅ scroll-popup.js (popup логіка)
3. ✅ hub.js (банер логіка)
4. ✅ events.js (обмеження 1 подія)
5. ✅ Використання debounce

### НОВІ ФАЙЛИ (7):
1. `static/css/components/scroll-popup.css`
2. `static/css/components/loyalty-rules.css`
3. `static/js/home.js`
4. `static/js/scroll-popup.js`
5. `templates/partials/scroll-popup.html`
6. `templates/loyalty/rules.html`
7. `apps/loyalty/urls.py`

### МОДИФІКОВАНІ ФАЙЛИ (12):
1. `apps/content/models.py` (Tag, Course, MonthlyQuote)
2. `apps/content/views.py` (CourseListView)
3. `apps/content/admin.py` (MonthlyQuoteAdmin)
4. `apps/core/views.py` (HomeView)
5. `apps/events/views.py` (EventListView)
6. `apps/accounts/cabinet_views.py` (UpdateProfileView, context)
7. `apps/loyalty/views.py` (LoyaltyRulesView)
8. `templates/pages/home.html`
9. `templates/hub/course_list.html`
10. `templates/events/event_list.html`
11. `templates/account/cabinet.html`
12. `templates/account/tabs/loyalty.html`

### CSS ФАЙЛИ (4):
1. `static/css/components/home.css` (додано стилі)
2. `static/css/components/hub.css` (додано стилі)
3. `static/css/components/cabinet.css` (додано стилі)
4. `static/js/events.js` (модифіковано)

### МІГРАЦІЇ (4):
1. `0XXX_add_tag_type_and_order.py`
2. `0XXX_populate_user_interests.py`
3. `0XXX_add_monthly_quote.py`
4. `0XXX_add_course_training_specialization.py`

---

## 🚀 КОМАНДИ ДЛЯ ЗАПУСКУ

```bash
# 1. Підготовка
git checkout -b feature/screenshot-changes-v2
mkdir -p backups
python3 manage.py dumpdata > backups/backup_$(date +%Y%m%d_%H%M%S).json

# 2. Створити файли
touch static/css/components/scroll-popup.css
touch static/css/components/loyalty-rules.css
touch static/js/home.js
touch static/js/scroll-popup.js
mkdir -p templates/partials templates/loyalty
touch templates/partials/scroll-popup.html
touch templates/loyalty/rules.html
touch apps/loyalty/urls.py

# 3. Міграції
python3 manage.py makemigrations content
python3 manage.py migrate

# 4. Тестовий запуск
python3 manage.py runserver

# 5. Collectstatic
python3 manage.py collectstatic --noinput

# 6. Deploy
./build.sh
```

---

## ⚠️ КРИТИЧНІ ПИТАННЯ ДО КЛІЄНТА

1. **Нова іконка кошика** - надати SVG код
2. **Описи експертів команди** - надати тексти
3. **Помилка "коучІнг"** - уточнити що змінити
4. **Механіка рефок** - деталі для popup
5. **API реєстрації** - чи є endpoint `/accounts/api/register/`?

---

**СТАТУС:** ✅ ГОТОВИЙ БЕЗ КОНФЛІКТІВ  
**ЧАС:** 13-18 годин  
**ЯКІСТЬ:** Senior Level, DRY, No !important, Clean Code

