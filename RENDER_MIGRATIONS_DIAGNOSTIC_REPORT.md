# 🔍 ЗВІТ: ПРОБЛЕМИ З МІГРАЦІЯМИ Play Vision

**Дата:** 2025-11-20  
**Середовище:** Render Production  
**Статус:** Всі сервіси SUSPENDED

---

## 🚨 КРИТИЧНІ ПРОБЛЕМИ

### 1. **CMS App - Розрив у ланцюгу міграцій**

**Стан:**
- ✅ Існує: `0001_initial.py`
- ✅ Існує: `0006_new_page_models.py` (залежить від `0001`)
- ✅ Існує: `0010_alter_eventgridcell_image_...py` (залежить від `0006`)
- ❌ ВІДСУТНІ: `0002.py`, `0003.py`, `0004.py`, `0005.py`, `0007.py`, `0008.py`, `0009.py`

**Проблема:**
- Django очікує послідовні номери міграцій
- Міграція `0006` має `dependencies = [('cms', '0001_initial')]`, але між ними пропущені 0002-0005
- Міграція `0010` залежить від `0006`, але пропущені 0007-0009
- Це **не зламає** виконання якщо всі таблиці вже створені, але **заплутує історію**

**Рішення:**
1. Перевірити чи застосовані ці міграції в БД
2. Якщо НІ - створити dummy міграції
3. Якщо ТАК - видалити непотрібні записи з `django_migrations`

### 2. **Subscriptions - Багато операцій очищення (potential data loss)**

**Міграції:**
```
0002_add_missing_fields.py
0003_remove_duration_field.py        ⚠️  Видалення поля
0004_remove_duration_months.py       ⚠️  Видалення поля
0005_verify_subscriptions_table.py   ⚠️  Data migration
0006_cleanup_old_columns.py          ⚠️  Видалення колонок
0007_make_old_fields_nullable.py     ⚠️  Зміна nullable
```

**Проблема:**
- Багато операцій `RemoveField` можуть призвести до **втрати даних**
- Потрібно перевірити чи є активні підписки перед застосуванням

**Рішення:**
1. Backup БД перед застосуванням міграцій
2. Перевірити чи є дані в таблиці `subscriptions_subscription`
3. Застосовувати поетапно з перевіркою після кожної

### 3. **Events - Rename поля `registration_data` → `custom_fields`**

**Міграція:** `0009_rename_registration_data_to_custom_fields.py`

**Проблема:**
- Перейменування поля може зламати старий код, якщо він досі посилається на `registration_data`
- Потрібно перевірити чи всі місця в коді оновлені

**Рішення:**
1. Grep по всьому коду: `registration_data`
2. Перевірити views/forms/serializers
3. Застосувати міграцію тільки якщо код синхронізовано

### 4. **ImageField max_length=500 (Cloudinary URLs)**

**Змінені міграції:**
- `accounts/0002_alter_profile_avatar.py`
- `events/0010_alter_event_banner_image_...py`
- `content/0012_alter_course_logo_...py`
- `cms/0010_alter_eventgridcell_image_...py`

**Проблема:**
- Всі `ImageField` змінено на `max_length=500` для довгих Cloudinary URLs
- Якщо міграції НЕ застосовані, завантаження зображень може **fail** з помилкою `max_length`

**Рішення:**
1. Перевірити чи застосовані ці міграції
2. Якщо НІ - застосувати НЕГАЙНО

---

## 📋 КОМАНДИ ДЛЯ ДІАГНОСТИКИ

### Варіант 1: Render CLI (якщо сервіс активний)

```bash
# Зробити скрипт виконуваним
chmod +x diagnose_render_db.sh

# Запустити діагностику
./diagnose_render_db.sh
```

### Варіант 2: Ручні команди Render CLI

```bash
# 1. Список сервісів
render services list

# 2. Статус сервісу playvision
render service status playvision

# 3. Логи (шукати migration errors)
render logs playvision --tail 200 | grep -i migration

# 4. Django shell - список міграцій
render shell playvision -- 'python manage.py showmigrations --list'

# 5. Django shell - незастосовані міграції
render shell playvision -- 'python manage.py showmigrations --plan'

# 6. Застосувати міграції (ОБЕРЕЖНО!)
render shell playvision -- 'python manage.py migrate --no-input'

# 7. Перевірити конкретний app
render shell playvision -- 'python manage.py showmigrations cms'
```

### Варіант 3: Python скрипт діагностики

```bash
# Завантажити скрипт на Render і виконати
cat check_render_migrations.py | render shell playvision
```

### Варіант 4: Прямий доступ до PostgreSQL

```bash
# Отримати DATABASE_URL з Render Dashboard
# Потім:

psql $DATABASE_URL

# SQL запити:
SELECT app, name FROM django_migrations WHERE app = 'cms' ORDER BY name;
SELECT app, name FROM django_migrations WHERE app = 'subscriptions' ORDER BY name;
SELECT app, name FROM django_migrations WHERE app = 'events' ORDER BY name;

# Перевірити таблиці
\dt cms_*
\dt subscriptions_*
\dt events_*

# Структура проблемних таблиць
\d cms_eventgridcell
\d subscriptions_subscription
\d events_eventregistration
```

---

## 🔧 КОМАНДИ ДЛЯ ВИПРАВЛЕННЯ

### Якщо виявлено незастосовані міграції:

```bash
# Застосувати всі міграції
render shell playvision -- 'python manage.py migrate --no-input'

# Застосувати конкретний app
render shell playvision -- 'python manage.py migrate cms --no-input'
render shell playvision -- 'python manage.py migrate subscriptions --no-input'
```

### Якщо виявлено розрив у CMS міграціях:

Локально створити dummy міграції:

```bash
# Якщо БД каже що 0002-0005 застосовані, але файлів немає
python manage.py makemigrations cms --empty --name dummy_02
python manage.py makemigrations cms --empty --name dummy_03
python manage.py makemigrations cms --empty --name dummy_04
python manage.py makemigrations cms --empty --name dummy_05
python manage.py makemigrations cms --empty --name dummy_07
python manage.py makemigrations cms --empty --name dummy_08
python manage.py makemigrations cms --empty --name dummy_09

# Або видалити записи з БД (НЕБЕЗПЕЧНО!)
psql $DATABASE_URL -c "DELETE FROM django_migrations WHERE app='cms' AND name IN ('0002_*', '0003_*', '0004_*', '0005_*', '0007_*', '0008_*', '0009_*');"
```

### Якщо потрібно squash міграції CMS:

```bash
# Об'єднати всі міграції CMS в одну
python manage.py squashmigrations cms 0001 0010

# Застосувати на Render
git add apps/cms/migrations/
git commit -m "Squash CMS migrations"
git push

# На Render автоматично відбудеться deploy
```

---

## 🎯 РЕКОМЕНДОВАНИЙ ПЛАН ДІЙ

### Крок 1: Діагностика (БЕЗ ЗМІН)

```bash
# Запустити скрипт діагностики
./diagnose_render_db.sh

# Або вручну:
render services list
render service status playvision
render logs playvision --tail 200
render shell playvision -- 'python manage.py showmigrations --list'
```

**Мета:** Зрозуміти реальний стан БД та міграцій

### Крок 2: Аналіз результатів

Перевірити:
- ✅ Які міграції **застосовані** в БД (таблиця `django_migrations`)
- ✅ Які міграції **є у файлах** (директорії `apps/*/migrations/`)
- ❌ Які міграції **відсутні** (розриви в нумерації)
- ❌ Які міграції **не застосовані** (файли є, але в БД немає)

### Крок 3: Backup БД (ОБОВ'ЯЗКОВО!)

```bash
# Через Render Dashboard або CLI
render db backup playvision-db
```

### Крок 4: Виправлення

**Варіант A:** Якщо всі таблиці існують і працюють:
- Нічого не робити
- Або видалити зайві записи з `django_migrations`

**Варіант B:** Якщо є незастосовані міграції:
- Застосувати через `python manage.py migrate`

**Варіант C:** Якщо є розриви і помилки:
- Створити dummy міграції
- Або squash існуючі міграції

### Крок 5: Тестування

```bash
# Запустити тести на Render
render shell playvision -- 'python manage.py check'
render shell playvision -- 'python manage.py migrate --check'

# Перевірити сайт
curl https://playvision.onrender.com/healthz
```

---

## 📊 ОЧІКУВАНІ РЕЗУЛЬТАТИ

Після виконання команд ви отримаєте:

1. **Список всіх сервісів** з їх статусами
2. **Логи останнього deploy** з помилками міграцій (якщо були)
3. **Повний список міграцій** по кожному додатку
4. **Порівняння** файлів міграцій vs записів в БД
5. **Рекомендації** щодо виправлення проблем

---

## ⚠️ ВАЖЛИВІ ЗАУВАЖЕННЯ

1. **НЕ запускати `migrate` без backup БД**
2. **НЕ видаляти міграції** з `django_migrations` без розуміння наслідків
3. **ЗАВЖДИ тестувати** зміни на staging перед production
4. **Всі сервіси suspended** - потрібно спочатку активувати `playvision`
5. **Squash міграцій** може зламати інші середовища (staging, local)

---

## 📚 ДОДАТКОВІ РЕСУРСИ

- Django Migrations: https://docs.djangoproject.com/en/5.1/topics/migrations/
- Render Deployment: https://render.com/docs/deploy-django
- Render CLI: https://render.com/docs/cli

---

**Автор:** AI Assistant  
**Проєкт:** Play Vision  
**Середовище:** Render Production (Frankfurt)


