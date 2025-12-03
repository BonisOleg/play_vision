<!-- c5d94779-f096-4e19-8ce0-2316592907e0 422f41b6-2f5c-4e61-83e4-a3eecd0124ba -->
# Виправлення помилок синхронізації в admin action

## Проблема

В адмінці показуються повідомлення про помилки синхронізації для деяких заявок, хоча в логах багато успішних записів.

## Можливі причини

1. Деякі заявки мають невалідні дані (порожні email/phone)
2. SendPulse API повертає помилки для деяких контактів
3. Недостатнє логування для діагностики проблем
4. Помилки не обробляються коректно в admin action

## Виправлення

### 1. Покращення логування в admin action (`apps/landing/admin.py`)

**Проблема:** Коли заявка не синхронізується, не видно детальної інформації про причину.

**Рішення:**

- Додати логування для кожної невдалої спроби з деталями (ID заявки, email, причина)
- Логувати, коли заявка пропускається через валідацію (відсутні email/phone)
- Додати логування, коли API повертає помилку (з повною відповіддю)
- Покращити повідомлення для користувача з конкретною інформацією

**Код:**

```python
# В циклі sync_to_sendpulse(), коли заявка пропускається:
if not lead.email or not lead.phone:
    error_count += 1
    logger.warning(
        f'Lead {lead.id} skipped: missing email or phone. '
        f'Email: {lead.email}, Phone: {lead.phone}'
    )
    continue

# Коли синхронізація не вдалася:
if not success:
    error_count += 1
    logger.error(
        f'Failed to sync lead {lead.id} ({lead.email}) to addressbook {addressbook_id}. '
        f'Source: {lead.source}, Name: {lead.first_name}'
    )
```

### 2. Покращення логування в SendPulseService (`apps/landing/services.py`)

**Проблема:** При помилках API не логується повна відповідь, важко діагностувати проблему.

**Рішення:**

- Логувати повну відповідь API при помилках (не тільки статус код)
- Додати логування даних, які відправляються до API (для діагностики)
- Логувати різні типи помилок окремо (422, 400, 500, тощо)

**Код:**

```python
# В методі add_contact_to_addressbook(), при помилці:
logger.error(
    f'Failed to add contact to SendPulse addressbook {addressbook_id}: '
    f'Status {response.status_code}, Response: {response.text}, '
    f'Payload: {payload}'
)
```

### 3. Обробка дублікатів контактів

**Проблема:** Якщо контакт вже існує в SendPulse, API може повертати помилку, але це не критично.

**Рішення:**

- Перевіряти, чи помилка пов'язана з дублікатом контакту
- Якщо так, вважати синхронізацію успішною (контакт вже є в системі)
- Логувати дублікати окремо для інформації

**Код:**

```python
# В методі add_contact_to_addressbook(), після отримання відповіді:
if response.status_code == 200:
    # ... existing code ...
elif response.status_code == 400:
    # Можливо, контакт вже існує
    error_data = response.json()
    if 'already exists' in error_data.get('message', '').lower():
        logger.info(f'Contact {email} already exists in addressbook {addressbook_id}')
        return True  # Вважаємо успішним
    else:
        logger.error(f'Bad request: {response.text}')
        return False
```

## Файли для зміни

- `apps/landing/admin.py` - покращити логування в `sync_to_sendpulse()`
- `apps/landing/services.py` - покращити логування в методах `add_contact()` та `add_contact_to_addressbook()`

### To-dos

- [x] 
- [x] 
- [x] 