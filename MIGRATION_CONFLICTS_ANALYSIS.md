# Аналіз конфліктів та потенційних проблем для міграцій

## Виявлені проблеми

### 1. ⚠️ КРИТИЧНА: Використання `plan.features` в шаблоні

**Файл:** `templates/account/tabs/subscription.html:159`
```html
{% for feature in plan.features %}
```

**Проблема:**
- В моделі `SubscriptionPlan` немає поля або property `features`
- Використовується метод `get_features()` або має бути property
- Після видалення `feature_1-30` це зламається

**Рішення:**
- Додати property `features` в модель який викликає `get_features()`
- Або змінити шаблон на `plan.get_features`

### 2. ⚠️ Міграція 0018 вже існує

**Файл:** `apps/subscriptions/migrations/0018_add_features_6_to_30.py`

**Проблема:**
- Міграція 0018 вже додає `feature_6` до `feature_30`
- Залежність: `('subscriptions', '0007_make_old_fields_nullable')`
- Нова міграція 0019 має залежати від 0018, а не від 0007

**Рішення:**
- Нова міграція 0019 має мати dependency: `('subscriptions', '0018_add_features_6_to_30')`

### 3. ⚠️ Потенційний конфлікт: `discount_3_months` та `discount_12_months`

**Поточні поля:**
- `discount_3_months` - IntegerField (відсоток знижки)
- `discount_12_months` - IntegerField (відсоток знижки)

**Нові поля:**
- `discount_monthly_percentage` - IntegerField
- `discount_monthly_start_date` - DateTimeField
- `discount_monthly_end_date` - DateTimeField
- `discount_3months_percentage` - IntegerField
- `discount_3months_start_date` - DateTimeField
- `discount_3months_end_date` - DateTimeField

**Проблема:**
- Старі поля `discount_3_months` та `discount_12_months` використовуються в `calculate_price()`
- Нові поля мають інші назви (`discount_3months_percentage` vs `discount_3_months`)

**Рішення:**
- Залишити старі поля для backward compatibility
- Або мігрувати дані зі старих полів в нові
- Оновити `calculate_price()` щоб враховувати таймери

### 4. ⚠️ Метод `get_features()` використовується без параметрів

**Файли:**
- `templates/subscriptions/pricing.html:83` - `{% for feature in plan.get_features %}`
- `apps/subscriptions/templatetags/subscription_tags.py:62` - `return plan.get_features()`

**Проблема:**
- Після змін метод `get_features(period='monthly')` буде вимагати параметр
- Існуючі виклики без параметра зламаються

**Рішення:**
- Зробити параметр `period` опціональним з дефолтом `'monthly'`
- Або створити окремий метод `get_features_for_period(period)`

### 5. ⚠️ Template tag `get_feature(plan, index)`

**Файл:** `apps/subscriptions/templatetags/subscription_tags.py:68-87`

**Проблема:**
- Використовує `feature_{index}` напряму
- Після видалення старих полів зламається
- Не враховує період

**Рішення:**
- Оновити щоб використовувати нові поля `feature_{index}_{period}`
- Додати параметр `period`

## Рекомендації для безпечної міграції

### Етап 1: Підготовка (без змін в БД)
1. Додати property `features` в модель для backward compatibility
2. Оновити `get_features()` щоб приймав опціональний `period` з дефолтом `'monthly'`
3. Оновити template tags для підтримки періодів

### Етап 2: Додавання нових полів (міграція 0019)
1. Додати 60 полів для переваг (`feature_1_monthly` до `feature_30_3months`)
2. Додати 6 полів для знижок з таймерами
3. Використати `RunSQL` з `IF NOT EXISTS` для безпеки

### Етап 3: Міграція даних (опціонально)
1. Якщо потрібно зберегти існуючі дані:
   - Скопіювати `feature_1-30` в `feature_1_monthly` до `feature_30_monthly`
   - Або залишити старі поля як fallback

### Етап 4: Видалення старих полів (міграція 0020)
1. Видалити `feature_1` до `feature_30`
2. Використати `RunSQL` з `IF EXISTS` для безпеки
3. **ВАЖЛИВО:** Виконати тільки після перевірки що всі дані мігровані

### Етап 5: Оновлення коду
1. Оновити шаблони для використання нових методів
2. Оновити JavaScript для динамічного перемикання переваг
3. Додати таймер знижок

## Команди для Render Shell

### 1. Діагностика БД
```bash
render shell playvision -- './render_db_diagnostic.sh'
```

### 2. Перевірка міграцій
```bash
render shell playvision -- './render_check_migrations.sh'
```

### 3. Тестування міграцій (dry-run)
```bash
render shell playvision -- './render_test_migration.sh'
```

### 4. Перевірка структури таблиці
```bash
render shell playvision -- 'python manage.py dbshell' <<EOF
\d subscription_plans
\q
EOF
```

### 5. Перевірка застосованих міграцій
```bash
render shell playvision -- 'python manage.py showmigrations subscriptions'
```

## Порядок виконання міграцій на Render

1. **Завантажити скрипти діагностики:**
   ```bash
   # Локально
   scp render_db_diagnostic.sh render_check_migrations.sh render_test_migration.sh user@render:/path/
   ```

2. **Виконати діагностику:**
   ```bash
   render shell playvision -- './render_db_diagnostic.sh'
   ```

3. **Перевірити міграції:**
   ```bash
   render shell playvision -- './render_check_migrations.sh'
   ```

4. **Після деплою коду з міграціями:**
   ```bash
   render shell playvision -- 'python manage.py migrate subscriptions --plan'
   ```

5. **Застосувати міграції:**
   ```bash
   render shell playvision -- 'python manage.py migrate subscriptions'
   ```

## Критичні моменти

1. ⚠️ **НЕ видаляти старі поля** поки не переконаєтесь що всі дані мігровані
2. ⚠️ **Зберегти backward compatibility** для існуючих викликів `get_features()`
3. ⚠️ **Тестувати на staging** перед production
4. ⚠️ **Backup БД** перед видаленням полів

