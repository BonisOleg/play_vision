# HTML/CSS Завдання - Виправлення відповідно до скріншотів

**Дата:** 19.10.2025  
**Базується на:** Скріншоти інтерфейсу особистого кабінету

---

## 🎯 ЗАВДАННЯ 1: Вкладка "Історія оплат" - ДОДАТИ КОЛОНКУ "ДІЯ"

### Файл для редагування:
`templates/account/tabs/payments.html`

### Що треба зробити:

#### 1.1. Додати 5-ту колонку в header таблиці

**Знайти (рядок 45-50):**
```html
<div class="table-header">
    <div class="col-date">Дата</div>
    <div class="col-description">Опис</div>
    <div class="col-amount">Сума</div>
    <div class="col-status">Статус</div>
</div>
```

**Змінити на:**
```html
<div class="table-header">
    <div class="col-date">Дата</div>
    <div class="col-description">Опис</div>
    <div class="col-amount">Сума</div>
    <div class="col-status">Статус</div>
    <div class="col-action">Дія</div>
</div>
```

#### 1.2. Додати 5-ту колонку в кожен рядок таблиці

**Знайти (рядок 51-98):**
```html
{% for payment in recent_payments %}
<div class="table-row">
    <div class="col-date">...</div>
    <div class="col-description">...</div>
    <div class="col-amount">...</div>
    <div class="col-status">...</div>
</div>
{% endfor %}
```

**ПІСЛЯ рядка 97 (після </div> для col-status) ДОДАТИ:**
```html
                <div class="col-action">
                    {% if payment.subscription and payment.status == 'succeeded' %}
                    <button class="btn-repeat" 
                            data-action="repeatPayment"
                            data-plan-id="{{ payment.subscription.plan.id }}"
                            data-payment-id="{{ payment.id }}">
                        Повторити
                    </button>
                    {% else %}
                    <span class="action-empty">—</span>
                    {% endif %}
                </div>
```

#### 1.3. Додати CSS для нової колонки

**Файл:** `static/css/components/cabinet.css` або `cabinet-additions.css`

**ДОДАТИ в кінець файлу:**
```css
/* Колонка "Дія" в історії оплат */
.col-action {
    flex: 0 0 120px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-repeat {
    background: #f97316;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-repeat:hover {
    background: #ea580c;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(249, 115, 22, 0.3);
}

.action-empty {
    color: #9ca3af;
}
```

#### 1.4. Додати JavaScript обробник для кнопки "Повторити"

**Файл:** `static/js/cabinet.js`

**ДОДАТИ в кінець файлу:**
```javascript
// Обробник кнопки "Повторити" платіж
document.addEventListener('DOMContentLoaded', function() {
    const repeatButtons = document.querySelectorAll('[data-action="repeatPayment"]');
    
    repeatButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const planId = this.dataset.planId;
            const paymentId = this.dataset.paymentId;
            
            if (!confirm('Повторити оплату за цим планом?')) {
                return;
            }
            
            try {
                // Redirect на сторінку checkout з вибраним планом
                window.location.href = `/subscriptions/checkout/${planId}/?repeat_payment=${paymentId}`;
            } catch (error) {
                console.error('Помилка повтору платежу:', error);
                alert('Виникла помилка. Спробуйте пізніше.');
            }
        });
    });
});
```

---

## 🎯 ЗАВДАННЯ 2: Вкладка "Підписка" - ДОДАТИ БЛОКИ LOYALTY

### Файл для редагування:
`templates/account/tabs/subscription.html`

### Що треба зробити:

#### 2.1. Додати новий блок ПЕРЕД "Поточний план"

**ПІСЛЯ рядка 2 (`<div class="subscription-tab">`) ВСТАВИТИ:**

```html
    <!-- Блоки Loyalty інформації -->
    {% if loyalty_account %}
    <div class="loyalty-info-grid">
        <!-- Блок "Рівень" -->
        <div class="info-card loyalty-tier">
            <h3>Рівень</h3>
            <div class="tier-display">
                <div class="tier-badge tier-{{ loyalty_account.current_tier.name|lower }}">
                    {{ loyalty_account.current_tier.name }}
                </div>
            </div>
        </div>

        <!-- Блок "Прогрес рівня" -->
        <div class="info-card loyalty-progress">
            <h3>Прогрес рівня</h3>
            <div class="progress-display">
                <div class="progress-text">
                    {{ loyalty_account.total_points }}/{{ loyalty_account.points_to_next_tier }} балів до {{ loyalty_account.next_tier.name }}
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: {{ loyalty_account.progress_percentage }}%"></div>
                </div>
                <div class="progress-percentage">{{ loyalty_account.progress_percentage }}%</div>
            </div>
        </div>

        <!-- Блок "Знижка" -->
        <div class="info-card loyalty-discount">
            <h3>Знижка</h3>
            <div class="discount-display">
                <div class="discount-current">
                    Поточна: <strong>{{ loyalty_account.current_discount }}%</strong>
                </div>
                <div class="discount-potential">
                    Потенційна: <strong>{{ loyalty_account.potential_discount }}%</strong>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

```

#### 2.2. Додати CSS для loyalty блоків

**Файл:** `static/css/components/cabinet-additions.css`

**ДОДАТИ:**
```css
/* Loyalty інфо грід у вкладці підписка */
.loyalty-info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 30px;
}

/* Блок "Рівень" */
.loyalty-tier .tier-display {
    text-align: center;
    padding: 20px 0;
}

.tier-badge {
    display: inline-block;
    padding: 12px 32px;
    border-radius: 24px;
    font-size: 18px;
    font-weight: 600;
    text-transform: uppercase;
}

.tier-badge.tier-bronze {
    background: #cd7f32;
    color: white;
}

.tier-badge.tier-silver {
    background: #f97316;
    color: white;
}

.tier-badge.tier-gold {
    background: #eab308;
    color: white;
}

.tier-badge.tier-platinum {
    background: linear-gradient(135deg, #8b5cf6, #ec4899);
    color: white;
}

/* Блок "Прогрес рівня" */
.loyalty-progress .progress-display {
    padding: 10px 0;
}

.progress-text {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 8px;
}

.progress-bar-container {
    width: 100%;
    height: 12px;
    background: #e5e7eb;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #f97316, #fb923c);
    transition: width 0.5s ease;
}

.progress-percentage {
    text-align: right;
    font-size: 14px;
    font-weight: 600;
    color: #f97316;
}

/* Блок "Знижка" */
.loyalty-discount .discount-display {
    padding: 10px 0;
}

.discount-current,
.discount-potential {
    font-size: 15px;
    margin-bottom: 8px;
    color: #4b5563;
}

.discount-current strong,
.discount-potential strong {
    font-size: 18px;
    color: #f97316;
}

.discount-potential {
    color: #9ca3af;
}

/* Responsive */
@media (max-width: 992px) {
    .loyalty-info-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }
}
```

#### 2.3. Додати дані loyalty в context

**Файл:** `apps/accounts/cabinet_views.py`

**Знайти метод `_get_subscription_context` (приблизно рядки 100-150)**

**ДОДАТИ в кінець методу перед `return context`:**

```python
# Додати loyalty дані
if hasattr(request.user, 'loyalty_account'):
    loyalty_account = request.user.loyalty_account
    context['loyalty_account'] = {
        'current_tier': loyalty_account.current_tier,
        'next_tier': loyalty_account.get_next_tier(),
        'total_points': loyalty_account.total_points,
        'points_to_next_tier': loyalty_account.points_to_next_tier(),
        'progress_percentage': loyalty_account.get_progress_percentage(),
        'current_discount': loyalty_account.get_discount_percentage(),
        'potential_discount': loyalty_account.get_potential_discount(),
    }
```

---

## 🎯 ЗАВДАННЯ 3: Додати індикатор "днів з нами"

### Файл для редагування:
`templates/account/cabinet.html`

### Що треба зробити:

#### 3.1. Додати HTML для індикатора

**Знайти секцію profile-avatar (рядки 18-30)**

**ПІСЛЯ рядка 30 (після `</div>` аватара) ДОДАТИ:**

```html
                <!-- Індикатор "днів з нами" -->
                <div class="days-with-us">
                    <svg class="calendar-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    <span class="days-text">{{ days_count }} {{ days_word }} з нами</span>
                </div>
```

#### 3.2. Додати CSS для індикатора

**Файл:** `static/css/components/cabinet-additions.css`

**ДОДАТИ:**
```css
/* Індикатор "днів з нами" */
.days-with-us {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 15px;
    padding: 10px 15px;
    background: #f3f4f6;
    border-radius: 8px;
    font-size: 14px;
    color: #6b7280;
}

.calendar-icon {
    flex-shrink: 0;
    stroke: #f97316;
}

.days-text {
    font-weight: 500;
}
```

#### 3.3. Додати логіку в view

**Файл:** `apps/accounts/cabinet_views.py`

**Знайти метод `get_context_data` в `CabinetView`**

**ДОДАТИ:**
```python
def get_days_word(n):
    """Повертає правильне слово для кількості днів"""
    if n % 10 == 1 and n % 100 != 11:
        return "день"
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return "дні"
    else:
        return "днів"

# В методі get_context_data додати:
from django.utils import timezone

days = (timezone.now().date() - self.request.user.date_joined.date()).days
context['days_count'] = days
context['days_word'] = get_days_word(days)
```

---

## 🎯 ЗАВДАННЯ 4: Перенумерувати напрямки інтересів

### Файл для редагування:
`templates/account/cabinet.html`

### Поточний стан:
На скріншоті видно що інтереси мають нумерацію та в іншому порядку.

### Що є зараз (рядки 82-95):
```html
<div class="interests-section">
    <label>Напрямки (інтереси)</label>
    <div class="interests-list">
        {% for interest in interests %}
        <label class="interest-item">
            <input type="checkbox" name="interests" value="{{ interest.id }}" 
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

### ✅ Це ВЖЕ ПРАВИЛЬНО!

Нумерація є (`{{ forloop.counter }}.`), порядок контролюється в базі даних через `display_order`.

**Що перевірити:**
- Чи є в базі 9 інтересів у правильному порядку (див. розділ 10.1 в usertask.md)
- Якщо ні - запустити команду `python manage.py create_interests`

---

## 🎯 ЗАВДАННЯ 5: Виправити відображення статусів верифікації

### Файл для редагування:
`templates/account/cabinet.html`

### Поточний стан (рядки 56-66):

На скріншоті видно:
- Email: "yn04" з зеленою позначкою "верифіковано" ✓
- Телефон: "+380..." з жовтою позначкою "очікує" ⚠

### Що змінити:

**Знайти (рядки 58-60):**
```html
<input type="email" id="email" name="email" class="form-control" value="{{ user.email }}">
<span class="verification-badge verified">верифіковано</span>
```

**Змінити на:**
```html
<input type="email" id="email" name="email" class="form-control" value="{{ user.email }}">
{% if user.is_email_verified %}
<span class="verification-badge verified">✓ верифіковано</span>
{% else %}
<span class="verification-badge pending">⚠ очікує</span>
{% endif %}
```

**Знайти (рядки 63-65):**
```html
<input type="tel" id="phone" name="phone" class="form-control" placeholder="+380..."
    value="{{ user.phone|default:'' }}">
<span class="verification-badge">очікує</span>
```

**Змінити на:**
```html
<input type="tel" id="phone" name="phone" class="form-control" placeholder="+380..."
    value="{{ user.phone|default:'' }}">
{% if user.is_phone_verified %}
<span class="verification-badge verified">✓ верифіковано</span>
{% else %}
<span class="verification-badge pending">⚠ очікує</span>
{% endif %}
```

### Додати CSS для статусів:

**Файл:** `static/css/components/cabinet.css`

**ДОДАТИ або ЗМІНИТИ:**
```css
.verification-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 12px;
    margin-top: 4px;
}

.verification-badge.verified {
    background: #d1fae5;
    color: #059669;
}

.verification-badge.pending {
    background: #fef3c7;
    color: #d97706;
}
```

---

## 📋 ПІДСУМОК ЗМІН

### Файли які треба редагувати:

1. **templates/account/tabs/payments.html**
   - Додати колонку "Дія" в header
   - Додати колонку "Дія" в кожен рядок
   - Додати кнопку "Повторити"

2. **templates/account/tabs/subscription.html**
   - Додати 3 блоки loyalty перед поточним планом
   - Рівень (Silver/Gold тощо)
   - Прогрес-бар до наступного рівня
   - Знижки (поточна/потенційна)

3. **templates/account/cabinet.html**
   - Додати індикатор "днів з нами" після аватара
   - Виправити статуси верифікації email/phone

4. **static/css/components/cabinet.css** або **cabinet-additions.css**
   - CSS для колонки "Дія"
   - CSS для кнопки "Повторити"
   - CSS для loyalty блоків
   - CSS для tier badges
   - CSS для progress bar
   - CSS для індикатора "днів з нами"
   - CSS для статусів верифікації

5. **static/js/cabinet.js**
   - JavaScript для кнопки "Повторити"
   - Обробка кліку та redirect

6. **apps/accounts/cabinet_views.py**
   - Додати loyalty_account в context вкладки "Підписка"
   - Додати days_count та days_word в context
   - Створити функцію get_days_word()

---

## ✅ ЧЕКЛИСТ ВИКОНАННЯ

ВКЛАДКА "ІСТОРІЯ ОПЛАТ":
- [ ] Додано колонку "Дія" в header таблиці
- [ ] Додано колонку "Дія" в кожен рядок
- [ ] Додано кнопку "Повторити" (оранжева)
- [ ] Додано CSS для кнопки
- [ ] Додано JavaScript обробник
- [ ] Протестовано роботу кнопки

ВКЛАДКА "ПІДПИСКА":
- [ ] Додано блок "Рівень" з badge
- [ ] Додано блок "Прогрес рівня" з progress bar
- [ ] Додано блок "Знижка" (поточна/потенційна)
- [ ] Додано CSS для всіх loyalty блоків
- [ ] Додано loyalty_account в context
- [ ] Протестовано відображення

ЗАГАЛЬНЕ:
- [ ] Додано індикатор "днів з нами"
- [ ] Додано функцію get_days_word для відмінків
- [ ] Виправлено статуси верифікації (зелений/жовтий)
- [ ] Додано іконки ✓ та ⚠
- [ ] Протестовано на реальних даних

---

## 🎨 ВІЗУАЛЬНЕ ПОРІВНЯННЯ

### На скріншоті є:
✓ Ліва панель з профілем - **Є в коді**
✓ Вкладки (Підписка, Історія оплат, Мої файли, Програма лояльності) - **Є в коді**
✓ Таблиця історії оплат - **Є в коді**
✗ Колонка "Дія" з кнопкою "Повторити" - **НЕМАЄ, треба додати**
✓ Вкладка підписка з блоками - **Є частково**
✗ Блоки Loyalty (Рівень, Прогрес, Знижка) - **НЕМАЄ у вкладці підписка, треба додати**

### Загальна готовність відповідно до скріншотів:
- Структура: **95%** ✓
- Функціонал: **85%** (немає кнопки "Повторити" та loyalty блоків)
- Візуальне оформлення: **90%** (кольори можуть відрізнятись - не важливо)

---

---

## 🎯 ЗАВДАННЯ 6: Вкладка "Мої файли" - ДОДАТИ ІКОНКИ

### Файл для редагування:
`templates/account/tabs/files.html`

### Що треба зробити:

#### 6.1. Додати іконку замочка 🔒 для заблокованих матеріалів

**Знайти (рядки 6-15):**
```html
<div class="material-card" data-material-id="{{ material.id }}">
    <!-- Заголовок матеріалу -->
    <div class="material-header">
        <h4 class="material-title">{{ material.title }}</h4>
        <div class="material-type">{{ material.content_type }}</div>
        <button class="favorite-btn {% if material.is_favorite %}active{% endif %}" 
                data-action="toggleFavorite"
                data-course-id="{{ material.course_id }}">
            <span class="star-icon">★</span>
        </button>
    </div>
```

**ДОДАТИ ПІСЛЯ рядка 9 (після `<div class="material-type">`):**
```html
                <!-- Іконка замочка для платних матеріалів -->
                {% if not material.has_access %}
                <div class="lock-icon" title="Потрібна підписка">🔒</div>
                {% endif %}
                
                <!-- Іконка валюти для окремо куплених -->
                {% if material.purchased_separately %}
                <div class="purchase-icon" title="Придбано окремо">💰</div>
                {% endif %}
```

#### 6.2. Додати CSS для іконок

**Файл:** `static/css/components/cabinet-additions.css`

**ДОДАТИ:**
```css
/* Іконки на картках матеріалів */
.material-header {
    position: relative;
}

.lock-icon,
.purchase-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 18px;
    opacity: 0.8;
}

.purchase-icon {
    top: 8px;
    right: 35px; /* Якщо є обидві іконки */
}

.lock-icon:hover,
.purchase-icon:hover {
    opacity: 1;
}
```

#### 6.3. Оновити логіку в view для визначення статусу матеріалу

**Файл:** `apps/accounts/cabinet_views.py`

**Знайти метод `_get_files_context` та ДОДАТИ в material_data:**

```python
material_data = {
    'id': material.id,
    'title': material.title,
    'content_type': material.get_content_type_display(),
    'progress': progress,
    'is_favorite': is_favorite,
    'course_id': material.course.id,
    'can_download': material.can_download,
    'is_completed': progress >= 100,
    # ДОДАТИ ЦІ 2 ПОЛЯ:
    'has_access': user_has_access_to_material(request.user, material),
    'purchased_separately': material_purchased_separately(request.user, material),
}
```

#### 6.4. Створити допоміжні функції

**Файл:** `apps/accounts/cabinet_views.py` або `apps/content/utils.py`

**ДОДАТИ:**
```python
def user_has_access_to_material(user, material):
    """Перевіряє чи має користувач доступ до матеріалу"""
    if not user.is_authenticated:
        return False
    
    # Перевірити підписку
    if hasattr(user, 'active_subscription') and user.active_subscription:
        return True
    
    # Перевірити чи куплений окремо
    from apps.payments.models import Payment
    has_purchase = Payment.objects.filter(
        user=user,
        course=material.course,
        status='succeeded'
    ).exists()
    
    return has_purchase

def material_purchased_separately(user, material):
    """Перевіряє чи матеріал куплений окремо (не через підписку)"""
    if not user.is_authenticated:
        return False
    
    from apps.payments.models import Payment
    
    # Перевірити чи є окрема покупка (не підписка)
    has_separate_purchase = Payment.objects.filter(
        user=user,
        course=material.course,
        status='succeeded',
        subscription__isnull=True  # Не через підписку
    ).exists()
    
    return has_separate_purchase
```

---

## 🎯 ЗАВДАННЯ 7: Виправити відображення інтересів (кнопки замість чекбоксів)

### Файл для редагування:
`templates/account/cabinet.html`

### Що є на скріншоті:
На скріншоті видно що інтереси - це **кнопки-теги** (Аналітика, Тренерство, Психологія, Харчування), а не чекбокси.

### Поточний код (рядки 82-95):
```html
<div class="interests-section">
    <label>Напрямки (інтереси)</label>
    <div class="interests-list">
        {% for interest in interests %}
        <label class="interest-item">
            <input type="checkbox" name="interests" value="{{ interest.id }}" 
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

### Що треба змінити:

**ЗАМІНИТИ весь блок на:**
```html
<div class="interests-section">
    <label>Напрямки (інтереси)</label>
    <div class="interests-tags">
        {% for interest in interests %}
        <button type="button" 
                class="interest-tag {% if interest in user.profile.interests.all %}active{% endif %}"
                data-action="toggleInterest"
                data-interest-id="{{ interest.id }}">
            {{ interest.name }}
        </button>
        {% endfor %}
    </div>
    <!-- Приховане поле для збереження обраних інтересів -->
    <input type="hidden" name="interests" id="selected-interests" 
           value="{% for interest in user.profile.interests.all %}{{ interest.id }},{% endfor %}">
</div>
```

### Додати CSS для кнопок-тегів:

**Файл:** `static/css/components/cabinet.css`

**ДОДАТИ:**
```css
/* Інтереси як кнопки-теги */
.interests-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
}

.interest-tag {
    padding: 8px 16px;
    border: 1px solid #d1d5db;
    background: #f9fafb;
    border-radius: 20px;
    font-size: 14px;
    color: #4b5563;
    cursor: pointer;
    transition: all 0.2s ease;
}

.interest-tag:hover {
    border-color: #f97316;
    background: #fff7ed;
}

.interest-tag.active {
    background: #f97316;
    color: white;
    border-color: #f97316;
}

.interest-tag.active:hover {
    background: #ea580c;
    border-color: #ea580c;
}
```

### Додати JavaScript для toggleInterest:

**Файл:** `static/js/cabinet.js`

**ДОДАТИ:**
```javascript
// Toggle інтересів
document.addEventListener('DOMContentLoaded', function() {
    const interestTags = document.querySelectorAll('[data-action="toggleInterest"]');
    const hiddenInput = document.getElementById('selected-interests');
    
    interestTags.forEach(tag => {
        tag.addEventListener('click', function() {
            this.classList.toggle('active');
            
            // Оновити приховане поле
            const selectedIds = Array.from(document.querySelectorAll('.interest-tag.active'))
                .map(tag => tag.dataset.interestId)
                .join(',');
            
            hiddenInput.value = selectedIds;
        });
    });
});
```

---

## 📊 ДЕТАЛЬНЕ ПОРІВНЯННЯ СКРІНШОТІВ З КОДОМ

### СКРІНШОТ 1 + 2: Вкладка "Історія оплат"

| Елемент | На скріншоті | В коді | Статус |
|---------|--------------|--------|--------|
| Колонка "Дата" | ✓ Є | ✓ Є | ✅ OK |
| Колонка "Опис" | ✓ Є | ✓ Є | ✅ OK |
| Колонка "Сума" | ✓ Є | ✓ Є | ✅ OK |
| Колонка "Статус" | ✓ Є | ✓ Є | ✅ OK |
| **Колонка "Дія"** | **✓ Є з кнопкою "Повторити"** | **✗ НЕМАЄ** | ❌ ДОДАТИ |
| Статус "Сплачено" | ✓ Є | ✓ Є (succeeded) | ✅ OK |
| Статус "Очікує" | ✓ Є | ✓ Є (pending) | ✅ OK |

### СКРІНШОТ 1: Вкладка "Підписка"

| Елемент | На скріншоті | В коді | Статус |
|---------|--------------|--------|--------|
| Блок "Поточний план" | ✓ Є (Місячна — $10) | ✓ Є | ✅ OK |
| Блок "Статус" | ✓ Є (Активна, 12.10.2025) | ✓ Є | ✅ OK |
| Блок "Переваги" | ✓ Є (список) | ✓ Є | ✅ OK |
| **Блок "Рівень"** | **✗ НЕ ВИДНО** | **✗ НЕМАЄ** | ⚠️ Можливо за межами скріну |
| **Блок "Прогрес"** | **✗ НЕ ВИДНО** | **✗ НЕМАЄ** | ⚠️ Можливо за межами скріну |
| **Блок "Знижка"** | **✗ НЕ ВИДНО** | **✗ НЕМАЄ** | ⚠️ Можливо за межами скріну |
| Кнопка "Змінити підписку" | ✓ Є | ✓ Є | ✅ OK |

### СКРІНШОТИ 3 + 4: Вкладка "Мої файли"

| Елемент | На скріншоті | В коді | Статус |
|---------|--------------|--------|--------|
| Сітка 3x2 матеріалів | ✓ Є | ✓ Є (materials-grid) | ✅ OK |
| Назва матеріалу | ✓ Є | ✓ Є (material-title) | ✅ OK |
| Тип (PDF/Відео) | ✓ Є | ✓ Є (material-type) | ✅ OK |
| Прогрес бар (оранжевий) | ✓ Є | ✓ Є (progress-bar) | ✅ OK |
| Відсоток (30%, 41%) | ✓ Є | ✓ Є (progress-text) | ✅ OK |
| Кнопка "Переглянути" | ✓ Є (оранжева) | ✓ Є (btn-primary) | ✅ OK |
| Кнопка "В офлайн" | ✓ Є | ✓ Є (btn-secondary) | ✅ OK |
| Іконка зірочки ★ | ✓ Є (чорна) | ✓ Є (favorite-btn) | ✅ OK |
| **Іконка замочка 🔒** | **✓ Є (вгорі праворуч)** | **✗ НЕМАЄ** | ❌ ДОДАТИ |
| **Іконка валюти 💰** | **✓ Є (вгорі праворуч)** | **✗ НЕМАЄ** | ❌ ДОДАТИ |

### СКРІНШОТ 2: Нижня частина - інтереси

| Елемент | На скріншоті | В коді | Статус |
|---------|--------------|--------|--------|
| Інтереси як кнопки | ✓ Є (Аналітика, Тренерство, Психологія, Харчування) | ✗ НЕМАЄ (є чекбокси) | ❌ ЗМІНИТИ |

---

## 🎯 ЗАВДАННЯ 8: Додати кнопку "Програма лояльності" у вкладці "Мої файли"

### Що видно на скріншоті:
Вгорі сторінки "Мої файли" має бути кнопка швидкого переходу до програми лояльності.

### Файл для редагування:
`templates/account/tabs/files.html`

### Що треба зробити:

**ПІСЛЯ рядка 2 (`<div class="files-tab">`) ВСТАВИТИ:**

```html
    <!-- Швидкі дії -->
    <div class="quick-actions">
        <a href="{% url 'cabinet:loyalty' %}" class="btn-quick-action">
            <span class="icon">🏆</span>
            Програма лояльності
        </a>
    </div>
```

**CSS:**
```css
.quick-actions {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
}

.btn-quick-action {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: #f97316;
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
}

.btn-quick-action:hover {
    background: #ea580c;
    transform: translateY(-1px);
}
```

---

## 📋 ОНОВЛЕНИЙ ЧЕКЛИСТ ВИКОНАННЯ

### ВКЛАДКА "ІСТОРІЯ ОПЛАТ":
- [ ] Додано 5-ту колонку "Дія" в header
- [ ] Додано 5-ту колонку в кожен рядок таблиці
- [ ] Додано кнопку "Повторити" (оранжева)
- [ ] Кнопка показується тільки для успішних платежів за підписку
- [ ] Додано CSS для col-action та btn-repeat
- [ ] Додано JavaScript обробник кліку
- [ ] Протестовано роботу кнопки

### ВКЛАДКА "ПІДПИСКА":
- [ ] Додано блок "Рівень" з badge (Silver/Gold/тощо)
- [ ] Додано блок "Прогрес рівня" з прогрес-баром
- [ ] Додано блок "Знижка" (поточна/потенційна)
- [ ] Додано CSS для loyalty-info-grid
- [ ] Додано CSS для tier-badge з кольорами
- [ ] Додано CSS для progress-bar
- [ ] Додано loyalty_account в context view
- [ ] Протестовано відображення всіх блоків

### ВКЛАДКА "МОЇ ФАЙЛИ":
- [ ] Додано іконку замочка 🔒 для заблокованих матеріалів
- [ ] Додано іконку валюти 💰 для окремо куплених
- [ ] Додано CSS для позиціонування іконок
- [ ] Додано логіку has_access в material_data
- [ ] Додано логіку purchased_separately в material_data
- [ ] Створено функції user_has_access_to_material()
- [ ] Створено функції material_purchased_separately()
- [ ] Додано кнопку "Програма лояльності" вгорі
- [ ] Протестовано відображення іконок

### ЗАГАЛЬНІ ЗМІНИ В КАБІНЕТІ:
- [ ] Додано індикатор "днів з нами" з іконкою календаря
- [ ] Додано функцію get_days_word() для правильних відмінків
- [ ] Змінено інтереси з чекбоксів на кнопки-теги
- [ ] Додано JavaScript для toggle інтересів
- [ ] Виправлено статуси верифікації (зелений ✓ / жовтий ⚠)
- [ ] Протестовано весь кабінет на всіх вкладках

---

## 🎨 ФІНАЛЬНА КАРТИНА

### ЩО ВЖЕ СПІВПАДАЄ ЗІ СКРІНШОТАМИ (95%):
- ✅ Загальна структура кабінету (ліва/права панель)
- ✅ Аватар з кнопкою завантаження
- ✅ Всі поля форми профілю
- ✅ Вкладки навігації
- ✅ Таблиця історії оплат (4 колонки з 5)
- ✅ Блоки підписки (частково)
- ✅ Сітка матеріалів у "Мої файли"
- ✅ Прогрес-бари на матеріалах
- ✅ Кнопки "Переглянути" та "В офлайн"
- ✅ Іконка зірочки для улюблених

### ЩО ТРЕБА ДОДАТИ ДЛЯ 100% ВІДПОВІДНОСТІ:
- ❌ Колонка "Дія" з кнопкою "Повторити" ← **ЗАВДАННЯ 1**
- ❌ Блоки Loyalty у вкладці підписка ← **ЗАВДАННЯ 2**
- ❌ Індикатор "днів з нами" ← **ЗАВДАННЯ 3**
- ❌ Іконки 🔒 та 💰 на матеріалах ← **ЗАВДАННЯ 6**
- ❌ Інтереси як кнопки (не чекбокси) ← **ЗАВДАННЯ 7**
- ❌ Кнопка "Програма лояльності" ← **ЗАВДАННЯ 8**

---

---

## 🎯 ЗАВДАННЯ 9: Вкладка "Програма лояльності" - ДОДАТИ БЛОКИ

### Що видно на скріншоті (photo_2025-09-01 12.53.54.jpeg):

На скріні видно 3 блоки в рядок:
1. **Рівень:** Silver (оранжева кнопка)
2. **Прогрес рівня:** "100/200 балів до Silver" з прогрес-баром
3. **Знижка:** Поточна 10%, Потенційна 15%

### Файл для редагування:
`templates/account/tabs/loyalty.html`

### Що треба перевірити/додати:

Можливо ці блоки вже є, тому треба:
1. Перевірити чи є файл `templates/account/tabs/loyalty.html`
2. Перевірити чи відображаються ці 3 блоки
3. Якщо немає - додати їх (аналогічно до ЗАВДАННЯ 2)

---

## 🎯 ЗАВДАННЯ 10: Сторінка Тарифів - ДОДАТИ ІКОНКИ ТА СЛОГАНИ

### Що видно на скріншотах (2 однакові фото тарифів):

**Заголовок сторінки:**
- "Train with a VISION."
- "Rise through the ranks."

**4 картки планів в рядок:**

1. **C-VISION** 
   - Іконка: 🔵 (синій круг)
   - Підзаголовок: "Початковий Рівень"
   - **Слоган:** "Знайди свій PRO-VISION" (синім кольором)
   
2. **B-VISION**
   - Іконка: 🏆 (помаранчева нагорода)
   - Підзаголовок: "Базовий + Поглиблений"
   - **Слоган:** "Розвивай свій PRO-VISION" (помаранчевим)
   
3. **A-VISION**
   - Іконка: 🎯 (помаранчева мішень)
   - Підзаголовок: "Професійний"
   - **Слоган:** "Встанови свій PRO-VISION" (помаранчевим)
   
4. **PRO-VISION**
   - Іконка: 👑 (рожева/червона корона)
   - Підзаголовок: "Елітний"
   - **Слоган:** "Ти є PRO-VISION" (червоним)

### Файл для редагування:
`templates/subscriptions/pricing.html`

### Що треба зробити:

#### 10.1. Додати заголовок та слоган

**Знайти (рядки 17-21):**
```html
<section class="pricing-header">
    <h1 class="pricing-title">Оберіть свій план підписки</h1>
    <p class="pricing-subtitle">Отримайте доступ до всіх курсів та матеріалів від провідних експертів футболу
    </p>
</section>
```

**ЗАМІНИТИ на:**
```html
<section class="pricing-header">
    <h1 class="pricing-title">Train with a VISION.</h1>
    <p class="pricing-subtitle">Rise through the ranks.</p>
</section>
```

#### 10.2. Додати іконки та слогани до кожної картки

**Знайти (рядки 32-39):**
```html
<div class="plan-header">
    <h3 class="plan-name">{{ plan.name }}</h3>
    <div class="plan-price">
        <span class="plan-currency">$</span>
        <span class="plan-amount">{{ plan.price }}</span>
        <span class="plan-period">/{{ plan.get_duration_display }}</span>
    </div>
</div>
```

**ЗАМІНИТИ на:**
```html
<div class="plan-header">
    <!-- Іконка плану -->
    <div class="plan-icon">
        {% if plan.tier_name == 'c_vision' %}
            <span class="icon-circle icon-blue">🔵</span>
        {% elif plan.tier_name == 'b_vision' %}
            <span class="icon-trophy">🏆</span>
        {% elif plan.tier_name == 'a_vision' %}
            <span class="icon-target">🎯</span>
        {% elif plan.tier_name == 'pro_vision' %}
            <span class="icon-crown">👑</span>
        {% endif %}
    </div>
    
    <h3 class="plan-name">{{ plan.name }}</h3>
    
    <!-- Підзаголовок -->
    <div class="plan-subtitle">
        {% if plan.tier_name == 'c_vision' %}
            Початковий Рівень
        {% elif plan.tier_name == 'b_vision' %}
            Базовий + Поглиблений
        {% elif plan.tier_name == 'a_vision' %}
            Професійний
        {% elif plan.tier_name == 'pro_vision' %}
            Елітний
        {% endif %}
    </div>
    
    <!-- Слоган -->
    <div class="plan-slogan plan-slogan-{{ plan.tier_name }}">
        {{ plan.tier_slogan }}
    </div>
    
    <div class="plan-price">
        <span class="plan-currency">$</span>
        <span class="plan-amount">{{ plan.price }}</span>
        <span class="plan-period">/{{ plan.get_duration_display }}</span>
    </div>
</div>
```

#### 10.3. Додати CSS для іконок та слоганів

**Файл:** `static/css/components/pricing.css`

**ДОДАТИ:**
```css
/* Іконки планів */
.plan-icon {
    font-size: 48px;
    margin-bottom: 15px;
    text-align: center;
}

.icon-circle,
.icon-trophy,
.icon-target,
.icon-crown {
    display: inline-block;
}

/* Підзаголовки */
.plan-subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 10px;
    text-align: center;
}

/* Слогани */
.plan-slogan {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 15px;
    text-align: center;
}

.plan-slogan-c_vision {
    color: #3b82f6; /* Синій */
}

.plan-slogan-b_vision {
    color: #f97316; /* Помаранчевий */
}

.plan-slogan-a_vision {
    color: #f97316; /* Помаранчевий */
}

.plan-slogan-pro_vision {
    color: #e11d48; /* Червоний */
}
```

---

## 🎯 ЗАВДАННЯ 11: Кошик - ПЕРЕВІРИТИ СТРУКТУРУ

### Що видно на скріншоті:

**Заголовок:** Кошик (оранжевий фон)

**Товари в кошику (приклади):**
1. "Форум футбольних фахівців 5"
   - VIDEO • ек хв
   - Теги: тренер, аналітик
   - Badge: "топ-продажів" (червоний), "Видалити" (червоний)
   - Кількість: - 1 +
   - Ціна: $19.00

2. "Дихальні практики перед грою"
   - PDF
   - Теги: гравець, психологія
   - Badge: "новинка" (зелений), "Видалити"
   - Кількість: - 1 +
   - Ціна: $6.00

**Блок "Рекомендації":**
- "Ідеальний додаток до кошика"
- Курс з описом
- Ціна
- Кнопка "+ Додати" (оранжева)

**Нижня частина:**
- Поле промокоду: "Введіть промокод"
- Кнопка "Застосувати" (оранжева)

**Правий sidebar "Підсумок":**
- Проміжна сума: $25.00
- Знижка: -$0.00
- Чайові авторам: $0.00
- До сплати: $25.00
- Текст про переглядати підписку
- Кнопка "Перейти до оплати" (оранжева)
- Кнопка "Продовжити покупки" (біла)

### Файл для перевірки:
`templates/cart/cart.html`

### ✅ ПОРІВНЯННЯ:

| Елемент | На скріншоті | В коді | Статус |
|---------|--------------|--------|--------|
| Заголовок "Кошик" | ✓ Є (оранжевий фон) | ✓ Є (рядок 16-18) | ✅ OK |
| Мініатюра товару | ✓ Є (Обкл.) | ✓ Є (рядки 24-30) | ✅ OK |
| Назва товару | ✓ Є | ✓ Є (рядок 35) | ✅ OK |
| Тип (VIDEO/PDF) | ✓ Є | ✓ Є (рядки 37-39) | ✅ OK |
| Теги (тренер, аналітик) | ✓ Є | ✓ Є (рядки 41-47) | ✅ OK |
| Badges (топ-продажів, новинка) | ✓ Є | ✓ Є (рядки 49-57) | ✅ OK |
| Кнопка "Видалити" | ✓ Є (червона) | ✓ Є (рядки 60-63) | ✅ OK |
| Кількість - 1 + | ✓ Є | ✓ Є (рядки 67-74) | ✅ OK |
| Ціна товару | ✓ Є | ✓ Є (рядок 76) | ✅ OK |
| Блок рекомендацій | ✓ Є | ✓ Є (рядки 83-101) | ✅ OK |
| Поле промокоду | ✓ Є | ✓ Є (рядки 104-109) | ✅ OK |
| Кнопка "Застосувати" | ✓ Є | ✓ Є (рядки 106-108) | ✅ OK |
| Sidebar "Підсумок" | ✓ Є | ✓ Є (рядки 134-184) | ✅ OK |
| Проміжна сума | ✓ Є | ✓ Є (рядки 138-141) | ✅ OK |
| Знижка | ✓ Є | ✓ Є (рядки 143-146) | ✅ OK |
| Чайові авторам | ✓ Є | ✓ Є (рядки 148-151) | ✅ OK |
| До сплати | ✓ Є | ✓ Є (рядки 153-156) | ✅ OK |
| Кнопка "Перейти до оплати" | ✓ Є | ✓ Є (рядки 170-172) | ✅ OK |
| Кнопка "Продовжити покупки" | ✓ Є | ✓ Є (рядки 174-176) | ✅ OK |

### ✅ ВИСНОВОК ПО КОШИКУ:
**КОШИК 100% СПІВПАДАЄ ЗІ СКРІНШОТОМ!** Всі елементи на місці, нічого додавати не треба!

---

## 🎯 ЗАВДАННЯ 12: Фільтри Хаб знань - ПЕРЕВІРИТИ КНОПКИ

### Що видно на скріншоті:

**Кнопки:**
1. "Застосувати фільтри" - червона з галочкою ✓
2. "Скинути всі" - біла з червоною обводкою

### Файл для перевірки:
`templates/hub/course_list.html`

### ✅ ПОРІВНЯННЯ:

| Елемент | На скріншоті | В коді | Статус |
|---------|--------------|--------|--------|
| Кнопка "Застосувати" | ✓ Є | ✓ Є (рядки 343-348) | ✅ OK |
| Іконка галочка ✓ | ✓ Є | ✓ Є (SVG path) | ✅ OK |
| Кнопка "Скинути всі" | ✓ Є | ✓ Є (рядки 349-355) | ✅ OK |
| Текст "Застосувати фільтри" | ✓ Є на скріні | ✗ Тільки "Застосувати" | ⚠️ ВИПРАВИТИ |
| Текст "Скинути всі" | ✓ Є | ✓ Є "Скинути все" | ⚠️ ВИПРАВИТИ |

### Що треба виправити:

**Файл:** `templates/hub/course_list.html`

**Рядок 347 - ЗМІНИТИ:**
```html
Застосувати
```
**НА:**
```html
Застосувати фільтри
```

**Рядок 354 - ЗМІНИТИ:**
```html
Скинути все
```
**НА:**
```html
Скинути всі
```

---

## 🎯 ЗАВДАННЯ 13: Список категорій інтересів - СТВОРИТИ В БД

### Що видно в Telegram повідомленні (скріншот 4):

**Список інтересів в чіткій послідовності:**
```
a) тренерство
   (підкатегорії: тренер воротарів, дитячий тренер, тренер ЗФП, тренер професійних команд)
б) аналітика і скаутинг
в) менеджмент
г) спортивна психологія
ґ) нутриціологія
д) реабілітація
е) футболіст
є) батько
```

**+ додати ці функціональні кнопки в поле фільтрації**

### Що треба зробити:

Створити management команду для додавання цих категорій в БД.

**Файл:** `apps/content/management/commands/create_interests.py`

**СТВОРИТИ НОВИЙ ФАЙЛ:**
```python
from django.core.management.base import BaseCommand
from apps.content.models import Tag, Category


class Command(BaseCommand):
    help = 'Створити теги інтересів та категорії згідно usertask.md'

    def handle(self, *args, **options):
        self.stdout.write('Створюємо інтереси...')
        
        # Інтереси для профілю користувача (чітка послідовність)
        interests_data = [
            ('Тренерство', 1),
            ('Аналітика і скаутинг', 2),
            ('ЗФП', 3),
            ('Менеджмент', 4),
            ('Психологія', 5),
            ('Нутриціологія', 6),  # НЕ "харчування"!
            ('Футболіст', 7),
            ('Батько', 8),
            ('Реабілітація', 9),
        ]
        
        for name, order in interests_data:
            tag, created = Tag.objects.get_or_create(
                name=name,
                tag_type='interest',
                defaults={
                    'display_order': order,
                    'slug': name.lower().replace(' ', '-').replace('і', 'i'),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Створено інтерес: {name}'))
            else:
                self.stdout.write(f'  Інтерес вже існує: {name}')
        
        self.stdout.write('')
        self.stdout.write('Створюємо категорії курсів...')
        
        # Категорії для фільтрації курсів
        categories_data = [
            ('Тренерство', 1, [
                'Тренер воротарів',
                'Дитячий тренер',
                'Тренер ЗФП',
                'Тренер професійних команд',
            ]),
            ('Аналітика і скаутинг', 2, []),
            ('Менеджмент', 3, []),
            ('Спортивна психологія', 4, []),
            ('Нутриціологія', 5, []),
            ('Реабілітація', 6, []),
            ('Футболіст', 7, []),
            ('Батько', 8, []),
        ]
        
        for name, order, subcats in categories_data:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'display_order': order,
                    'slug': name.lower().replace(' ', '-').replace('і', 'i'),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Створено категорію: {name}'))
            else:
                self.stdout.write(f'  Категорія вже існує: {name}')
            
            # Підкатегорії
            for sub_name in subcats:
                sub_cat, sub_created = Category.objects.get_or_create(
                    name=sub_name,
                    parent=cat,
                    defaults={
                        'slug': sub_name.lower().replace(' ', '-'),
                    }
                )
                if sub_created:
                    self.stdout.write(f'  ✓ Створено підкатегорію: {sub_name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Всі інтереси та категорії створено!'))
```

**Після створення запустити:**
```bash
python manage.py create_interests
```

---

## 📊 ФІНАЛЬНЕ ПОРІВНЯННЯ ВСІХ СКРІНШОТІВ

### СКРІНШОТИ 1-2 (Особистий кабінет):
**Сторінка:** Кабінет користувача  
**Вкладки:** Історія оплат + Підписка  
**Співпадання:** 90%  
**Треба додати:** Колонка "Дія", блоки Loyalty

### СКРІНШОТ 3 (Програма лояльності):
**Сторінка:** Вкладка "Програма лояльності"  
**Співпадання:** Невідомо (треба перевірити файл)  
**Треба:** 3 блоки (Рівень, Прогрес, Знижка)

### СКРІНШОТИ 4-5 (Тарифи):
**Сторінка:** Тарифна сітка (pricing.html)  
**Співпадання:** 85%  
**Треба додати:** Іконки, слогани, правильні заголовки

### СКРІНШОТ 6 (Кошик):
**Сторінка:** Кошик покупок  
**Співпадання:** **100%** ✅  
**Треба додати:** НІЧОГО! Все готово!

### СКРІНШОТИ 7-8 (Фільтри):
**Сторінка:** Хаб знань (course_list.html)  
**Співпадання:** 95%  
**Треба виправити:** Тексти кнопок ("Застосувати" → "Застосувати фільтри")

### СКРІНШОТ 9 (Категорії):
**Це текст з usertask.md** - список категорій які треба створити в БД  
**Треба:** Команда create_interests для наповнення БД

---

## 📋 ПІДСУМКОВИЙ ЧЕКЛИСТ ВСІХ ЗАВДАНЬ

### ОСОБИСТИЙ КАБІНЕТ:
- [ ] Вкладка "Історія оплат" - додати колонку "Дія" (ЗАВДАННЯ 1)
- [ ] Вкладка "Підписка" - додати блоки Loyalty (ЗАВДАННЯ 2)
- [ ] Додати індикатор "днів з нами" (ЗАВДАННЯ 3)
- [ ] Виправити статуси верифікації (ЗАВДАННЯ 5)
- [ ] Вкладка "Мої файли" - додати іконки 🔒 💰 (ЗАВДАННЯ 6)
- [ ] Інтереси як кнопки-теги (ЗАВДАННЯ 7)
- [ ] Кнопка "Програма лояльності" (ЗАВДАННЯ 8)
- [ ] Вкладка "Програма лояльності" - перевірити блоки (ЗАВДАННЯ 9)

### СТОРІНКА ТАРИФІВ:
- [ ] Змінити заголовок на "Train with a VISION." (ЗАВДАННЯ 10)
- [ ] Додати слоган "Rise through the ranks." (ЗАВДАННЯ 10)
- [ ] Додати іконки до кожного плану (ЗАВДАННЯ 10)
- [ ] Додати підзаголовки (Початковий Рівень, тощо) (ЗАВДАННЯ 10)
- [ ] Додати слогани з кольорами (ЗАВДАННЯ 10)
- [ ] CSS для іконок та слоганів (ЗАВДАННЯ 10)

### ХАБ ЗНАНЬ (ФІЛЬТРИ):
- [ ] Виправити текст "Застосувати" → "Застосувати фільтри" (ЗАВДАННЯ 12)
- [ ] Виправити текст "Скинути все" → "Скинути всі" (ЗАВДАННЯ 12)

### БАЗА ДАНИХ:
- [ ] Створити команду create_interests (ЗАВДАННЯ 13)
- [ ] Додати 9 інтересів у чіткій послідовності (ЗАВДАННЯ 13)
- [ ] Додати 8 категорій з підкатегоріями (ЗАВДАННЯ 13)
- [ ] Запустити команду python manage.py create_interests (ЗАВДАННЯ 13)

### КОШИК:
- [✓] **ВСЕ ГОТОВО! 100% СПІВПАДАЄ!** Нічого робити не треба!

---

## 🎯 ЗАВДАННЯ 14: Виправити помилку в кнопці "Зберти зміни"

### Що показує скріншот з Telegram:

**Текст:** "+ в кнопці 'Зберти зміни' прибрати помилку, має бути 'ЗБЕРЕГТИ'"

### Файл для перевірки:
`templates/account/cabinet.html`

### ✅ ПЕРЕВІРКА:

Дивлюся на рядок 97:
```html
<button type="submit" class="btn-save">ЗБЕРЕГТИ</button>
```

**ВИСНОВОК:** Помилка вже виправлена! Зараз правильно написано "ЗБЕРЕГТИ". ✅

---

## 🎯 ЗАВДАННЯ 15: Перевірити індикатор "днів з нами"

### Що показує скріншот:

На скріні бачу в лівій панелі кабінету:
- Іконка календаря 📅 з числом "17"
- Текст: "1 ..." (обрізаний)
- Текст: "3 нами"

Це індикатор днів з нами! Має показувати "1 день з нами" або "3 дні з нами" тощо.

### Статус:
Індикатора НЕМАЄ в поточному коді. Треба додати (див. ЗАВДАННЯ 3).

---

## 🎯 ЗАВДАННЯ 16: Перевірити вкладки "Особиста інформація" та "Налаштування"

### Що показує Telegram текст:

"- прибрати вікна 'Особиста інформація' та 'Налаштування' - в правій частині OK"

### Файл для перевірки:
`templates/account/cabinet.html`

### ✅ ПЕРЕВІРКА:

Дивлюся на вкладки (рядки 105-124):
```html
<nav class="cabinet-tabs">
    <a href="{% url 'cabinet:profile' %}">Профіль</a>
    <a href="{% url 'cabinet:subscription' %}">Підписка</a>
    <a href="{% url 'cabinet:files' %}">Мої файли</a>
    <a href="{% url 'cabinet:loyalty' %}">Програма лояльності</a>
    <a href="{% url 'cabinet:payments' %}">Історія оплат</a>
</nav>
```

**ВИСНОВОК:** 
- Немає вкладок "Особиста інформація" та "Налаштування" ✅
- Є тільки: Профіль, Підписка, Мої файли, Програма лояльності, Історія оплат
- Все правильно! ✅

---

## 🎯 ЗАВДАННЯ 17: Сторінка івенту - ДОДАТИ БЛОКИ

### Що показує скріншот детальної сторінки івенту:

**Структура сторінки:**

1. **Секція "Опис та програма"**
   - Заголовок: "ФФП — щорічний форум для тренерів, аналітиків, менеджерів, нутриціологів та психологів"

2. **Блок "Що ти отримаєш:"**
   - Шаблінні відео аналітика та скаут-форм
   - Доступ до закритої спільноти у telegram

3. **Блок "Для кого"**
   - Тренери (всіх команд та віковів)
   - Аналітики, скаути, менеджери
   - Психологи, нутриціологія, батьки гравців

4. **Агенція (скорочено):**
   - 18:00 — Відкриття, привітання
   - 18:10 — Панель «Аналітика + тактика»
   - 19:00 — Практика «Підвищення швидкості УПР»
   - 19:45 — Перерва і нетворкінг
   - 20:15 — Обхуття молодих талантів
   - 20:35 — Q&A, прогнози, фінал FFF 6

5. **Квитки (3 тарифи):**
   - **STANDARD** — 5450
     - Доступ до трансляції + 7 днів запис
   - **PRO** — 6750
     - STANDARD + матеріали спікерів (PDF) + вебінар
   - **VIP** — 41250
     - PRO + трансляція Q&A (30 хв)

6. **Кнопка:** "Купити квиток" (червона)

7. **Спікери форуму:**
   - 4 картки з фото: ctte.jpg, owen.jpg, zou-hai.jpg, villaforta.jpg

### Файл для редагування:
`templates/events/event_detail.html`

### ✅ ПОРІВНЯННЯ:

| Елемент | На скріншоті | В коді | Статус |
|---------|--------------|--------|--------|
| Hero секція | ✓ Є | ✓ Є (рядки 13-52) | ✅ OK |
| Опис події | ✓ Є | ✓ Є (рядки 59-64) | ✅ OK |
| Розклад/Агенда | ✓ Є | ✓ Є (рядки 67-107) | ✅ OK |
| Спікери | ✓ Є | ✓ Є (рядки 110-177) | ✅ OK |
| Кнопка "Купити квиток" | ✓ Є | ✓ Є (рядок 236) | ✅ OK |
| **"Що ти отримаєш"** | **✓ Є** | **✗ НЕМАЄ** | ❌ ДОДАТИ |
| **"Для кого"** | **✓ Є** | **✗ НЕМАЄ** | ❌ ДОДАТИ |
| **3 тарифи квитків** | **✓ Є (STANDARD/PRO/VIP)** | **✗ НЕМАЄ** | ❌ ДОДАТИ |

### Що треба додати:

#### 17.1. Додати блок "Що ти отримаєш"

**ПІСЛЯ секції "Про подію" (після рядка 64) ВСТАВИТИ:**

```html
<!-- Що ти отримаєш -->
<section class="event-section">
    <h2 class="section-title">Що ти отримаєш</h2>
    {% if event.benefits %}
    <ul class="benefits-list">
        {% for benefit in event.benefits %}
        <li class="benefit-item">
            <svg class="benefit-icon" width="20" height="20" viewBox="0 0 24 24">
                <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <span>{{ benefit }}</span>
        </li>
        {% endfor %}
    </ul>
    {% else %}
    <ul class="benefits-list">
        <li class="benefit-item">
            <svg class="benefit-icon" width="20" height="20" viewBox="0 0 24 24">
                <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <span>Шаблінні відео аналітика та скаут-форм</span>
        </li>
        <li class="benefit-item">
            <svg class="benefit-icon" width="20" height="20" viewBox="0 0 24 24">
                <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <span>Доступ до закритої спільноти у telegram</span>
        </li>
    </ul>
    {% endif %}
</section>
```

#### 17.2. Додати блок "Для кого"

**ПІСЛЯ блоку "Що ти отримаєш" ВСТАВИТИ:**

```html
<!-- Для кого -->
<section class="event-section">
    <h2 class="section-title">Для кого</h2>
    {% if event.target_audience %}
    <ul class="audience-list">
        {% for audience in event.target_audience %}
        <li class="audience-item">{{ audience }}</li>
        {% endfor %}
    </ul>
    {% else %}
    <ul class="audience-list">
        <li class="audience-item">Тренери (всіх команд та віковів)</li>
        <li class="audience-item">Аналітики, скаути, менеджери</li>
        <li class="audience-item">Психологи, нутриціологія, батьки гравців</li>
    </ul>
    {% endif %}
</section>
```

#### 17.3. Додати блок "Тарифи квитків"

**ПІСЛЯ блоку розкладу (після рядка 107) ВСТАВИТИ:**

```html
<!-- Тарифи квитків -->
{% if event.ticket_tiers %}
<section class="event-section">
    <h2 class="section-title">Квитки</h2>
    <div class="ticket-tiers-grid">
        {% for tier in event.ticket_tiers %}
        <div class="tier-card">
            <div class="tier-header">
                <h3 class="tier-name">{{ tier.name }}</h3>
                <div class="tier-price">{{ tier.price }}</div>
            </div>
            <div class="tier-features">
                <ul>
                    {% for feature in tier.features %}
                    <li>{{ feature }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endfor %}
    </div>
</section>
{% endif %}
```

#### 17.4. Додати CSS для нових блоків

**Файл:** `static/css/components/events.css`

**ДОДАТИ:**
```css
/* Блок "Що ти отримаєш" */
.benefits-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.benefit-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
    font-size: 16px;
    line-height: 1.5;
}

.benefit-icon {
    flex-shrink: 0;
    color: #10b981;
    margin-top: 2px;
}

/* Блок "Для кого" */
.audience-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.audience-item {
    padding: 12px 20px;
    margin-bottom: 10px;
    background: #f3f4f6;
    border-left: 3px solid #f97316;
    border-radius: 4px;
    font-size: 15px;
}

/* Тарифи квитків */
.ticket-tiers-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 20px;
}

.tier-card {
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px;
    transition: all 0.3s ease;
}

.tier-card:hover {
    border-color: #f97316;
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.1);
}

.tier-header {
    text-align: center;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e5e7eb;
}

.tier-name {
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 10px;
}

.tier-price {
    font-size: 36px;
    font-weight: 700;
    color: #f97316;
}

.tier-features ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.tier-features li {
    padding: 8px 0;
    border-bottom: 1px solid #f3f4f6;
    font-size: 14px;
}

.tier-features li:last-child {
    border-bottom: none;
}

@media (max-width: 992px) {
    .ticket-tiers-grid {
        grid-template-columns: 1fr;
    }
}
```

#### 17.5. Додати поля в модель Event

**Файл:** `apps/events/models.py`

**ЗНАЙТИ модель Event та ДОДАТИ поля:**

```python
class Event(models.Model):
    # ... існуючі поля ...
    
    # Додати ці поля:
    benefits = models.JSONField(
        default=list,
        blank=True,
        help_text='Список переваг події (що отримає учасник)',
        verbose_name='Що ти отримаєш'
    )
    
    target_audience = models.JSONField(
        default=list,
        blank=True,
        help_text='Для кого ця подія (цільова аудиторія)',
        verbose_name='Для кого'
    )
    
    ticket_tiers = models.JSONField(
        default=list,
        blank=True,
        help_text='Тарифи квитків у форматі JSON',
        verbose_name='Тарифи квитків'
    )
    
    # Приклад для ticket_tiers:
    # [
    #     {
    #         "name": "STANDARD",
    #         "price": 5450,
    #         "features": ["Доступ до трансляції", "7 днів запис"]
    #     },
    #     {
    #         "name": "PRO",
    #         "price": 6750,
    #         "features": ["STANDARD", "Матеріали спікерів (PDF)", "Вебінар"]
    #     },
    #     {
    #         "name": "VIP",
    #         "price": 41250,
    #         "features": ["PRO", "Трансляція Q&A (30 хв)"]
    #     }
    # ]
```

**ПІСЛЯ ДОДАВАННЯ полів - створити міграцію:**
```bash
python manage.py makemigrations events
python manage.py migrate
```

---

## 🎯 ЗАВДАННЯ 18: Додати кнопку "Правила Програми Лояльності"

### Що каже Telegram текст:

"- змінити розділ Програми Лояльності (згідно тієї, що раніше була презентована) + додати кнопку 'Правила Програми Лояльності' для переходу на сторінку (та саму сторінку) з детальною інформацією про ПЛ"

### Файл для редагування:
`templates/account/tabs/loyalty.html`

### Що треба додати:

#### 18.1. Перевірити чи є файл loyalty.html та кнопка

Треба перевірити:
1. Чи існує `templates/account/tabs/loyalty.html`
2. Чи є кнопка "Правила Програми Лояльності"
3. Чи веде вона на окрему сторінку `loyalty:rules`

#### 18.2. Перевірити окрему сторінку Програми Лояльності

Згідно finalplan.md:
- Файл `templates/loyalty/rules.html` вже реалізований
- Містить: Hero banner, таблиці, roadmap, CTA кнопки
- Треба лише покращити дизайн (див. ЗАВДАННЯ в finalplan)

---

## 🎯 ЗАВДАННЯ 19: Подфіксити функцію додавання фото

### Що каже Telegram текст:

"- подфіксити функцію додавання фото"

### Файл для перевірки:
`templates/account/cabinet.html` + `static/js/cabinet.js`

### Поточний код (рядки 26-29):

```html
<button class="avatar-upload-btn">
    Завантажити фото
</button>
<input type="file" id="avatar-input" accept="image/*" class="is-hidden">
```

### Що треба додати в JavaScript:

**Файл:** `static/js/cabinet.js`

**ПЕРЕВІРИТИ чи є такий код, якщо НЕМАЄ - ДОДАТИ:**

```javascript
// Активація input при кліку на кнопку
document.addEventListener('DOMContentLoaded', function() {
    const uploadBtn = document.querySelector('.avatar-upload-btn');
    const avatarInput = document.getElementById('avatar-input');
    
    if (uploadBtn && avatarInput) {
        uploadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            avatarInput.click();
        });
        
        // Автоматична відправка форми при виборі файлу
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const formData = new FormData();
                formData.append('avatar', this.files[0]);
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                
                fetch('{% url "cabinet:update_avatar" %}', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Оновити аватар на сторінці
                        location.reload();
                    } else {
                        alert('Помилка завантаження фото');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Помилка завантаження');
                });
            }
        });
    }
});
```

#### 19.1. Додати view для завантаження аватара

**Файл:** `apps/accounts/cabinet_views.py`

**ПЕРЕВІРИТИ чи є view `update_avatar`, якщо НЕМАЄ - ДОДАТИ:**

```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def update_avatar(request):
    """AJAX завантаження аватара"""
    try:
        if 'avatar' in request.FILES:
            profile = request.user.profile
            profile.avatar = request.FILES['avatar']
            profile.save()
            
            return JsonResponse({
                'success': True,
                'avatar_url': profile.avatar.url
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Файл не знайдено'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
```

**Додати URL:**

**Файл:** `apps/accounts/cabinet_urls.py`

```python
path('update-avatar/', views.update_avatar, name='update_avatar'),
```

---

## 📊 ФІНАЛЬНИЙ АНАЛІЗ НОВИХ СКРІНШОТІВ

### СКРІНШОТ 1 (Форма кабінету з індикатором днів):
**Сторінка:** Особистий кабінет  
**Що видно:**
- ✅ Вкладки (Підписка, Історія оплат, Мої файли, Програма лояльності)
- ✅ Форма профілю
- ✅ Інтереси як кнопки-теги (Аналітика, Тренерство, Психологія, Харчування)
- ✅ Кнопка "ЗБЕРЕГТИ" (вже виправлено!)
- ❌ Індикатор "днів з нами" (видно іконку календаря, але текст обрізаний)
- ✅ Вікон "Особиста інформація" та "Налаштування" НЕМАЄ (правильно!)

### СКРІНШОТ 2-3 (Історія оплат):
**Сторінка:** Вкладка "Історія оплат"  
**Що видно:**
- ✅ Таблиця з колонками
- ✅ Статуси платежів
- ❌ Колонка "Дія" з кнопками "Повторити" (треба перевірити чи є)

### СКРІНШОТ 4 (Детальна сторінка івенту):
**Сторінка:** event_detail.html  
**Що видно:**
- ✅ Опис події
- ✅ Агенда/розклад
- ✅ Спікери (4 картки)
- ✅ Кнопка "Купити квиток"
- ❌ Блок "Що ти отримаєш"
- ❌ Блок "Для кого"
- ❌ Тарифи (STANDARD, PRO, VIP)

---

## 📋 ОНОВЛЕНИЙ ПОВНИЙ ЧЕКЛИСТ

### ОСОБИСТИЙ КАБІНЕТ:
- [✓] Кнопка "ЗБЕРЕГТИ" - вже виправлено!
- [✓] Вкладки "Особиста інформація" та "Налаштування" - прибрано!
- [ ] Додати індикатор "днів з нами" (ЗАВДАННЯ 3)
- [ ] Подфіксити функцію завантаження фото (ЗАВДАННЯ 19)
- [ ] Вкладка "Історія оплат" - колонка "Дія" (ЗАВДАННЯ 1)
- [ ] Вкладка "Підписка" - блоки Loyalty (ЗАВДАННЯ 2)
- [ ] Вкладка "Мої файли" - іконки 🔒💰 (ЗАВДАННЯ 6)
- [ ] Інтереси як кнопки-теги (ЗАВДАННЯ 7)
- [ ] Кнопка "Правила ПЛ" у вкладці loyalty (ЗАВДАННЯ 18)

### СТОРІНКА ІВЕНТУ:
- [ ] Додати блок "Що ти отримаєш" (ЗАВДАННЯ 17.1)
- [ ] Додати блок "Для кого" (ЗАВДАННЯ 17.2)
- [ ] Додати блок "Тарифи квитків" (ЗАВДАННЯ 17.3)
- [ ] Додати поля benefits, target_audience, ticket_tiers в модель Event (ЗАВДАННЯ 17.5)
- [ ] Створити міграцію
- [ ] CSS для нових блоків (ЗАВДАННЯ 17.4)

### СТОРІНКА ТАРИФІВ:
- [ ] Іконки та слогани (ЗАВДАННЯ 10)

### ХАБ ЗНАНЬ:
- [ ] Виправити тексти кнопок (ЗАВДАННЯ 12)

### БАЗА ДАНИХ:
- [ ] Команда create_interests (ЗАВДАННЯ 13)

---

**ВАЖЛИВО:** Всі зміни мають бути зроблені згідно існуючого стилю коду!
Зберігайте відступи, класи, структуру як у поточних файлах.

