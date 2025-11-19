# 🚨 КРИТИЧНИЙ АУДИТ CMS ФУНКЦІОНАЛУ — ПЕРЕД ЗДАЧЕЮ ПРОЕКТУ

**Дата аудиту:** 19 листопада 2025  
**Статус:** 🔴 КРИТИЧНІ ПРОБЛЕМИ ЗНАЙДЕНО

---

## ❌ КРИТИЧНІ ПОМИЛКИ (БЛОКЕРИ)

### 🔴 #1 — ВІДСУТНІЙ CONTEXT PROCESSOR ДЛЯ CMS ДАНИХ

**Файл:** `apps/cms/context_processors.py`  
**Проблема:** Context processor `site_content()` повертає ТІЛЬКИ `country_code` і `theme`, але НЕ передає CMS об'єкти!

**Що очікується в templates:**
```python
# templates/pages/home.html використовує:
- cms_hero_slides
- cms_experts  
- main_courses

# templates/pages/about.html використовує:
- cms_experts

# templates/pages/mentoring.html використовує:
- cms_experts
```

**Що є зараз:**
```python
# apps/cms/context_processors.py:40
def site_content(request):
    country_code = get_country_code(request)
    theme = request.COOKIES.get('theme', 'light')
    
    return {
        'country_code': country_code,
        'theme': theme,
        'is_ukraine': country_code == 'UA',
    }
    # ❌ НЕ ПОВЕРТАЄ: cms_hero_slides, cms_experts, main_courses!
```

**ЩО ВІДПАДЕ:**
- Hero слайди на головній — показуватиметься fallback hardcode
- Експерти на всіх 3 сторінках — показуватиметься hardcode
- Основні програми — показуватиметься або порожньо, або fallback

**РІШЕННЯ:**  
Додати до `site_content()`:
```python
def site_content(request):
    country_code = get_country_code(request)
    theme = request.COOKIES.get('theme', 'light')
    
    # Додати CMS дані
    from apps.cms.models import HeroSlide, ExpertCard
    from apps.content.models import Course
    
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by('order')
    experts = ExpertCard.objects.filter(is_active=True).order_by('order')
    
    # Featured courses для головної
    featured = FeaturedCourse.objects.filter(
        is_active=True, 
        page='home'
    ).select_related('course').order_by('order')
    main_courses = [f.course for f in featured if f.course]
    
    return {
        'country_code': country_code,
        'theme': theme,
        'is_ukraine': country_code == 'UA',
        # CMS дані:
        'cms_hero_slides': hero_slides,
        'cms_experts': experts,
        'main_courses': main_courses,
    }
```

**Термін:** 🔴 КРИТИЧНО — зробити ЗАРАЗ

---

### 🔴 #2 — НЕ ВИКОРИСТОВУЮТЬСЯ МЕТОДИ get_title(), get_subtitle()

**Проблема:** Моделі мають методи для отримання контенту по країні (UA/World), але templates їх НЕ ВИКОРИСТОВУЮТЬ!

**В моделях є:**
```python
# HeroSlide.get_title(country_code='UA')
# HeroSlide.get_subtitle(country_code='UA')
# HeroSlide.get_cta_text(country_code='UA')
```

**В templates:**
```html
<!-- home.html:66 -->
<h1 class="hero-title">{{ first_slide.title }}</h1>
<!-- ❌ НЕ ВИКОРИСТОВУЄ: {{ first_slide.get_title }} -->

<!-- home.html:67 -->
<p class="hero-subtitle">{{ first_slide.subtitle }}</p>
<!-- ❌ НЕ ВИКОРИСТОВУЄ: {{ first_slide.get_subtitle }} -->
```

**ЩО ВІДПАДЕ:**
- Дублювання UA/World версій НЕ працюватиме
- Показуватимуться тільки UA поля (`title_ua`, `subtitle_ua`)
- Для інших країн fallback НЕ спрацює

**РІШЕННЯ:**  
В templates змінити:
```html
<!-- ЗАМІСТЬ: -->
{{ first_slide.title }}
{{ first_slide.subtitle }}
{{ first_slide.cta_text }}

<!-- ВИКОРИСТОВУВАТИ: -->
{{ first_slide.get_title }}
{{ first_slide.get_subtitle }}
{{ first_slide.get_cta_text }}

<!-- АБО з передачею country_code: -->
{% with slide.get_title as title %}
    {{ title }}
{% endwith %}
```

**Термін:** 🟠 ВАЖЛИВО — зробити перед здачею

---

### 🟠 #3 — ДУБЛІ HARDCODE В FALLBACK БЛОКАХ

**Файли:**
- `templates/pages/home.html` (рядки 78-86, 302-397)
- `templates/pages/about.html` (рядки 104-199)
- `templates/pages/mentoring.html` (рядки 141-236)

**Проблема:** Якщо CMS дані НЕ завантажені, показується hardcode fallback. Але це означає що:
1. Адмін додає експерта — НІЧОГО не зміниться (буде показуватися hardcode)
2. Потрібно видалити hardcode fallback після додавання context processor

**РІШЕННЯ:**  
Після виправлення #1, видалити всі `{% else %}` блоки з hardcode:
```html
<!-- ВИДАЛИТИ: -->
{% else %}
<!-- Fallback: Hardcode experts -->
<div class="expert-card">...</div>
{% endif %}

<!-- ЗАЛИШИТИ ТІЛЬКИ: -->
{% if cms_experts %}
    {% for expert in cms_experts %}
        <!-- Expert card -->
    {% endfor %}
{% else %}
    <p>Експерти скоро будуть додані</p>
{% endif %}
```

**Термін:** 🟠 ВАЖЛИВО — після виправлення #1

---

### 🟠 #4 — НЕМАЄ ПЕРЕВІРКИ МІГРАЦІЙ

**Проблема:** В `apps/cms/migrations/` є тільки:
- `0001_initial.py`
- `0006_new_page_models.py`

Але моделі (AboutHero, HubHero, MentorHero...) потребують окремих таблиць!

**Перевірити:**
```bash
python manage.py makemigrations cms
python manage.py migrate cms
```

**Можливі проблеми:**
- Таблиці не створені в базі
- Адмін викине помилку `DoesNotExist`
- Додавання через адмінку НЕ працюватиме

**РІШЕННЯ:**  
1. Запустити `makemigrations`
2. Перевірити що всі таблиці створені
3. Протестувати додавання через адмінку

**Термін:** 🔴 КРИТИЧНО — зробити ЗАРАЗ

---

### 🟡 #5 — НЕМАЄ ОБРОБКИ country_code У get_title()

**Проблема:** Методи `get_title(country_code='UA')` очікують параметр, але в templates передається context `country_code`, який НЕ пробрасується.

**Приклад:**
```python
# Модель:
def get_title(self, country_code='UA'):
    if country_code == 'UA' or not self.title_world:
        return self.title_ua
    return self.title_world
```

**В template:**
```html
<!-- НЕ ПЕРЕДАЄТЬСЯ country_code: -->
{{ slide.get_title }}

<!-- ПОТРІБНО: -->
{{ slide.get_title|call_with:country_code }}
<!-- АБО зробити template tag -->
```

**РІШЕННЯ:**  
Створити template filter:
```python
# apps/cms/templatetags/cms_tags.py

@register.filter
def get_localized_title(obj, country_code):
    """Отримати title з урахуванням країни"""
    if hasattr(obj, 'get_title'):
        return obj.get_title(country_code)
    return getattr(obj, 'title_ua', '')

@register.filter
def get_localized_subtitle(obj, country_code):
    """Отримати subtitle з урахуванням країни"""
    if hasattr(obj, 'get_subtitle'):
        return obj.get_subtitle(country_code)
    return getattr(obj, 'subtitle_ua', '')
```

**В templates:**
```html
{{ slide|get_localized_title:country_code }}
{{ slide|get_localized_subtitle:country_code }}
```

**Термін:** 🟡 СЕРЕДНЬО — зробити перед запуском

---

## 🟡 СЕРЕДНІ ПРОБЛЕМИ (ПОТРІБНО ВИПРАВИТИ)

### 🟡 #6 — НЕМАЄ ОБРОБКИ ВІДСУТНІХ ЗОБРАЖЕНЬ

**Проблема:** Якщо адмін НЕ завантажить зображення, може бути помилка 404.

**Приклад:**
```html
<!-- home.html:33 -->
<img src="{{ first_slide.image.url }}" ...>
<!-- ❌ Якщо image = None → помилка! -->
```

**РІШЕННЯ:**  
Додати перевірку:
```html
{% if first_slide.image %}
    <img src="{{ first_slide.image.url }}" ...>
{% else %}
    <img src="{% static 'images/Hiro.png' %}" ...>
{% endif %}
```

**Термін:** 🟡 СЕРЕДНЬО

---

### 🟡 #7 — НЕМАЄ КЕШУВАННЯ CMS ДАНИХ

**Проблема:** При кожному запиті завантажуються HeroSlide, ExpertCard тощо. Це впливає на продуктивність.

**РІШЕННЯ:**  
Додати кешування в context processor:
```python
from django.core.cache import cache

def site_content(request):
    # ...
    
    # Кешувати hero slides (5 хв)
    hero_slides = cache.get('cms_hero_slides')
    if not hero_slides:
        hero_slides = list(HeroSlide.objects.filter(is_active=True).order_by('order'))
        cache.set('cms_hero_slides', hero_slides, 60*5)
    
    # Кешувати експертів (10 хв)
    experts = cache.get('cms_experts')
    if not experts:
        experts = list(ExpertCard.objects.filter(is_active=True).order_by('order'))
        cache.set('cms_experts', experts, 60*10)
    
    return {
        'cms_hero_slides': hero_slides,
        'cms_experts': experts,
        # ...
    }
```

**Термін:** 🟡 СЕРЕДНЬО — після основних виправлень

---

### 🟡 #8 — НЕМАЄ ВАЛІДАЦІЇ ПОРЯДКУ (order)

**Проблема:** Можна додати 2 слайди з однаковим `order=1`. Це порушить сортування.

**В моделях:**
```python
# FeaturedCourse має unique_together:
unique_together = [('page', 'order'), ('page', 'course')]
# ✅ Добре!

# HeroSlide НЕ має unique order:
order = models.PositiveIntegerField('Order', default=0)
# ❌ Можна додати дублі!
```

**РІШЕННЯ:**  
Додати валідацію в `HeroSlide.save()`:
```python
def clean(self):
    # Перевірити що order унікальний
    if HeroSlide.objects.filter(order=self.order, is_active=True).exclude(pk=self.pk).exists():
        raise ValidationError(f'Слайд з порядком {self.order} вже існує')
```

**Термін:** 🟢 НИЗЬКО — nice to have

---

## 🟢 НИЗЬКІ ПРОБЛЕМИ (ПОКРАЩЕННЯ)

### 🟢 #9 — НЕОПТИМІЗОВАНІ ЗАПИТИ

**Проблема:** ExpertCard завантажується окремим запитом для кожної сторінки.

**РІШЕННЯ:** Використовувати `select_related()` та `prefetch_related()` де потрібно.

**Термін:** 🟢 НИЗЬКО

---

### 🟢 #10 — НЕМАЄ PREVIEW В ADMIN

**Проблема:** Адмін не бачить як виглядатиме слайд/експерт на сайті.

**РІШЕННЯ:** Додати `readonly_fields` з HTML preview в admin.

**Термін:** 🟢 НИЗЬКО — nice to have

---

## 📋 ЧЕКЛИСТ ВИПРАВЛЕНЬ (ОБОВ'ЯЗКОВО)

### Перед здачею проекту:

- [ ] **#1 КРИТИЧНО** — Виправити `context_processors.py` (додати CMS дані)
- [ ] **#2 ВАЖЛИВО** — Використовувати методи `get_title()`, `get_subtitle()` в templates
- [ ] **#3 ВАЖЛИВО** — Видалити hardcode fallback після #1
- [ ] **#4 КРИТИЧНО** — Запустити міграції та протестувати
- [ ] **#5 СЕРЕДНЬО** — Створити template filters для локалізації
- [ ] **#6 СЕРЕДНЬО** — Додати перевірки на відсутні зображення
- [ ] **#7 СЕРЕДНЬО** — Додати кешування

### Тестування після виправлень:

1. ✅ Зайти в Django Admin
2. ✅ Додати HeroSlide через адмінку
3. ✅ Перевірити що слайд показується на головній
4. ✅ Додати ExpertCard
5. ✅ Перевірити що експерт з'являється на 3 сторінках
6. ✅ Додати FeaturedCourse
7. ✅ Перевірити каруселі курсів
8. ✅ Протестувати UA/World fallback (змінити IP)
9. ✅ Протестувати Light/Dark theme (змінити cookie)

---

## 📊 СТАТИСТИКА ПРОБЛЕМ

| Критичність | Кількість | Статус |
|-------------|-----------|--------|
| 🔴 Критичні (Блокери) | 2 | Потрібно виправити ЗАРАЗ |
| 🟠 Важливі | 2 | Виправити перед здачею |
| 🟡 Середні | 5 | Виправити для стабільності |
| 🟢 Низькі | 2 | Nice to have |
| **ВСЬОГО** | **11** | - |

---

## 🎯 ПЛАН ДІЙ (ЧЕРГОВІСТЬ)

### Крок 1: Виправити критичні (30 хв)
1. Виправити `apps/cms/context_processors.py` — додати CMS дані
2. Запустити міграції `python manage.py makemigrations cms && python manage.py migrate`
3. Протестувати додавання через адмінку

### Крок 2: Виправити важливі (1 год)
1. Створити template filters для локалізації
2. Замінити прямі звернення на методи get_*()
3. Видалити hardcode fallback

### Крок 3: Виправити середні (1 год)
1. Додати перевірки зображень
2. Додати кешування
3. Протестувати всі сторінки

### Крок 4: Фінальне тестування (30 хв)
1. Пройти чеклист
2. Протестувати різні сценарії
3. Перевірити продукцію

---

**ЗАГАЛЬНИЙ ЧАС НА ВИПРАВЛЕННЯ:** ~3 години  
**ГОТОВНІСТЬ ДО ЗДАЧІ:** після виправлення пунктів #1-#7


