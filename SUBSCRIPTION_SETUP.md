# 🎯 Налаштування системи підписок Play Vision

## 📋 Зміст
1. [Встановлення залежностей](#встановлення-залежностей)
2. [Налаштування LiqPay](#налаштування-liqpay)
3. [Міграції БД](#міграції-бд)
4. [Створення планів підписки](#створення-планів-підписки)
5. [Автопродовження підписок](#автопродовження-підписок)
6. [Тестування](#тестування)

---

## 1️⃣ Встановлення залежностей

```bash
pip3 install -r requirements.txt
```

Основні нові залежності:
- `liqpay-sdk-python==1.0.1` - SDK для роботи з LiqPay API

---

## 2️⃣ Налаштування LiqPay

### Отримання API ключів

1. Зареєструйтесь на [liqpay.ua](https://www.liqpay.ua/)
2. Створіть магазин
3. Перейдіть в розділ **API** та скопіюйте:
   - `public_key`
   - `private_key`

### Додайте ключі в `.env`

```env
# LiqPay Settings
LIQPAY_PUBLIC_KEY=your_public_key_here
LIQPAY_PRIVATE_KEY=your_private_key_here
LIQPAY_SANDBOX=True  # False для production
```

---

## 3️⃣ Міграції БД

```bash
python3 manage.py migrate subscriptions
```

Це створить нові поля для моделі `Plan`:
- `is_best_value` - автоматичне визначення найвигіднішого плану
- `badge_type` - тип бейджа
- `total_subscriptions` - статистика продажів

---

## 4️⃣ Створення планів підписки

### Автоматичне створення 4 тарифів

```bash
python3 manage.py create_subscription_plans
```

Це створить:
- **C-VISION** (1 міс) - 299₴
- **B-VISION** (1 міс) - 599₴  
- **A-VISION** (1 міс) - 999₴
- **PRO-VISION** (1 міс) - 1499₴

### Ручне створення через Django Admin

1. Перейдіть в `/admin/subscriptions/plan/`
2. Додайте новий план
3. Заповніть поля:
   - `name` - назва плану
   - `duration` - тривалість (1_month / 3_months / 12_months)
   - `duration_months` - кількість місяців (число)
   - `price` - ціна
   - `features` - JSON масив переваг
   - `is_popular` - чи популярний план
   - `is_active` - чи активний

---

## 5️⃣ Автопродовження підписок

### Налаштування cron job

Додайте в crontab для щоденного запуску о 00:00:

```bash
crontab -e
```

```cron
0 0 * * * cd /path/to/Play_Vision && /path/to/venv/bin/python3 manage.py renew_subscriptions --days-before=3
```

### Ручний запуск

```bash
# Тестовий режим (без реальних списань)
python3 manage.py renew_subscriptions --dry-run

# Реальний запуск
python3 manage.py renew_subscriptions --days-before=3
```

Параметри:
- `--days-before N` - за скільки днів до закінчення почати продовження (за замовчуванням: 3)
- `--dry-run` - тестовий режим без реальних дій

---

## 6️⃣ Тестування

### Тестування флоу підписки

1. **Перейдіть на сторінку підписок:**
   ```
   http://localhost:8000/pricing/
   ```

2. **Оберіть план** → клік на "Вступити в клуб" або "Обрати план"

3. **Сторінка checkout:**
   ```
   http://localhost:8000/checkout/<plan_id>/
   ```
   - Перевірте поле промокоду
   - Перевірте способи оплати
   - Перевірте порівняння з окремими покупками (якщо є)

4. **Тестова оплата:**
   - В режимі `LIQPAY_SANDBOX=True` використовуйте тестові картки LiqPay
   - Тестова картка: `4242424242424242`, CVV: `123`, будь-яка дата

5. **Перевірте результати:**
   - Success: `http://localhost:8000/payment-success/`
   - Failure: `http://localhost:8000/payment-failure/`

### Перевірка редіректів

- **Неавторизований користувач** → "Вступити в клуб" → зберігається вибраний план
- **Авторизований без підписки** → "Обрати план" → checkout
- **З активною підпискою** → показує "Поточний план"

### Перевірка бейджів

- **Найдовший термін** → автоматично отримує "Максимальна економія"
- **is_popular=True** → "Найпопулярніший"
- **Економія 15-29%** → "Вигідно"
- **Економія 30%+** → "Максимальна економія"

---

## 🎨 Кастомізація

### Зміна цін планів

```python
from apps.subscriptions.models import Plan

plan = Plan.objects.get(name='PRO-VISION')
plan.price = 1999.00
plan.save()
```

### Зміна бейджів

```python
plan = Plan.objects.get(name='B-VISION')
plan.is_popular = True
plan.badge_text = "Хіт продажів"
plan.save()
```

### Додавання нових переваг

```python
plan = Plan.objects.get(name='PRO-VISION')
plan.features.append('Нова перевага')
plan.save()
```

---

## 🔧 Troubleshooting

### Помилка "Module liqpay not found"

```bash
pip3 install liqpay-sdk-python
```

### Помилка "Invalid signature" від LiqPay

Перевірте правильність ключів в `.env`:
```bash
echo $LIQPAY_PUBLIC_KEY
echo $LIQPAY_PRIVATE_KEY
```

### Підписка не продовжується автоматично

1. Перевірте cron job:
   ```bash
   crontab -l
   ```

2. Перевірте логи:
   ```bash
   tail -f /var/log/cron.log
   ```

3. Запустіть вручну в тестовому режимі:
   ```bash
   python3 manage.py renew_subscriptions --dry-run
   ```

---

## 📚 Додаткові ресурси

- [LiqPay API Documentation](https://www.liqpay.ua/documentation/api/home)
- [Django Subscriptions Best Practices](https://docs.djangoproject.com/)
- [Play Vision Documentation](./README.md)

---

## 🎉 Готово!

Система підписок повністю налаштована та готова до використання.

Для production обов'язково:
1. Встановіть `LIQPAY_SANDBOX=False` в `.env`
2. Використовуйте реальні API ключі
3. Налаштуйте HTTPS
4. Налаштуйте webhook URL для LiqPay callbacks
5. Додайте моніторинг автопродовження підписок

