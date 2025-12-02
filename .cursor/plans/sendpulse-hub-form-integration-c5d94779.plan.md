<!-- c5d94779-f096-4e19-8ce0-2316592907e0 422f41b6-2f5c-4e61-83e4-a3eecd0124ba -->
# Виправлення синхронізації заявок з SendPulse

## Проблема

57 заявок не синхронізуються з SendPulse через:

1. Відсутність обробки порожніх значень `first_name` в методі `add_contact()` для CRM API
2. Недостатнє логування помилок в admin action
3. Відсутність валідації даних перед синхронізацією

## Виправлення

### 1. Оновлення методу `add_contact()` в `apps/landing/services.py`

**Проблема:** Якщо `first_name` порожнє або відсутнє, `firstName` та `lastName` не додаються до `contact_data`, але SendPulse їх вимагає.

**Рішення:**

- Додати fallback для `firstName`: якщо `first_name` порожнє, використовувати частину email до `@` або "User"
- Завжди додавати `firstName` та `lastName` до `contact_data` для CRM API
- Додати валідацію email та phone перед відправкою

**Код:**

```python
# В методі add_contact(), після рядка 92:
# Додати firstName та lastName завжди
if variables and 'first_name' in variables:
    first_name = variables.get('first_name', '').strip()
else:
    first_name = ''

# Якщо first_name порожнє, використати email як fallback
if not first_name:
    # Взяти частину email до @
    email_part = email.split('@')[0] if '@' in email else 'User'
    first_name = email_part if email_part else 'User'

# Розділити ім'я на firstName та lastName
name_parts = first_name.split(maxsplit=1)
contact_data['firstName'] = name_parts[0] if name_parts else first_name
contact_data['lastName'] = name_parts[1] if len(name_parts) > 1 else name_parts[0]
```

### 2. Покращення обробки помилок в `apps/landing/admin.py`

**Проблема:** Помилки не логуються детально, важко зрозуміти причину невдачі.

**Рішення:**

- Додати детальне логування помилок з email та причиною
- Додати валідацію даних перед синхронізацією
- Покращити повідомлення про помилки для користувача

**Код:**

```python
# В методі sync_to_sendpulse(), перед циклом:
import logging
logger = logging.getLogger(__name__)

# В циклі, перед try:
# Валідація даних
if not lead.email or not lead.phone:
    error_count += 1
    logger.warning(f'Lead {lead.id} missing email or phone, skipping')
    continue

# В блоці except:
except Exception as e:
    error_count += 1
    logger.error(
        f'Failed to sync lead {lead.id} ({lead.email}): {str(e)}',
        exc_info=True
    )
    self.message_user(
        request,
        f'Помилка синхронізації {lead.first_name or lead.email}: {str(e)}',
        level=messages.ERROR
    )
```

### 3. Додавання валідації в метод `add_contact_to_addressbook()`

**Проблема:** Можливі порожні значення `name` не обробляються коректно.

**Рішення:**

- Додати fallback для `name` з email, якщо воно порожнє
- Переконатися, що `lastName` завжди має значення

**Код:**

```python
# В методі add_contact_to_addressbook(), після рядка 189:
# Валідація name - має бути не порожнім
if not name or not name.strip():
    # Використати email як fallback
    email_part = email.split('@')[0] if '@' in email else 'User'
    name = email_part if email_part else 'User'
else:
    name = name.strip()

# Розділити ім'я на firstName та lastName
name_parts = name.split(maxsplit=1)
first_name = name_parts[0] if name_parts else 'User'
last_name = name_parts[1] if len(name_parts) > 1 else first_name
```

## Очікуваний результат

1. Всі заявки з валідними email та phone синхронізуються успішно
2. Заявки з порожнім `first_name` використовують email як fallback
3. Детальне логування помилок для діагностики
4. Повідомлення "Не вдалося синхронізувати" зменшиться до 0 або мінімуму

## Файли для зміни

- `apps/landing/services.py` - оновлення методів `add_contact()` та `add_contact_to_addressbook()`
- `apps/landing/admin.py` - покращення обробки помилок в `sync_to_sendpulse()`

### To-dos

- [ ] Додати метод add_contact_to_addressbook() в SendPulseService для роботи з Email Service API
- [ ] Оновити submit_lead view для використання нового методу з адресною книгою для source='hub'
- [ ] Додати SENDPULSE_ADDRESS_BOOK_ID в settings та оновити credentials
- [ ] Протестувати відправку форми на сторінці /hub/ та перевірити додавання контакту в SendPulse