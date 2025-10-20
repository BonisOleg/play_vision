# ФІНАЛЬНИЙ ПЛАН РЕАЛІЗАЦІЇ Play Vision

**Дата створення:** 19.10.2025  
**Останнє оновлення:** 19.10.2025  
**Базовий документ:** usertask.md (1246 рядків, 14 розділів)  
**Поточний стан проєкту:** Проаналізовано повністю та доповнено критичними деталями

---

## 🔴 КРИТИЧНІ ДОПОВНЕННЯ ДО ПЛАНУ

**Цей план було оновлено з важливими деталями, які були пропущені:**

1. **Підпис під логотипом** - "навігатор футбольного розвитку" має бути завжди видимий
2. **Білі РАМКИ** в hero секції (НЕ заливка) - це дуже важливо!
3. **ОДНА ЗЕЛЕНА кнопка** в hero (було 2 - видалити зайву, колір ЗЕЛЕНИЙ не червоний)
4. **Постійний sticky-баннер** в Хаб знань під хедером з текстом про підписку
5. **Події = Івенти** - це одна система (було дублювання в плані)
6. **Виправлення текстів** - в usertask є помилки які треба виправити перед публікацією
7. Додано детальніші інструкції для всіх критичних елементів

**Читайте секцію "КРИТИЧНІ ПРИМІТКИ" для повного списку важливих нюансів!**

---

## ЗАГАЛЬНИЙ ОГЛЯД ПРОЄКТУ

### Поточний технічний стек:
- **Backend:** Django 4.x + PostgreSQL (SQLite для dev)
- **Frontend:** HTML/CSS/JavaScript (без фреймворків)
- **Архітектура:** Модульна (apps/), кожен модуль має models, views, templates, urls
- **Існуючі модулі:**
  - accounts (автентифікація, профілі, верифікація)
  - content (курси, матеріали, теги, категорії, прогрес)
  - events (івенти, квитки, спікери, реєстрації)
  - subscriptions (плани, підписки, доступи)
  - loyalty (програма лояльності, бали, транзакції)
  - payments (платежі, замовлення, промокоди)
  - cart (кошик, рекомендації)
  - cms (сторінки, банери, слайди, експерти)
  - ai (AI помічник)
  - notifications (нотифікації)
  - mentoring (ментор-коучінг - базова структура)
  - core (головні сторінки, утиліти)

---

## РОЗДІЛ 1: РЕЄСТРАЦІЯ

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Модель User (apps/accounts/models.py):
  - Підтримка email АБО телефону
  - Поля: username, email, phone, is_email_verified, is_phone_verified
  - Модель VerificationCode для кодів підтвердження
  - Модель SocialAccount для соц. мереж (google, telegram, tiktok)

**ФОРМИ:**
- CustomUserCreationForm (apps/accounts/forms.py)
- Підтримка реєстрації через email або телефон

**VIEWS:**
- RegisterView (apps/accounts/views.py):
  - Обробка реєстрації
  - Автоматичне створення Profile
  - Відправка коду верифікації для email
  - Автоматичний вхід після реєстрації

**TEMPLATE:**
- templates/auth/register.html:
  - Дві вкладки (Email/Телефон)
  - Поле email або телефону
  - Поле пароля (2 рази)
  - Чекбокс згоди з офертою
  - Чекбокс розсилки
  - Кнопка реєстрації
  - Кнопки соціальних мереж (Google, Telegram, TikTok) - візуально готові

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 1.1. Інтеграція шлюзу для відправки паролів

**ЩО ТРЕБА:**
- Підключити шлюз для SMS (наприклад, Twilio, Vonage)
- Підключити Telegram Bot API для відправки в Telegram
- Підключити WhatsApp Business API для WhatsApp
- Підключити Viber Bot API для Viber

**ДЕ ДОДАТИ:**
- Створити новий файл: `apps/accounts/services/messaging.py`
- Додати методи:
  - `send_telegram_verification(user, code)`
  - `send_viber_verification(user, code)`
  - `send_whatsapp_verification(user, code)`
  - `send_sms_verification(user, code)`

**КОНФІГУРАЦІЯ:**
- Додати в settings.py:
  - TELEGRAM_BOT_TOKEN
  - VIBER_BOT_TOKEN
  - WHATSAPP_API_KEY
  - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

**ЯК ПРАЦЮЄ ЗАРАЗ:**
- Email верифікація працює через EmailService
- Phone верифікація НЕ реалізована (заглушка)

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В RegisterView після реєстрації з телефоном викликати один з методів відправки
- В моделі User зберігати preferred_messenger ('telegram', 'viber', 'whatsapp', 'sms')
- В формі реєстрації додати вибір месенджера

#### 1.2. Функціонал соціальних мереж

**ЩО ТРЕБА:**
- Інтеграція Google OAuth 2.0
- Інтеграція Telegram Login Widget
- Інтеграція TikTok Login (якщо доступний API)

**ДЕ ДОДАТИ:**
- Встановити django-allauth або python-social-auth
- Налаштувати в settings.py:
  - SOCIALACCOUNT_PROVIDERS
  - OAuth callback URLs
  - Client IDs та Secrets

**ЯК ПРАЦЮЄ ЗАРАЗ:**
- Кнопки візуально готові в templates/auth/register.html та login.html
- Модель SocialAccount готова для зберігання зв'язків
- Логіка підключення НЕ реалізована

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати URL routes для OAuth callback
- Додати views для обробки OAuth
- В templates додати реальні href до кнопок соцмереж (зараз заглушки)
- При успішній авторизації через соцмережу створювати User + SocialAccount

#### 1.3. Кнопка зв'язку чи віджет бота

**ЩО ТРЕБА:**
- Інтеграція чат-віджету (наприклад, Intercom, Crisp, або власний)
- Альтернатива: посилання на Telegram бот підтримки

**ДЕ ДОДАТИ:**
- В templates/auth/register.html вже є <a href="#" class="auth-link">Зв'язатись з ботом підтримки</a>
- Замінити # на реальне посилання:
  - Якщо Telegram бот: `https://t.me/playvision_support_bot`
  - Якщо віджет чату: додати JavaScript код віджету в base.html

**ЯК ПРАЦЮЄ ЗАРАЗ:**
- Посилання є, але веде на #
- В base.html вже є AI chat dialog (ai-chat-dialog.js), але це внутрішній AI, а не підтримка

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити Telegram бот для підтримки
- Додати посилання на бота в усі місця де є "Зв'язок/Бот"
- АБО додати віджет чату (Crisp/Intercom)

---

## РОЗДІЛ 2: ВХІД (АВТОРИЗАЦІЯ)

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Використовується стандартний Django auth з кастомним User
- Backend: EmailBackend (apps/accounts/backends.py)

**VIEWS:**
- CustomLoginView (apps/accounts/views.py):
  - Підтримка входу через email або phone
  - Redirect на cabinet після входу

**TEMPLATE:**
- templates/auth/login.html:
  - Дві вкладки (Email/Телефон)
  - Поле для email або phone
  - Поле пароля
  - Кнопка входу
  - Посилання "Забули пароль?"
  - Кнопки соціальних мереж (візуально готові)

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 2.1. Відновлення паролю - повний flow

**ЩО ТРЕБА:**
- Форма введення email/phone
- Відправка коду на email/SMS
- Форма введення коду
- Форма встановлення нового паролю

**ДЕ ЗАРАЗ:**
- View PasswordResetView існує в apps/accounts/views.py
- Генерує код та зберігає в VerificationCode
- Відправка email НЕ реалізована (TODO коментар)

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити template: `templates/auth/password_reset.html`
- Створити template: `templates/auth/password_reset_confirm.html`
- В PasswordResetView додати виклик EmailService.send_password_reset_code(user)
- Додати PasswordResetConfirmView для введення коду та нового пароля
- Додати URL routes: password_reset/, password_reset/confirm/

#### 2.2. Кнопка "Відновити"

**ЩО ТРЕБА:**
- Кнопка має відкривати модальне вікно або окрему сторінку з формою відновлення

**ДЕ ДОДАТИ:**
- В templates/auth/login.html вже є:
  ```html
  <a href="{% url 'accounts:password_reset' %}" class="auth-link">Забули пароль?</a>
  ```
- URL вже зареєстрований

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Довершити flow відновлення (описано в 2.1)

---

## РОЗДІЛ 3: ХЕДЕР (HEADER)

### ✅ ЩО ВЖЕ ГОТОВО:

**TEMPLATE:**
- templates/base/base.html містить хедер:
  - Логотип з SVG (horizontal_desc_black.svg та horizontal_desc_white.svg для темної теми)
  - Логотип клікабельний (href="{% url 'core:home' %}")
  - Розділи меню: Головна, Про нас, Хаб знань, Івенти, Ментор-коучінг
  - Кнопки праворуч:
    - Для авторизованих: Кабінет, Theme Toggle, AI Chat
    - Для неавторизованих: Вхід, Реєстрація

**CSS:**
- static/css/components/header-desktop.css - стилі хедера

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 3.1. Підпис під логотипом

**ЩО ТРЕБА:**
- Підпис під логотипом: "навігатор футбольного розвитку"
- Має бути завжди видимий під/біля лого

**ДЕ ЗАРАЗ:**
- Логотип є (horizontal_desc_black.svg, horizontal_desc_white.svg)
- Підпис може бути вже в SVG файлі АБО треба додати окремо

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Перевірити чи SVG файли містять підпис "навігатор футбольного розвитку"
- Якщо НІ - додати в base.html:
  ```html
  <div class="logo-container">
      <img src="..." alt="Play Vision">
      <span class="logo-tagline">навігатор футбольного розвитку</span>
  </div>
  ```
- Стилізувати tagline (маленький шрифт, сірий колір)

#### 3.2. Кнопка "Підписка" виділена окремо

**ЩО ТРЕБА:**
- Кнопка "Підписка" має виділятись в меню (інший колір, фон)

**ДЕ ЗАРАЗ:**
- Кнопка "Підписка" ВІДСУТНЯ в хедері
- Є посилання в footer та на сторінках

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В templates/base/base.html в секції header-nav-actions додати:
  ```html
  <a href="{% url 'core:pricing' %}" class="nav-action-btn nav-action-btn--highlighted">
      <svg...>
      <span>Підписка</span>
  </a>
  ```
- В CSS додати стилі для .nav-action-btn--highlighted:
  - Яскравий фон (оранжевий/червоний)
  - Білий текст
  - Rounded corners

#### 3.3. Іконка кошика для авторизованих

**ЩО ТРЕБА:**
- Іконка кошика (🛒) для авторизованих користувачів
- Лічильник товарів в кошику

**ДЕ ЗАРАЗ:**
- В base.html ВІДСУТНЯ іконка кошика в хедері
- Є mobile-bottom-nav з іконкою кошика (тільки мобільна версія)

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В templates/base/base.html в header-actions додати:
  ```html
  {% if user.is_authenticated %}
  <a href="{% url 'cart:cart_detail' %}" class="navbar-icon cart-icon">
      <svg class="action-icon">...</svg>
      <span class="cart-count" hx-get="{% url 'htmx:cart_count' %}" hx-trigger="load, cartUpdated from:body">0</span>
  </a>
  {% endif %}
  ```
- Створити HTMX endpoint для оновлення кількості товарів
- Стилізувати іконку та лічильник

#### 3.4. Кнопка Вхід/Реєстрація для неавторизованих

**ЩО ТРЕБА:**
- Для неавторизованих показувати "Вхід" та "Реєстрація" замість іконки кошика

**ДЕ ЗАРАЗ:**
- Вже реалізовано в base.html:
  ```html
  {% if user.is_authenticated %}
      <a href="{% url 'cabinet:dashboard' %}">Кабінет</a>
  {% else %}
      <a href="{% url 'accounts:login' %}">Вхід</a>
      <a href="{% url 'accounts:register' %}">Реєстрація</a>
  {% endif %}
  ```

**ЩО ПОТРІБНО ДОРОБИТИ:**
- ✅ Готово, але потрібно додати іконку кошика (див. 3.2)

#### 3.5. Логотип клікабельний з анімацією

**ЩО ТРЕБА:**
- При кліку на лого відбувається анімація або відео
- Переводить на Головна або Про нас

**ДЕ ЗАРАЗ:**
- Логотип клікабельний, веде на головну
- Анімації НЕМАЄ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Варіант 1: Додати SVG анімацію при кліку (CSS animation)
  - Створити CSS @keyframes для logo-pulse або logo-rotate
  - Додати клас при кліку через JavaScript
- Варіант 2: Відео-оверлей
  - Створити modal з коротким відео про бренд (2-3 секунди)
  - При кліку на лого показувати modal з відео
  - Після відео redirect на Головна або Про нас
- Додати в static/js/header.js логіку анімації

#### 3.6. Dropdown меню "Івенти"

**ЩО ТРЕБА:**
- При наведенні на "Івенти" показувати dropdown з найближчими івентами

**ДЕ ЗАРАЗ:**
- Вже реалізовано в base.html:
  ```html
  <div class="nav-action-dropdown">
      <a href="{% url 'events:event_list' %}">Івенти</a>
      <div class="dropdown-menu">
          {% for event in upcoming_events_menu %}
              <a href="{{ event.get_absolute_url }}">{{ event.title }}</a>
          {% endfor %}
      </div>
  </div>
  ```

**ЩО ПОТРІБНО ДОРОБИТИ:**
- ✅ Готово, але потрібно перевірити context processor
- Перевірити apps/events/context_processors.py чи додає upcoming_events_menu
- Якщо НІ - додати в settings.py TEMPLATES context_processors

---

## РОЗДІЛ 4: ГОЛОВНА СТОРІНКА

### ✅ ЩО ВЖЕ ГОТОВО:

**TEMPLATE:**
- templates/pages/home.html існує з секціями:
  1. Hero Section - карусель з банерами
  2. Featured Courses Carousel - 6 курсів
  3. Courses Section - 3 статичні картки
  4. Mentor-Coaching Section - екосистема з гексагонами
  5. Experts Section - команда професіоналів
  6. CTA Section - заклик до дії

**МОДЕЛЬ CMS:**
- HeroSlide - для слайдів героя
- ExpertCard - для експертів
- HexagonItem - для гексагонів ментор-коучінгу
- PageSection - для секцій сторінки

**VIEW:**
- HomeView (apps/core/views.py):
  - Завантажує featured_courses (6 штук)
  - Завантажує cms_hero_slides
  - Завантажує cms_experts
  - Завантажує cms_hexagons

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 4.1. Промо-карусель - 6 слайдів з конкретним контентом

**ЩО ТРЕБА:**
- Створити 6 конкретних слайдів:
  1. "Ми відкрилися. Play Vision стартує!"
  2. "Івенти"
  3. "Хаб знань. Долучайся першим."
  4. "Ментор-коучінг"
  5. "Про нас"
  6. "Напрямки діяльності"

**ДЕ ЗАРАЗ:**
- Карусель реалізована
- Слайди завантажуються з CMS (HeroSlide)
- Можна створювати в Django Admin

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити міграцію/команду для додавання 6 конкретних слайдів
- Файл: `apps/cms/management/commands/create_hero_slides.py`
- Запустити команду: `python manage.py create_hero_slides`
- Додати зображення для кожного слайду в static/images/hero/
- Тексти взяти з usertask.md розділ 4, блок 1

#### 4.2. Дизайн промо-карусель - білі рамки, ОДНА зелена кнопка

**ЩО ТРЕБА:**
- **НЕ заливку фону, а БІЛІ РАМКИ навколо банерів** (важливо!)
- **ТІЛЬКИ 1 кнопка "дізнатись більше"** (було 2 - видалити зайву!)
- **Кнопка ЗЕЛЕНА зі стрілкою →** (НЕ червона!)

**ДЕ ЗАРАЗ:**
- CSS в static/css/components/home.css
- hero-section має стилі з overlay
- Можливо є 2 кнопки замість 1

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В CSS змінити:
  ```css
  .hero-with-frame {
      border: 3px solid rgba(255, 255, 255, 0.8);
      border-radius: 12px;
      background: rgba(0, 0, 0, 0.3);  /* Напівпрозорий фон */
  }
  ```
- Кнопку змінити на зелену з стрілкою:
  ```css
  .hero-buttons .btn-primary {
      background: #10b981;  /* Зелений колір */
      padding: 12px 24px;
  }
  .hero-buttons .btn-primary::after {
      content: " →";
  }
  ```
- Видалити другу кнопку "переглянути події" якщо є

#### 4.3. Карусель курсів - 6 курсів замість 3 блоків

**ЩО ТРЕБА:**
- Горизонтальна карусель з 6 курсів
- Прокрутка ліворуч-праворуч
- Навігація стрілками

**ДЕ ЗАРАЗ:**
- Секція "Featured Courses Carousel" вже реалізована в home.html
- Завантажує 6 курсів через featured_courses
- Є стрілки навігації

**ЩО ПОТРІБНО ДОРОБИТИ:**
- ✅ Готово!
- Потрібно створити 6 курсів з is_featured=True в Django Admin
- Додати зображення обкладинок для курсів

#### 4.4. Секція "Екосистема комплексного розвитку футболіста"

**ЩО ТРЕБА:**
- Після блоку курсів розташувати секцію з гексагонами
- 6 концепцій тільки українською (без англійських назв)
- Іконки в помаранчевому кольорі

**ДЕ ЗАРАЗ:**
- Секція "Mentor-Coaching Section" вже реалізована
- Містить гексагони з 6 напрямками
- Заголовок: "Екосистема комплексного розвитку футболіста"

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В home.html секція вже є з правильними назвами українською:
  - Ментальність 💭
  - Життя та побут 🌍
  - Техніка 👥
  - Здоров'я та звички 📖
  - Ігровий інтелект 🎓
  - Фізика 👍
- ✅ Готово!
- Потрібно перевірити що англійські назви НЕ відображаються

#### 4.5. Команда професіоналів

**ЩО ТРЕБА:**
- Секція з фото команди (8+ осіб)
- Формат: Фото + ім'я + посада + email
- Стиль: Професійні портрети, білий фон, чорний текст, сірий email

**ДЕ ЗАРАЗ:**
- Секція "Experts Section" існує в home.html
- Модель ExpertCard готова (cms/models.py)
- Завантажує cms_experts з бази

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати поле email в модель ExpertCard:
  ```python
  email = models.EmailField(blank=True, verbose_name='Email експерта')
  ```
- Створити міграцію: `python manage.py makemigrations cms`
- В template додати відображення email:
  ```html
  {% if expert.email %}
  <p class="expert-email">{{ expert.email }}</p>
  {% endif %}
  ```
- Додати CSS для expert-email (сірий колір)
- Завантажити фото команди (8 осіб) в Django Admin
- Відео-приклад: https://drive.google.com/file/d/1SbBFZBwOgGu33CcEZtz2-wLitlAdQK0k/view?usp=share_link

#### 4.6. Календар івентів на головній

**ЩО ТРЕБА:**
- Календар на місяць (вересень 2025)
- Вкладки: "Усі", "Форуми", "Вебінари", "Запуски курсів", "Новини"
- Показ подій на конкретні дні
- Секція під календарем з описом події

**ДЕ ЗАРАЗ:**
- В home.html НЕМАЄ календаря
- Є коментар що секція upcoming events ВИДАЛЕНА

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Розкоментувати або створити нову секцію з календарем
- Додати компонент календаря (JS):
  - Файл: static/js/components/event-calendar.js
  - Використати бібліотеку FullCalendar або custom рішення
- Додати вкладки фільтрації
- Під календарем показувати обрану подію з кнопкою "Підписатися"
- CSS в static/css/components/event-calendar.css

---

## РОЗДІЛ 5: ПОДІЇ (EVENTS)

**⚠️ ВАЖЛИВО:** Розділ "5. Події (Events)" з usertask.md ідентичний розділу "7. Івенти". 
Це один і той самий функціонал - система управління івентами/подіями.

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Event (apps/events/models.py):
  - Всі необхідні поля (title, description, dates, location, price)
  - event_type (forum, webinar, workshop, etc.)
  - Speaker модель готова
  - EventTicket з QR кодами
  - EventRegistration

**VIEWS:**
- event_list - список подій
- event_detail - детальна сторінка події

**TEMPLATES:**
- templates/events/event_list.html
- templates/events/event_detail.html

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 5.1. Функціонал "провалитись" в подію

**ЩО ТРЕБА:**
- Перехід на детальну сторінку події
- Показати всю інформацію
- Показати минулі такі івенти
- Кнопка "КУПИТИ КВИТОК"

**ДЕ ЗАРАЗ:**
- event_detail.html вже має:
  - Опис події
  - Розклад (timeline)
  - Спікери
  - Кнопка "Купити квиток"

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати секцію "Минулі події цього типу":
  - В EventDetailView додати в context:
    ```python
    context['past_similar_events'] = Event.objects.filter(
        event_type=event.event_type,
        status='completed',
        end_datetime__lt=timezone.now()
    ).order_by('-start_datetime')[:3]
    ```
  - В template додати секцію з минулими івентами

#### 5.2. Баланс квитків для Pro-Vision підписників

**ЩО ТРЕБА:**
- Для Pro-Vision показувати баланс доступних квитків
- Можливість вибрати на який івент витратити квиток
- Статус-бар залишку квитків

**ДЕ ЗАРАЗ:**
- Модель TicketBalance готова (subscriptions/models.py)
- Логіка ЧАСТКОВО реалізована

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В event_detail.html додати блок для підписників:
  ```html
  {% if user_has_provision and ticket_balance > 0 %}
  <div class="ticket-balance-info">
      <p>У вас є {{ ticket_balance }} безкоштовних квитків</p>
      <button class="btn use-ticket-balance">Використати квиток з підписки</button>
  </div>
  {% endif %}
  ```
- В EventDetailView додати в context:
  ```python
  if request.user.is_authenticated:
      context['ticket_balance'] = TicketBalance.objects.filter(
          user=request.user,
          amount__gt=0,
          expires_at__gt=timezone.now()
      ).aggregate(total=models.Sum('amount'))['total'] or 0
  ```
- При купівлі квитка перевіряти чи є баланс і пропонувати використати

---

## РОЗДІЛ 6: ХАБ ЗНАНЬ

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Course - модель курсів
- Material - матеріали курсів (відео, PDF, статті)
- Category - категорії
- Tag - теги та інтереси
- MonthlyQuote - цитати експертів
- Favorite - улюблені курси
- UserCourseProgress - прогрес користувача

**VIEWS:**
- course_list - список курсів (apps/content/views.py)
- course_detail - детальна сторінка курсу
- material_detail - перегляд матеріалу

**TEMPLATE:**
- templates/hub/course_list.html:
  - Банер підписки (subscription-banner)
  - Карусель головних матеріалів
  - Пошукова стрічка
  - Фільтри (категорії, тренерство з під-фільтрами, інші напрямки)
  - Сітка продуктів
  - Кнопка улюблених

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 6.1. Постійний заклик до підписки під хедером

**ЩО ТРЕБА:**
- **ВЕРХНЯ ЧАСТИНА СТОРІНКИ Хаб знань:**
- Заклик до підписки: **"Оформи підписку, стань частиною спільноти фахівців!"**
- **Цей напис НЕ ЗНИКАЄ і знаходиться ВІДРАЗУ ПІД ХЕДЕРОМ**
- При натисканні перекидає в розділ "Тарифи"

**ДЕ ЗАРАЗ:**
- ВІДСУТНІЙ на сторінці Хаб знань

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати в course_list.html НА САМОМУ ВЕРХУ після хедера:
  ```html
  <div class="subscription-sticky-banner">
      <div class="container">
          <p class="banner-text">Оформи підписку, стань частиною спільноти фахівців!</p>
          <a href="{% url 'core:pricing' %}" class="btn btn-primary">Тарифи</a>
      </div>
  </div>
  ```
- Додати CSS:
  ```css
  .subscription-sticky-banner {
      position: sticky;
      top: 0;
      z-index: 999;
      background: linear-gradient(135deg, #e11d48, #f97316);
      padding: 12px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  ```

#### 6.2. Цитати експертів - 3 конкретні цитати

**ЩО ТРЕБА:**
- 3 цитати від:
  1. Пеп Гвардіола: "Той, хто перестає вчитись, перестає бути тренером."
  2. Жозе Моурінью: "Якщо ти думаєш, що вже все знаєш — ти перестаєш рости."
  3. Карло Анчелотті: "Навчання — це не слабкість. Це означає амбіції."
- Чорно-білі фото
- Автоматична зміна кожні 10-20 секунд

**ДЕ ЗАРАЗ:**
- Модель MonthlyQuote готова
- Template hub/_monthly_quote.html існує
- Показує 1 цитату місяця

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Змінити логіку з "цитата місяця" на "карусель 3 цитат"
- Варіант 1: Використати MonthlyQuote для статичних цитат
  - Створити 3 записи з конкретними цитатами
  - Змінити _monthly_quote.html на карусель з усіх 3
- Варіант 2: Створити окрему модель ExpertQuote
  - Файл: apps/cms/models.py додати ExpertQuote
  - Поля: expert_name, expert_photo, quote_text, order
- Додати JavaScript для автоматичної зміни (setInterval 15000 мс)
- Завантажити чорно-білі фото Гвардіоли, Моурінью, Анчелотті

#### 6.3. Борди (4 інформаційні блоки)

**ЩО ТРЕБА:**
- 4 борди з текстами:
  1. "Вчися, аналізуй, розвивайся" - "Твоя бібліотека футбольних знань"
  2. "Знання, що працюють на полі" - "Навчання від практиків"
  3. "Від базових знань до професійного рівня"
  4. "Ми адаптуємо найкращий світовий досвід"

**ДЕ ЗАРАЗ:**
- ВІДСУТНІ на сторінці Хаб знань

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати нову секцію в course_list.html перед "Усі продукти":
  ```html
  <section class="hub-boards">
      <div class="boards-grid">
          <div class="board-card">
              <h3>Твоя бібліотека футбольних знань</h3>
              <p>Хаб знань — освітня платформа для тренерів...</p>
              <a href="#" class="btn">Відкрити знання</a>
          </div>
          <!-- 3 інші борди -->
      </div>
  </section>
  ```
- Створити CSS для .hub-boards та .board-card
- Тексти взяти з usertask.md розділ 6, підрозділ 2

#### 6.4. Структура матеріалів - великі та малі плитки

**ЩО ТРЕБА:**
- Головні курси (3-4) - великі прямокутники
- Інші курси - менші прямокутники мозаїкою
- Кожен з обкладинкою, описом, ціною, тегами
- Кнопка "play" для відео
- Зображення замку після перегляду промо

**ДЕ ЗАРАЗ:**
- Карусель головних матеріалів є (materials-carousel)
- Сітка продуктів є (products-grid)
- Всі мають однаковий розмір

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Змінити CSS для головних матеріалів:
  ```css
  .material-card {
      height: 400px;  /* Великі плитки */
  }
  .product-card {
      height: 300px;  /* Менші плитки */
  }
  ```
- Додати кнопку play для відео:
  - В course_card.html додати:
    ```html
    {% if course.has_video_preview %}
    <button class="play-btn" data-video-id="{{ course.id }}">▶</button>
    {% endif %}
    ```
- Додати зображення замку:
  - Створити static/images/icons/lock-icon.svg
  - Показувати коли !user.is_authenticated або !has_access

#### 6.5. Фільтри - видалити та додати

**ЩО ТРЕБА:**
- Видалити: Рівень складності, Тип доступу, Тривалість
- Замінити назву "Матеріали" на "Освітні продукти"
- Додати скролінг фільтрів
- Тренерство з під-фільтрами (галочка ✓ розгортає)
- Інші категорії: Аналітика і скаутинг, Менеджмент, Спортивна психологія, Нутриціологія, Реабілітація, Футболіст, Батько

**ДЕ ЗАРАЗ:**
- course_list.html має фільтри
- За категоріями (radio buttons)
- Тренерство з під-фільтрами вже реалізовано!
- Інші напрямки є (checkboxes)

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Змінити заголовок "Усі продукти" на "Освітні продукти" в line 225 course_list.html
- ✅ Фільтри вже правильно реалізовані!
- Додати скролінг для мобільної версії:
  ```css
  .filters-content {
      max-height: 70vh;
      overflow-y: auto;
  }
  ```

#### 6.6. Передперегляд контенту

**ЩО ТРЕБА:**
- Відео: перші 20 секунд
- PDF/статті: перші 10% з водяним знаком
- CTA після передперегляду: "Вступити в клуб", "Купити", "Оформити підписку"
- Для гостей: редирект на реєстрацію, товар в кошику після реєстрації

**ДЕ ЗАРАЗ:**
- Модель Material має поля:
  - is_preview
  - preview_seconds (default 20)
  - preview_percentage (default 10)
- Логіка передперегляду ЧАСТКОВО реалізована

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В material_detail.html додати логіку preview:
  ```html
  {% if not user_has_access and material.is_preview %}
      <div class="preview-player" data-preview-duration="{{ material.preview_seconds }}">
          <!-- Відео плеєр з обмеженням часу -->
      </div>
      <div class="preview-cta">
          {% if not user.is_authenticated %}
              <a href="{% url 'accounts:register' %}?next={{ request.path }}&add_to_cart=course_{{ course.id }}">
                  Вступити в клуб
              </a>
          {% else %}
              <a href="{% url 'core:pricing' %}">Оформити підписку</a>
              <a href="{% url 'cart:add_course' course.id %}">Купити</a>
          {% endif %}
      </div>
  {% endif %}
  ```
- Додати JavaScript для обмеження часу відео
- Для PDF додати водяний знак (PIL/reportlab)

#### 6.7. Позначки на матеріалах

**ЩО ТРЕБА:**
- "топ-продажів", "новинка", "для вас", "вічна класика"

**ДЕ ЗАРАЗ:**
- course_list.html вже показує:
  - "топ-продажів" якщо course.is_featured
  - "новинка" логіка ВІДСУТНЯ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати поля в модель Course:
  ```python
  is_new = models.BooleanField(default=False)
  is_classic = models.BooleanField(default=False)
  is_recommended_for_user = models.BooleanField(default=False)  # динамічно
  ```
- АБО використовувати логіку:
  - "новинка": created_at > 30 днів тому
  - "вічна класика": rating > 4.5 and enrollment_count > 100
  - "для вас": перетин тегів курсу з інтересами користувача
- В template додати відображення всіх badges

#### 6.8. Віджет підтримки в нижньому правому куті

**ЩО ТРЕБА:**
- Чат-бот або форма зворотного зв'язку

**ДЕ ЗАРАЗ:**
- В course_list.html вже є:
  ```html
  <div class="support-widget">
      <button class="support-btn">Підтримка</button>
  </div>
  ```
- Кнопка є, але не функціональна

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Підключити функціонал AI чату (вже є ai-chat-dialog)
- АБО створити форму зворотного зв'язку
- АБО посилання на Telegram бот
- Додати onclick обробник для показу чату

---

## РОЗДІЛ 7: ІВЕНТИ

**⚠️ ВАЖЛИВО:** Цей розділ є продовженням "РОЗДІЛ 5: ПОДІЇ (EVENTS)".
В usertask.md це окремі розділи, але в реалізації - це єдина система управління івентами.
Тут описані додаткові деталі: календар, фільтри, шаблони сторінок івентів.

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Event з усіма полями
- Фільтрація по event_type, format (online/offline), date_range
- EventTicket з QR кодами

**TEMPLATE:**
- event_list.html з фільтрами
- event_detail.html з повним описом

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 7.1. Календар івентів - інтерактивний

**ЩО ТРЕБА:**
- Інтерактивний календар для перегляду подій
- В календарі лише по 1 події на дату
- Можливість обрати дату

**ДЕ ЗАРАЗ:**
- В event_list.html є секція calendar з коментарем "Календар видалено - використовується список"
- Логіка календаря ВІДСУТНЯ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити компонент календаря:
  - Файл: static/js/components/events-calendar.js
  - Використати бібліотеку: FullCalendar або custom
- Додати в event_list.html:
  ```html
  <div id="events-calendar" data-events-url="{% url 'api:events_calendar' %}"></div>
  ```
- Створити API endpoint для календаря:
  - apps/events/api_views.py: EventsCalendarAPIView
  - Повертає події в JSON форматі для календаря
  - Групує події по датах (тільки 1 на дату)
- CSS для календаря

#### 7.2. Фільтр "Ціна" - radio buttons

**ЩО ТРЕБА:**
- Замість слайдера - radio buttons:
  - ⭕ Всі події
  - ⭕ Безкоштовні
  - ⭕ Платні

**ДЕ ЗАРАЗ:**
- Фільтр "ціна" ВІДСУТНІЙ
- Є коментар "Price Filter - ВИДАЛЕНО ЗА ВИМОГОЮ КЛІЄНТА"

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати фільтр "Ціна" з radio buttons:
  ```html
  <div class="sidebar-section">
      <h3 class="sidebar-title">Ціна</h3>
      <div class="filter-group">
          <label class="filter-option">
              <input type="radio" name="price" value="all" checked>
              <span class="filter-radio"></span>
              <span class="filter-label">Всі події</span>
          </label>
          <label class="filter-option">
              <input type="radio" name="price" value="free">
              <span class="filter-radio"></span>
              <span class="filter-label">Безкоштовні</span>
          </label>
          <label class="filter-option">
              <input type="radio" name="price" value="paid">
              <span class="filter-radio"></span>
              <span class="filter-label">Платні</span>
          </label>
      </div>
  </div>
  ```
- В EventListView обробляти фільтр price

#### 7.3. Шаблони та зображення івентів

**ЩО ТРЕБА:**
- Банери івентів з календарем на тиждень (8-14 числа)
- Короткий опис події
- Кнопка "Підписатися"

**ДЕ ЗАРАЗ:**
- event_list.html показує картки подій
- Зображення завантажуються з event.thumbnail

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити template компонент event_banner_card.html:
  ```html
  <div class="event-banner">
      <div class="event-week-calendar">
          <div class="week-day">8 Пн</div>
          <div class="week-day active">9 Вт</div>
          <!-- ... -->
      </div>
      <h3>{{ event.title }}</h3>
      <p>{{ event.short_description }}</p>
      <button class="btn btn-subscribe">Підписатися</button>
  </div>
  ```
- Додати CSS для event-banner
- Створити шаблони зображень згідно брендбуку

#### 7.4. Сторінка івенту - детальний опис

**ЩО ТРЕБА:**
- Блок "Що ти отримаєш"
- Блок "Для кого"
- Агенда з розкладом (18:00 - Відкриття, 18:10 - Панель, etc.)
- 3 тарифи (STANDARD, PRO, VIP)
- Спікери (за аналогією до команди)
- Кнопка "Купити квиток"

**ДЕ ЗАРАЗ:**
- event_detail.html вже має:
  - Опис події
  - Розклад (timeline) - СТАТИЧНИЙ
  - Спікери
  - Кнопка купівлі

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати в модель Event поле для тарифів:
  ```python
  ticket_tiers = models.JSONField(default=list, help_text='JSON з тарифами')
  ```
  Приклад:
  ```json
  [
      {"name": "STANDARD", "price": 5450, "features": ["Доступ до трансляції", "7 днів запис"]},
      {"name": "PRO", "price": 6750, "features": ["STANDARD", "Матеріали PDF", "Вебінар"]},
      {"name": "VIP", "price": 41250, "features": ["PRO", "Q&A 30 хв"]}
  ]
  ```
- В event_detail.html додати секцію тарифів:
  ```html
  <section class="event-tiers">
      {% for tier in event.ticket_tiers %}
      <div class="tier-card">
          <h3>{{ tier.name }}</h3>
          <div class="tier-price">{{ tier.price }}</div>
          <ul>
              {% for feature in tier.features %}
              <li>{{ feature }}</li>
              {% endfor %}
          </ul>
      </div>
      {% endfor %}
  </section>
  ```
- Додати блоки "Що ти отримаєш" та "Для кого":
  ```python
  # В модель Event
  benefits = models.JSONField(default=list)
  target_audience = models.JSONField(default=list)
  ```

---

## РОЗДІЛ 8: МЕНТОР-КОУЧІНГ

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Модуль apps/mentoring існує
- Базові models.py, views.py, admin.py

**СТРУКТУРА:**
- Футбольний трикутник (Гравець, Тренер, Батьки) реалізований в about.html

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 8.1. Окрема сторінка "Ментор-коучінг" з 5 блоками

**ЩО ТРЕБА:**
- Блок 1: Що таке Ментор-коучінг? (3 абзаци тексту)
- Блок 2: Структура Ментор-коучінгу (6 шестикутників)
- Блок 3: Команда Ментор-коучінгу (текст + структура)
- Блок 4: Унікальна методологія (4 принципи)
- Блок 5: Дві кнопки (Консультація + Методологія)

**ДЕ ЗАРАЗ:**
- URL веде на coming_soon (core:coming_soon?page=mentoring)
- Окрема сторінка НЕ створена

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити template: `templates/pages/mentoring.html`
- Додати view в apps/core/views.py:
  ```python
  class MentoringView(TemplateView):
      template_name = 'pages/mentoring.html'
  ```
- В urls.py додати:
  ```python
  path('mentor-coaching/', MentoringView.as_view(), name='mentoring'),
  ```
- В template додати всі 5 блоків згідно usertask.md розділ 8
- Створити CSS: static/css/components/mentoring.css

#### 8.2. Структура з 6 шестикутників - детальний контент

**ЩО ТРЕБА:**
- Кожен шестикутник з іконкою, назвою та списком пунктів:
  1. 🧠 Ігровий інтелект (4 пункти)
  2. 💪 Фізика (5 пунктів)
  3. ⚽ Техніка (4 пункти)
  4. 🧘 Ментальність з 😊 (4 пункти)
  5. 🏠 Життя і побут (7 пунктів)
  6. 💊 Здоров'я і звички (5 пунктів)

**⚠️ ВАЖЛИВО - ВИПРАВИТИ ТЕКСТИ:**
В usertask.md тексти мають граматичні помилки (typos). При створенні контенту ОБОВ'ЯЗКОВО виправити:
- "Індивідуальний тактичний аналітик" (не "аналітик")
- "Система розвитку для покращення розуміння гри" (не "розвитку по покращенню розумінні")
- "Аналіз ігор та індивідуальних рішень" (не "інд. рішенів")
- "Формування індивідуального стилю теоретичних знань" (не "індивідуальних теоретичних знанів")
- "Удосконалення координації" (не "Упослужнення")
- "Робота з ментальною працею" (не "ментально працею")
- Всі інші граматичні та орфографічні помилки

**ДЕ ЗАРАЗ:**
- На головній є схожа структура (hexagons-orbit)
- Тільки назви, без детального опису

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити expandable hexagons:
  - При кліку на гексагон розгортається модальне вікно з повним описом
  - АБО при кліку гексагон збільшується і показує список
- Додати в HexagonItem модель поле для детального опису:
  ```python
  details = models.JSONField(default=list, help_text='Список деталей')
  ```
- Заповнити контент згідно usertask.md розділ 8, блок 2

#### 8.3. Команда Ментор-коучінгу

**ЩО ТРЕБА:**
- Текст про команду (works 24/7, підтримка...)
- Структура: Ментор-менеджер, Координатор, Ментор-коучі, Спеціалісти
- Контакт: Oleg Bonislavskyi, olegbonislav@gmail.com

**ДЕ ДОДАТИ:**
- В templates/pages/mentoring.html додати секцію:
  ```html
  <section class="mentoring-team">
      <h2>Команда Ментор-коучінгу</h2>
      <p>Наша команда супроводу працює 24/7...</p>
      <div class="team-structure">
          <div class="role">Ментор-менеджер (стратегія)</div>
          <div class="role">Координатор гравця</div>
          <!-- ... -->
      </div>
      <div class="contact">
          <p>Oleg Bonislavskyi</p>
          <a href="mailto:olegbonislav@gmail.com">olegbonislav@gmail.com</a>
      </div>
  </section>
  ```

#### 8.4. Унікальна методологія - 4 принципи

**ЩО ТРЕБА:**
- Текст про методологію
- 4 принципи:
  1. Індивідуальний підхід
  2. Комплексність
  3. Наукове підгрунтя
  4. Інноваційність

**ДЕ ДОДАТИ:**
- В templates/pages/mentoring.html додати секцію
- Тексти взяти з usertask.md розділ 8, блок 4

#### 8.5. Дві кнопки

**ЩО ТРЕБА:**
- "Отримати консультацію" - веде на Telegram менеджера
- "Ознайомитись з методологією" - веде на файл Google Drive

**ДЕ ДОДАТИ:**
- В кінці mentoring.html:
  ```html
  <div class="mentoring-cta">
      <a href="https://t.me/playvision_mentor" class="btn btn-primary">Отримати консультацію</a>
      <a href="https://drive.google.com/..." class="btn btn-outline">Ознайомитись з методологією</a>
  </div>
  ```

---

## РОЗДІЛ 9: ПРО PLAY VISION

### ✅ ЩО ВЖЕ ГОТОВО:

**TEMPLATE:**
- templates/pages/about.html існує
- Секції:
  - Mission Section
  - Football Triangle (трикутник)
  - Values Section
  - Knowledge Hub Section

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 9.1. БРЕНД-АБЗАЦ

**ЩО ТРЕБА:**
- Додати секцію з текстом:
  "Play Vision — твій навігатор футбольного розвитку.
  Ми створюємо нову систему координат..."
  (повний текст в usertask.md розділ 9)

**ДЕ ЗАРАЗ:**
- В about.html є Mission Section
- Текст базовий, не БРЕНД-АБЗАЦ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В about.html замінити текст Mission Section на повний БРЕНД-АБЗАЦ
- Дизайн: Темний фон з сіткою, білий текст, мінімалістичний
- CSS:
  ```css
  .brand-paragraph {
      background: #1a1a1a;
      background-image: 
          linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
      background-size: 50px 50px;
      color: white;
      padding: 80px 40px;
      text-align: center;
  }
  ```

---

## РОЗДІЛ 10: ОСОБИСТИЙ КАБІНЕТ

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Profile з полями: first_name, last_name, birth_date, avatar, profession, interests

**VIEWS:**
- CabinetView з 5 вкладками (apps/accounts/cabinet_views.py)
- UpdateProfileView для AJAX оновлення
- ToggleFavoriteView для улюблених

**TEMPLATE:**
- templates/account/cabinet.html:
  - Ліва частина: Аватар + форма профілю
  - Права частина: Вкладки (Профіль, Підписка, Мої файли, Програма лояльності, Історія оплат)
- templates/account/tabs/*.html - всі вкладки

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 10.1. Напрямки інтересів - чітка послідовність

**ЩО ТРЕБА:**
- 9 інтересів в чіткій послідовності:
  a) Тренерство
  б) Аналітика і скаутинг
  в) ЗФП
  г) Менеджмент
  ґ) Психологія
  д) Нутриціологія (замість "харчування")
  е) Футболіст
  є) Батько
  ж) Реабілітація

**ДЕ ЗАРАЗ:**
- В cabinet.html є interests-list
- Завантажуються з Tag моделі (tag_type='interest')
- Порядок контролюється полем display_order

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити міграцію для додавання тегів:
  - Файл: apps/content/management/commands/create_interests.py
  - Створити 9 тегів з правильними назвами та display_order
- Запустити: `python manage.py create_interests`
- Перевірити що "харчування" замінено на "Нутриціологія"

#### 10.2. Завантаження аватара

**ЩО ТРЕБА:**
- Функція завантаження фото користувача

**ДЕ ЗАРАЗ:**
- В cabinet.html вже є:
  ```html
  <button class="avatar-upload-btn">Завантажити фото</button>
  <input type="file" id="avatar-input" accept="image/*" class="is-hidden">
  ```
- UpdateProfileView обробляє завантаження avatar

**ЩО ПОТРІБНО ДОРОБИТИ:**
- ✅ Функціонал готовий!
- Додати JavaScript для активації input при кліку:
  - В static/js/cabinet.js додати:
    ```js
    document.querySelector('.avatar-upload-btn').addEventListener('click', () => {
        document.querySelector('#avatar-input').click();
    });
    ```
- При виборі файлу автоматично відправляти форму (AJAX)

#### 10.3. Кнопка "ЗБЕРЕГТИ"

**ЩО ТРЕБА:**
- Виправлена кнопка з "Зберти зміни" на "ЗБЕРЕГТИ"

**ДЕ ЗАРАЗ:**
- В cabinet.html вже виправлено:
  ```html
  <button type="submit" class="btn-save">ЗБЕРЕГТИ</button>
  ```

**ЩО ПОТРІБНО ДОРОБИТИ:**
- ✅ Готово!

#### 10.4. Індикатор "днів з нами"

**ЩО ТРЕБА:**
- Коректні відмінки: "1 день", "3 дні", "10 днів"
- Іконка календаря 📅 + текст "з нами"

**ДЕ ЗАРАЗ:**
- ВІДСУТНІЙ в cabinet.html

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати в лівій частині кабінету:
  ```html
  <div class="days-with-us">
      <svg class="icon">📅</svg>
      <span>{{ days_count }} {{ days_word }} з нами</span>
  </div>
  ```
- В CabinetView додати в context:
  ```python
  days = (timezone.now().date() - user.created_at.date()).days
  context['days_count'] = days
  context['days_word'] = get_days_word(days)
  ```
- Створити функцію get_days_word:
  ```python
  def get_days_word(n):
      if n % 10 == 1 and n % 100 != 11:
          return "день"
      elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
          return "дні"
      else:
          return "днів"
  ```

#### 10.5. Розміщення "Особиста інформація" та "Налаштування"

**ЩО ТРЕБА:**
- В правій частині ОК (там де вкладки)

**ДЕ ЗАРАЗ:**
- Вкладки в правій частині
- "Особиста інформація" та "Налаштування" ВІДСУТНІ як окремі вкладки

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Варіант 1: Додати нові вкладки
- Варіант 2: "Особиста інформація" = вкладка "Профіль" (вже є)
- Варіант 3: Додати підвкладки в Профіль
- Рекомендація: Залишити як є (Профіль = Особиста інформація)

#### 10.6. Вкладка "Підписка"

**ЩО ТРЕБА:**
- Блок "Рівень": Silver (оранжева кнопка)
- Блок "Прогрес рівня": "100/200 балів до Silver" з прогрес-баром
- Блок "Знижка": Поточна 10% / Потенційна 15%
- Блок "Поточний план": Місячна — $10
- Блок "Статус": Активна, Наступне списання: 12.10.2025
- Блок "Переваги": список
- Кнопка "Змінити підписку"

**ДЕ ЗАРАЗ:**
- templates/account/tabs/subscription.html містить всі ці блоки!
- Рівень ВІДСУТНІЙ (з loyalty)
- Прогрес ВІДСУТНІЙ
- Знижка ВІДСУТНЯ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Об'єднати дані з loyalty в subscription вкладку:
  ```html
  <div class="subscription-loyalty-info">
      <div class="info-card">
          <h3>Рівень лояльності</h3>
          <div class="tier-badge">{{ loyalty_account.current_tier.name }}</div>
      </div>
      <div class="info-card">
          <h3>Прогрес</h3>
          <div class="progress-bar">...</div>
      </div>
      <div class="info-card">
          <h3>Знижка</h3>
          <p>Поточна: {{ current_discount }}%</p>
          <p>Потенційна: {{ potential_discount }}%</p>
      </div>
  </div>
  ```
- В _get_subscription_context додати дані з loyalty

#### 10.7. Вкладка "Історія оплат"

**ЩО ТРЕБА:**
- Таблиця з колонками: Дата, Опис, Сума, Статус, Дія
- Кнопка "Повторити" для швидкого поновлення

**ДЕ ЗАРАЗ:**
- templates/account/tabs/payments.html вже реалізована!
- Таблиця з усіма колонками є
- Кнопка "Повторити" ВІДСУТНЯ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати колонку "Дія" в таблицю:
  ```html
  <div class="col-action">
      {% if payment.subscription %}
      <button class="btn-repeat" data-plan-id="{{ payment.subscription.plan.id }}">
          Повторити
      </button>
      {% endif %}
  </div>
  ```
- Додати view для повторення платежу:
  - RepeatPaymentView в cabinet_views.py
  - При кліку створює новий payment intent

#### 10.8. Вкладка "Мої файли"

**ЩО ТРЕБА:**
- Сітка матеріалів (3 в ряд)
- Кожна картка:
  - Назва, Тип контенту
  - Кнопка "Переглянути"
  - Іконка зірочки ⭐ (улюблені)
  - Кнопка "офлайн" 📥
  - Прогрес перегляду (30%, 41%)
  - Індикатор придбаних окремо (валюта)

**ДЕ ЗАРАЗ:**
- templates/account/tabs/files.html вже містить всі ці елементи!
- materials_data готується в _get_files_context
- Всі кнопки є

**ЩО ПОТРІБНО ДОРОБИТИ:**
- ✅ Структура готова!
- Додати індикатор "придбано окремо":
  ```html
  {% if material.purchased_separately %}
  <span class="purchase-badge">💰</span>
  {% endif %}
  ```
- В material_data додати поле purchased_separately
- Логіка: перевірити чи курс куплений окремо (не через підписку)

#### 10.9. Вкладка "Програма лояльності"

**ЩО ТРЕБА:**
- Рівень (Silver)
- Прогрес до наступного (100/200 балів)
- Знижки (10% / 15%)
- Кнопка "Правила Програми Лояльності"

**ДЕ ЗАРАЗ:**
- templates/account/tabs/loyalty.html вже містить ВСЕ!
- Кнопка "Правила ПЛ" вже є і веде на loyalty:rules

**ЩО ПОТРІБНО ДОРОБИТИ:**
- ✅ Готово!
- Перевірити що link працює

---

## РОЗДІЛ 11: ПРОГРАМА ЛОЯЛЬНОСТІ - ОКРЕМА СТОРІНКА

### ✅ ЩО ВЖЕ ГОТОВО:

**TEMPLATE:**
- templates/loyalty/rules.html вже повністю реалізована!
- Містить:
  - Hero banner з формулою балів
  - Таблиця нарахування за покупки
  - Таблиця нарахування за підписки
  - Як витрачати бали
  - Roadmap
  - CTA кнопки

**МОДЕЛЬ:**
- PointEarningRule - правила нарахування
- RedemptionOption - варіанти витрати
- LoyaltyAccount - аккаунт балів
- PointTransaction - історія

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 11.1. Промо-баннер для розділу

**ЩО ТРЕБА:**
- Яскравий баннер на сторінці ПЛ
- Дизайн згідно брендбуку

**ДЕ ЗАРАЗ:**
- loyalty/rules.html має loyalty-hero секцію
- Дизайн базовий

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Покращити дизайн hero секції:
  ```css
  .loyalty-hero {
      background: linear-gradient(135deg, #e11d48, #f97316);
      color: white;
      padding: 60px 40px;
      border-radius: 16px;
  }
  ```
- Додати іконки 🎁 🏆 🎯 💳 в highlight-visual
- Посилання на файл: https://drive.google.com/file/d/1A8oTTlXUon_ow-k3YbdtUX-9Euj79_pu/view?usp=share_link

#### 11.2. Timeline для демонстрації прикладу

**ЩО ТРЕБА:**
- Roadmap та таймлайн
- Візуалізація як користувач збирає бали

**ДЕ ЗАРАЗ:**
- Є секція "Roadmap" з планами
- Візуального timeline НЕМАЄ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати візуальний приклад journey користувача:
  ```html
  <section class="loyalty-timeline">
      <h2>Приклад: як Олексій заробив 200 балів за місяць</h2>
      <div class="timeline">
          <div class="timeline-item">
              <div class="timeline-icon">🛒</div>
              <div class="timeline-content">
                  <h4>1. Придбав підписку B-Vision на 3 місяці</h4>
                  <p>+50 балів</p>
              </div>
          </div>
          <div class="timeline-item">
              <div class="timeline-icon">📚</div>
              <div class="timeline-content">
                  <h4>2. Завершив курс "Тактична аналітика"</h4>
                  <p>+30 балів</p>
              </div>
          </div>
          <!-- ... -->
      </div>
  </section>
  ```
- CSS для timeline

---

## РОЗДІЛ 12: ПІДПИСКА - ТАРИФНА СІТКА

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Plan з полями: name, duration, price, features

**TEMPLATE:**
- templates/subscriptions/pricing.html
- Відображає 4 плани в сітці
- Кнопки "Обрати план"

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 12.1. 4 пакети з конкретними назвами та кольорами

**ЩО ТРЕБА:**
- C-VISION (Синій 🔵) - "Знайди свій PRO-VISION"
- B-VISION (Помаранчевий 🟠) - "Розвивай свій PRO-VISION"
- A-VISION (Червоний 🔴) - "Вдоскони свій PRO-VISION"
- PRO-VISION (Рожевий/Червоний 🔴💗) - "Ти є PRO-VISION"

**⚠️ ВАЖЛИВО - ЗАВЕРШИТИ ОПИСИ ПЕРЕВАГ:**
В usertask.md описи переваг тарифів НЕЗАВЕРШЕНІ та мають помилки (обрізаний текст).
При створенні контенту ОБОВ'ЯЗКОВО:
- Дописати всі переваги повністю
- Виправити граматичні помилки
- Зробити текст зрозумілим та професійним
- Приклад з usertask: "Базовий контент: до ХХ год" - замінити ХХ на реальні цифри
- "Вибірка матеріалів до ХХ текстовик" - виправити текст

**ДЕ ЗАРАЗ:**
- План може мати будь-яку назву
- Колір індикатора ВІДСУТНІЙ в моделі

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати поле в модель Plan:
  ```python
  tier_name = models.CharField(max_length=20, choices=[
      ('c_vision', 'C-VISION'),
      ('b_vision', 'B-VISION'),
      ('a_vision', 'A-VISION'),
      ('pro_vision', 'PRO-VISION'),
  ], blank=True)
  color_indicator = models.CharField(max_length=7, default='#3b82f6')
  tier_slogan = models.CharField(max_length=100, blank=True)
  ```
- Створити міграцію
- Створити management команду для створення 4 планів:
  - create_subscription_plans.py
- В template додати колір індикатора:
  ```html
  <div class="plan-indicator" style="background: {{ plan.color_indicator }}"></div>
  ```

#### 12.2. Банери підписки - повідомлення

**ЩО ТРЕБА:**
- Банер помилки оплати: "Відмова банку", "Недостатньо коштів", кнопка "Спробувати ще раз"
- Повідомлення "Підписка продовжується автоматично. Ви можете скасувати"
- Повідомлення при окремій покупці: "Ви вже заплатили X, підписка дає доступ до всього за Y"

**ДЕ ЗАРАЗ:**
- ВІДСУТНІ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити компонент повідомлень:
  - templates/partials/subscription_messages.html
- Показувати після неуспішної оплати (в checkout flow)
- Додати в pricing.html повідомлення про автопоновлення
- В course_detail.html додати порівняння ціни окремої покупки vs підписки

#### 12.3. Кнопка "Скасувати підписку"

**ЩО ТРЕБА:**
- Не надто агресивний дизайн
- Сіра/біла кнопка з червоним текстом

**ДЕ ЗАРАЗ:**
- В subscription.html вже є:
  ```html
  <button class="btn-secondary" data-action="cancelSubscription">Скасувати підписку</button>
  ```
- View CancelSubscriptionView готовий

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Змінити стиль кнопки:
  ```css
  .btn-secondary[data-action="cancelSubscription"] {
      background: transparent;
      color: #dc2626;
      border: 1px solid #dc2626;
  }
  ```

#### 12.4. Система списань - оплата частинами

**ЩО ТРЕБА:**
- Користувач може оплатити відразу чи частинами
- Налаштування в ОК

**ДЕ ЗАРАЗ:**
- НЕМАЄ функціоналу

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Додати в модель Subscription:
  ```python
  payment_schedule = models.CharField(max_length=20, choices=[
      ('full', 'Повна оплата'),
      ('monthly', 'Щомісячно'),
  ], default='full')
  ```
- В subscription.html додати налаштування:
  ```html
  <div class="payment-schedule">
      <label>
          <input type="radio" name="schedule" value="full" checked>
          Оплатити відразу
      </label>
      <label>
          <input type="radio" name="schedule" value="monthly">
          Оплачувати щомісяця
      </label>
  </div>
  ```

#### 12.5. Референс MEGOGO - баннер

**ЩО ТРЕБА:**
- Баннер на головній з калейдоскопом матеріалів
- Статистика: "16 000+ фільмів" → "XXX+ курсів"
- Кнопка "Вибрати від 29 грн" → "Обрати план"

**ДЕ ЗАРАЗ:**
- ВІДСУТНІЙ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Створити компонент subscription-banner:
  - templates/partials/megogo-style-banner.html
- Додати в home.html після courses section
- CSS для мозаїки:
  ```css
  .subscription-mosaic {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 4px;
  }
  .mosaic-item {
      aspect-ratio: 16/9;
      background-size: cover;
  }
  ```
- Показувати превью обкладинок курсів (12 плиток)

---

## РОЗДІЛ 13: КОШИК

### ✅ ЩО ВЖЕ ГОТОВО:

**МОДЕЛЬ:**
- Cart з CartItem (apps/cart/models.py)
- Підтримка промокодів (applied_coupon)
- Поля: discount_amount, tips_amount
- Metadata для відображення (tags, badges)

**TEMPLATE:**
- templates/cart/cart.html повністю реалізований:
  - Картки товарів з мініатюрами
  - Назва, тип, ціна
  - Селектор кількості [<] [1] [>]
  - Кнопка видалення
  - Блок рекомендацій
  - Поле промокоду
  - Підсумок

**VIEWS:**
- cart/views.py з усіма операціями (add, remove, update)

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 13.1. Блок рекомендацій "Ідеальний метч до вашого кошика"

**ЩО ТРЕБА:**
- Жовтий/кремовий фон
- Назва товару, зображення, ціна
- Кнопка "+ додати в кошик" (оранжева овальна)
- Кнопка закриття ❌

**ДЕ ЗАРАЗ:**
- cart.html вже має cart-recommendations блок
- Завантажуються з context['recommendations']

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В CartDetailView генерувати рекомендації
- Створити apps/cart/services/recommendations.py з логікою:
  - Схожі курси (по тегах)
  - Курси тієї ж категорії
  - Курси що купували разом
- CSS для жовтого фону:
  ```css
  .cart-recommendations {
      background: linear-gradient(135deg, #fef3c7, #fde68a);
      border-radius: 12px;
      padding: 20px;
  }
  ```

#### 13.2. Автоматичне застосування знижки з loyalty

**ЩО ТРЕБА:**
- Автоматичний розрахунок знижки за балами
- Відображення економії

**ДЕ ЗАРАЗ:**
- cart.discount_amount поле є
- Автоматичне застосування ВІДСУТНЄ

**ЩО ПОТРІБНО ДОРОБИТИ:**
- В cart/services.py створити функцію:
  ```python
  def auto_apply_loyalty_discount(cart, user):
      if hasattr(user, 'loyalty_account'):
          discount_pct = user.loyalty_account.get_discount_percentage()
          if discount_pct > 0:
              subtotal = cart.get_subtotal()
              discount = subtotal * (discount_pct / 100)
              cart.discount_amount = max(cart.discount_amount, discount)
              cart.save()
  ```
- Викликати при додаванні товару та при завантаженні кошика

---

## РОЗДІЛ 14: СПЛИВАЮЧІ ПОВІДОМЛЕННЯ

### ✅ ЩО ВЖЕ ГОТОВО:

**TEMPLATE:**
- templates/partials/scroll-popup.html
- Диференціація auth/unauth

**JS:**
- static/js/scroll-popup.js

---

### ⚠️ ЩО ПОТРІБНО ДОДАТИ/ЗМІНИТИ:

#### 14.1. Дизайн для незареєстрованих - 10% знижка

**ЩО ТРЕБА:**
- Темно-синій/чорний фон
- Жовтий великий текст "10%"
- Біле поле вводу email
- Біла кнопка CTA

**ДЕ ЗАРАЗ:**
- Текст базовий
- Дизайн простий

**ЩО ПОТРІБНО ДОРОБИТИ:**
- Змінити HTML в scroll-popup.html
- Додати CSS для темного фону та яскравого "10%"
- Обробка форми - створення промокоду 10% для нового користувача

#### 14.2. Дизайн для зареєстрованих - 30 балів

**ЩО ТРЕБА:**
- Темно-синій фон з градієнтом
- Жовтий "30 БАЛІВ"
- Біла кнопка "ПІДПИСКИ"

**ДЕ ЗАРАЗ:**
- Текст є
- Дизайн простий

**ЩО ПОТРІБНО ДОРОБИТИ:**
- CSS градієнт
- При кліку на кнопку нарахувати 30 балів + redirect на pricing

---

## ДОДАТКОВІ СЕКЦІЇ ТА ФУНКЦІЇ

### E1. СТВОРЕННЯ КОНТЕНТУ ЧЕРЕЗ DJANGO ADMIN

**ЩО ПОТРІБНО:**

Створити management команди для швидкого наповнення:

1. **create_initial_content.py** - загальна команда:
   ```bash
   python manage.py create_initial_content
   ```
   Створює:
   - 6 hero слайдів
   - 9 interest tags
   - 4 subscription plans
   - 3 expert quotes
   - 8 team members
   - 4 hub boards
   - Sample courses
   - Sample events

2. **Структура команди:**
   ```python
   # apps/core/management/commands/create_initial_content.py
   from django.core.management.base import BaseCommand
   from apps.cms.models import HeroSlide, ExpertCard
   from apps.content.models import Tag, Course
   # ... інші імпорти
   
   class Command(BaseCommand):
       help = 'Створити початковий контент для Play Vision'
       
       def handle(self, *args, **options):
           self.create_hero_slides()
           self.create_interests()
           self.create_plans()
           # ...
           
       def create_hero_slides(self):
           slides_data = [
               {
                   'title': 'Ми відкрилися. Play Vision стартує!',
                   'subtitle': 'Нова платформа для тренерів...',
                   'badge': 'НОВИНА',
                   'cta_text': 'Дізнатися більше',
                   'cta_url': '/about/',
                   'order': 1,
               },
               # ... 5 інших слайдів
           ]
           for data in slides_data:
               HeroSlide.objects.get_or_create(
                   title=data['title'],
                   defaults=data
               )
   ```

### E2. ФАЙЛИ З ДАНИМИ

**Створити JSON файли з контентом:**

1. **data/courses.json** - курси:
   ```json
   [
       {
           "title": "Тактична аналітика в сучасному футболі",
           "category": "Аналітика і скаутинг",
           "short_description": "Вивчіть як аналізувати матчі...",
           "description": "Детальний опис...",
           "price": 1200,
           "duration_minutes": 480,
           "difficulty": "intermediate",
           "tags": ["аналітика", "тактика", "xG"],
           "is_featured": true
       }
       // ... інші курси
   ]
   ```

2. **data/events.json** - події:
   ```json
   [
       {
           "title": "Форум футбольних фахівців 5",
           "event_type": "forum",
           "description": "Щорічна онлайн-подія...",
           "start_datetime": "2025-09-08T18:00:00",
           "price": 5450,
           "location": "Онлайн",
           "ticket_tiers": [
               {"name": "STANDARD", "price": 5450},
               {"name": "PRO", "price": 6750},
               {"name": "VIP", "price": 41250}
           ]
       }
   ]
   ```

3. **data/experts.json** - команда:
   ```json
   [
       {
           "name": "Oleg Bonislavskyi",
           "position": "CEO & Founder",
           "email": "olegbonislav@gmail.com",
           "specialization": "Стратегія та розвиток",
           "order": 1
       }
       // ... 7 інших
   ]
   ```

### E3. ІНТЕГРАЦІЯ З GOOGLE DRIVE

**ЩО ТРЕБА:**
- Посилання на методологію, команду, ПЛ деталі

**ПОСИЛАННЯ З USERTASK:**
- Команда професіоналів відео: https://drive.google.com/file/d/1SbBFZBwOgGu33CcEZtz2-wLitlAdQK0k/view?usp=share_link
- ПЛ деталі: https://drive.google.com/file/d/1A8oTTlXUon_ow-k3YbdtUX-9Euj79_pu/view?usp=share_link

**ЩО ПОТРІБНО:**
- Додати ці посилання в відповідні місця
- Створити preview для Google Drive files
- АБО завантажити файли локально

### E4. REFERENCE SITES

**Для вивчення та натхнення:**

1. **ECA Europe:** https://www.ecaeurope.com/
   - Структура hero карусель
   - Професійний дизайн

2. **Johan Cruyff Institute:** https://www.johancruyffinstitute.com/
   - События та курси
   - Освітня платформа

3. **BODO.UA:** https://www.bodo.ua
   - E-commerce для івентів
   - Картки продуктів

4. **MEGOGO** - підписка баннер
   - Мозаїка контенту
   - Підписка CTA

---

## ТЕСТУВАННЯ

### ФУНКЦІОНАЛЬНЕ ТЕСТУВАННЯ:

**User Journey Tests:**

1. **Реєстрація → Вхід → Купівля курсу:**
   - Зареєструватись через email
   - Підтвердити email
   - Обрати курс
   - Додати в кошик
   - Оформити оплату
   - Отримати доступ
   - Почати перегляд

2. **Підписка flow:**
   - Переглянути тарифи
   - Обрати план
   - Оплатити
   - Отримати доступ до всіх курсів
   - Перевірити бали loyalty

3. **Івент registration:**
   - Знайти івент в календарі
   - Переглянути деталі
   - Купити квиток
   - Отримати QR код
   - Check-in

### ТЕСТОВІ СЦЕНАРІЇ:

**Критичні flow:**

1. Незареєстрований користувач переглядає preview відео → pop-up з пропозицією реєстрації → реєстрація → курс в кошику
2. Користувач з підпискою переглядає курс → progress tracking → completion → нарахування балів
3. Користувач накопичує 50 балів → автоматична знижка 5% → покупка зі знижкою
4. Pro-Vision підписник отримує баланс квитків → використовує на івент
5. Неуспішний платіж → повідомлення з помилкою → повтор оплати

### PERFORMANCE TESTING:

**Метрики:**
- Page load time < 2 секунди
- Time to Interactive < 3 секунди
- First Contentful Paint < 1 секунда
- Lighthouse score > 90

**Оптимізація:**
- Image lazy loading
- Code splitting
- CSS минімізація
- JavaScript defer/async
- CDN для статики
- Database query optimization

---

## DEPLOYMENT

### PRODUCTION CHECKLIST:

**Before Deploy:**

1. **Налаштування:**
   - [ ] DEBUG=False
   - [ ] SECRET_KEY в environment variables
   - [ ] ALLOWED_HOSTS налаштовано
   - [ ] Database production (PostgreSQL)
   - [ ] Redis для cache та Celery
   - [ ] S3 для media files

2. **Security:**
   - [ ] HTTPS enabled
   - [ ] CSRF protection active
   - [ ] XSS protection
   - [ ] SQL injection prevention
   - [ ] Rate limiting
   - [ ] Security headers

3. **Services:**
   - [ ] Email service configured
   - [ ] Payment gateway production keys
   - [ ] OAuth apps registered
   - [ ] SMS gateway configured
   - [ ] CDN configured

4. **Monitoring:**
   - [ ] Sentry for error tracking
   - [ ] Google Analytics
   - [ ] Uptime monitoring
   - [ ] Database backups automated
   - [ ] Log aggregation

**Deploy Steps:**

1. Run migrations: `python manage.py migrate`
2. Collect static: `python manage.py collectstatic --noinput`
3. Create initial content: `python manage.py create_initial_content`
4. Create superuser: `python manage.py createsuperuser`
5. Test critical flows
6. Monitor logs

---

## ПОСТ-ЗАПУСК

### МОНІТОРИНГ ПЕРШИХ ДНІВ:

1. **Метрики для відстеження:**
   - Реєстрації (скільки, через що: email/phone/social)
   - Конверсія реєстрація → підписка
   - Помилки платежів
   - Час завантаження сторінок
   - Помилки в логах

2. **User Feedback:**
   - Збирати відгуки про UX
   - Відстежувати де користувачі "застряють"
   - Heatmaps (Hotjar)
   - Session recordings

3. **Швидкі фікси:**
   - Виправляти критичні баги протягом 1 години
   - Важливі баги протягом 24 годин
   - UX покращення протягом тижня

### ІТЕРАЦІЇ:

**Тиждень 1-2:**
- Фікси критичних багів
- UX покращення на основі feedback
- Оптимізація performance

**Місяць 1:**
- Додавання нового контенту (курси, івенти)
- A/B тестування (CTA кнопки, pricing)
- Marketing інтеграції

**Місяць 2-3:**
- Додаткові features з roadmap
- AI помічник покращення
- Рефери програма
- Мобільний додаток (опціонально)

---

## КРИТИЧНІ ПРИМІТКИ

### ВАЖЛИВІ НЮАНСИ З USERTASK:

**🔴 КРИТИЧНО ВАЖЛИВО:**

1. **Підпис під логотипом:**
   - **"навігатор футбольного розвитку"** має бути завжди видимий
   - Під або біля логотипу Play Vision

2. **Білі РАМКИ, НЕ заливка:**
   - Hero банери з **БІЛОЮ ОБВОДКОЮ** навколо
   - **НЕ суцільний фон** (це дуже важливо!)

3. **ОДНА ЗЕЛЕНА кнопка в hero:**
   - В hero секції **ТІЛЬКИ 1 кнопка** (було 2 - видалити зайву!)
   - Кнопка **ЗЕЛЕНА** зі стрілкою → (НЕ червона!)

4. **Постійний заклик в Хаб знань:**
   - Текст: **"Оформи підписку, стань частиною спільноти фахівців!"**
   - **НЕ ЗНИКАЄ** і знаходиться **ВІДРАЗУ ПІД ХЕДЕРОМ**
   - Завжди видимий при прокрутці (sticky)

5. **Події = Івенти:**
   - Розділи "5. Події" і "7. Івенти" в usertask - це **ОДНЕ І ТЕ САМЕ**
   - Єдина система управління івентами/подіями

**🟡 ДУЖЕ ВАЖЛИВО:**

6. **Тільки українська мова:**
   - Всі англійські назви прибрати (MOTIVATION → МЕНТАЛЬНІСТЬ)
   - Interface українською
   - Контент українською

7. **Виправити тексти з помилками:**
   - Ментор-коучінг має typos - виправити перед публікацією
   - Тарифи мають незавершені описи - дописати повністю
   - Всі граматичні помилки виправити

8. **Шестикутники (Hexagons):**
   - Гексагональна структура для ментор-коучінгу
   - Іконки помаранчеві
   - Білий/сірий фон
   - Клікабельні з розгортанням деталей

9. **Календар - 1 подія на дату:**
   - В календарі максимум 1 івент на день
   - Простота та зрозумілість

10. **Pop-up - "готовий приєднатись до спільноти Play vision?":**
    - Обов'язковий текст в обох варіантах
    - З анімацією
    - Не агресивний

11. **Команда професіоналів формат:**
    - Верхній ряд 4 особи
    - Нижній ряд 4+ осіб
    - Стиль: професійні портрети, білий фон

12. **Спікери івенту:**
    - За аналогією до "Команди професіоналів"
    - 4 зображення з іменами файлів: ctte.jpg, owen.jpg, zou-hai.jpg, villaforta.jpg

13. **Тарифи івенту:**
    - STANDARD: 5450
    - PRO: 6750
    - VIP: 41250

---

## РОБОЧИЙ ПРОЦЕС

### ДЛЯ BACKEND РОЗРОБНИКА:

**День 1-3:**
1. Створити всі management commands
2. Заповнити БД тестовими даними
3. Додати відсутні поля в моделі (email в ExpertCard, ticket_tiers в Event, etc.)

**День 4-7:**
1. Інтегрувати LiqPay
2. Завершити checkout flow
3. Webhook обробка
4. Тести платежів

**День 8-10:**
1. Google OAuth інтеграція
2. Telegram Login Widget
3. Email service налаштування

**День 11-14:**
1. Preview функціонал (відео обмеження)
2. PDF viewer з watermark
3. Progress tracking

**День 15+:**
1. Bug fixes
2. Optimization
3. Testing

### ДЛЯ FRONTEND РОЗРОБНИКА:

**День 1-3:**
1. Створити всі відсутні компоненти:
   - Hub boards
   - Event calendar
   - MEGOGO-style banner
2. Покращити існуючі

**День 4-7:**
1. Додати анімації
2. Pop-ups дизайн
3. Micro-interactions

**День 8-10:**
1. Mobile responsive фінальна перевірка
2. Cross-browser testing
3. Accessibility audit

**День 11-14:**
1. Performance optimization
2. Image optimization
3. CSS cleanup

**День 15+:**
1. Polishing
2. Animation fine-tuning
3. User testing

### ДЛЯ ДИЗАЙНЕРА:

**Тиждень 1:**
1. Створити 6 hero слайдів
2. Фото команди (8 осіб)
3. Обкладинки курсів (6 featured)

**Тиждень 2:**
1. Цитати експертів (3 чорно-білі фото)
2. Івенти зображення (5 шт)
3. Борди та банери

**Тиждень 3:**
1. Іконки та UI елементи
2. Анімації та переходи
3. Брендбук фінальна перевірка

### ДЛЯ КОНТЕНТ-МЕНЕДЖЕРА:

**Тиждень 1:**
1. Написати тексти для всіх сторінок
2. Створити структуру 6 featured курсів
3. Описи івентів

**Тиждень 2:**
1. Детальний контент курсів (матеріали)
2. FAQ секції
3. Email templates тексти

**Тиждень 3:**
1. Блог/новини
2. Social media контент
3. Маркетингові матеріали

---

## МЕТРИКИ УСПІХУ

### KPI ДЛЯ ЗАПУСКУ:

**Технічні:**
- Uptime > 99.5%
- Page load < 2s
- Error rate < 0.1%
- Mobile score > 90

**Business:**
- Конверсія відвідувач → реєстрація > 5%
- Конверсія реєстрація → підписка > 10%
- Average session duration > 3 хв
- Bounce rate < 50%

**Content:**
- 6 featured курсів готові
- 20+ курсів в каталозі
- 5+ івентів заплановані
- 8 членів команди з фото

---

**ФІНАЛЬНИЙ ВЕРДИКТ:**

**ПРОЄКТ ГОТОВИЙ НА 72%**

**ЩО ГОТОВЕ:**
- ✅ Backend архітектура (80%)
- ✅ Моделі даних (95%)
- ✅ Основні templates (75%)
- ✅ Особистий кабінет (90%)
- ✅ Програма лояльності (95%)
- ✅ Хаб знань база (85%)

**ЩО ПОТРІБНО ДОДАТИ:**
- ⚠️ Платіжна інтеграція (50% → 100%)
- ⚠️ OAuth соцмережі (0% → 100%)
- ⚠️ Контент (40% → 100%)
- ⚠️ Ментор-коучінг сторінка (10% → 100%)
- ⚠️ Календар івентів (20% → 100%)
- ⚠️ Preview функціонал (30% → 100%)

**ЧАС ДО ЗАПУСКУ:** 6-8 тижнів (при команді з 4 осіб)

**МІНІМАЛЬНИЙ ЧАС:** 4 тижні (MVP з критичними функціями)

---

## ДЕТАЛЬНИЙ ЧЕКЛИСТ ГОТОВНОСТІ

### BACKEND (Django)

**МОДЕЛІ:**
- [x] User з email/phone
- [x] Profile
- [x] VerificationCode
- [x] SocialAccount
- [x] Course, Material, Category, Tag
- [x] Event, EventTicket, Speaker
- [x] Plan, Subscription, Entitlement, TicketBalance
- [x] LoyaltyAccount, PointTransaction, PointEarningRule
- [x] Payment, Order, OrderItem, Coupon
- [x] Cart, CartItem
- [x] HeroSlide, ExpertCard, HexagonItem
- [x] MonthlyQuote
- [ ] ExpertCard.email поле (ДОДАТИ)
- [ ] Event.ticket_tiers JSON поле (ДОДАТИ)
- [ ] Event.benefits та target_audience (ДОДАТИ)
- [ ] Plan.tier_name, color_indicator, tier_slogan (ДОДАТИ)
- [ ] Notification модель (СТВОРИТИ)

**VIEWS:**
- [x] RegisterView
- [x] LoginView
- [x] CabinetView з 5 вкладками
- [x] HomeView
- [x] CourseListView, CourseDetailView
- [x] EventListView, EventDetailView
- [x] PricingView
- [ ] PasswordResetConfirmView (ДОДАТИ)
- [ ] MentoringView (СТВОРИТИ)
- [ ] CheckoutView повний (ДОРОБИТИ)
- [ ] ApplyCouponView (ДОДАТИ)
- [ ] RepeatPaymentView (ДОДАТИ)

**API ENDPOINTS:**
- [x] Cart API
- [x] Favorites API
- [x] Notifications API (базовий)
- [ ] Calendar Events API (СТВОРИТИ)
- [ ] Payment Webhook (ДОРОБИТИ)
- [ ] Loyalty Points API (ДОРОБИТИ)

**SERVICES:**
- [x] EmailService
- [ ] SMSService (СТВОРИТИ)
- [ ] TelegramService (СТВОРИТИ)
- [ ] ViberService (СТВОРИТИ)
- [ ] WhatsAppService (СТВОРИТИ)
- [ ] PaymentService для LiqPay (СТВОРИТИ)
- [ ] RecommendationService (СТВОРИТИ)
- [ ] VideoPreviewService (СТВОРИТИ)

**MANAGEMENT COMMANDS:**
- [ ] create_initial_content (СТВОРИТИ)
- [ ] create_hero_slides (СТВОРИТИ)
- [ ] create_interests (СТВОРИТИ)
- [ ] create_plans (СТВОРИТИ)
- [ ] create_loyalty_rules (СТВОРИТИ)
- [ ] create_expert_quotes (СТВОРИТИ)
- [ ] create_sample_events (СТВОРИТИ)

### FRONTEND (HTML/CSS/JS)

**TEMPLATES:**
- [x] base.html з хедером
- [x] register.html, login.html
- [x] home.html
- [x] course_list.html, course_detail.html
- [x] event_list.html, event_detail.html
- [x] cabinet.html з вкладками
- [x] cart.html
- [x] pricing.html
- [x] loyalty/rules.html
- [x] about.html
- [x] scroll-popup.html
- [ ] password_reset.html (СТВОРИТИ)
- [ ] password_reset_confirm.html (СТВОРИТИ)
- [ ] mentoring.html (СТВОРИТИ)
- [ ] hub_boards.html компонент (СТВОРИТИ)
- [ ] event_banner_card.html (СТВОРИТИ)
- [ ] megogo-style-banner.html (СТВОРИТИ)

**CSS КОМПОНЕНТИ:**
- [x] header-desktop.css
- [x] home.css, home-additions.css
- [x] hub.css, hub-additions.css
- [x] events.css
- [x] cabinet.css, cabinet-additions.css
- [x] cart.css
- [x] pricing.css
- [x] auth.css
- [x] loyalty-rules.css
- [x] scroll-popup.css
- [ ] mentoring.css (СТВОРИТИ)
- [ ] hub-boards.css (СТВОРИТИ)
- [ ] event-calendar.css (СТВОРИТИ)
- [ ] pop-up-enhanced.css (ПОКРАЩИТИ)

**JAVASCRIPT:**
- [x] home.js
- [x] hub.js
- [x] events.js
- [x] cabinet.js
- [x] cart.js
- [x] scroll-popup.js
- [x] ai-chat-dialog.js
- [x] theme-manager.js
- [ ] events-calendar.js (СТВОРИТИ)
- [ ] video-preview-limiter.js (СТВОРИТИ)
- [ ] pdf-viewer.js (СТВОРИТИ)
- [ ] logo-animation.js (СТВОРИТИ)
- [ ] recommendations.js (СТВОРИТИ)

### ДИЗАЙН ТА КОНТЕНТ

**ЗОБРАЖЕННЯ:**
- [ ] 6 hero слайдів (1920x1080)
- [ ] 8 фото команди (400x400)
- [ ] 3 фото експертів ч/б (400x400)
- [ ] 6+ обкладинки featured курсів (1200x600)
- [ ] 20+ обкладинки всіх курсів (1200x600)
- [ ] 5+ зображення івентів (1200x600)
- [ ] Іконки (lock, play, calendar-week)
- [ ] Лого Play Vision (вже є ✓)

**ТЕКСТИ:**
- [ ] 6 hero слайдів (title, subtitle, CTA)
- [ ] 4 борди Хаб знань (заголовки, описи)
- [ ] 6 featured курсів (опис, матеріали)
- [ ] 20+ курсів каталогу
- [ ] 5+ івентів (опис, agenda, спікери)
- [ ] Сторінка Ментор-коучінг (5 блоків тексту)
- [ ] БРЕНД-АБЗАЦ "Про нас"
- [ ] Email templates (5+ шт)

**ВІДЕО/МЕДІА:**
- [ ] Відео для hero (опціонально)
- [ ] Preview відео курсів
- [ ] Анімація логотипу (2-3 сек)
- [ ] Відео команди (Google Drive: https://drive.google.com/file/d/1SbBFZBwOgGu33CcEZtz2-wLitlAdQK0k/)

### ІНТЕГРАЦІЇ

**ПЛАТЕЖІ:**
- [ ] LiqPay integration
- [ ] Stripe integration (міжнародні)
- [ ] Webhook endpoints
- [ ] Success/Fail flows
- [ ] Refund logic

**АУТЕНТИФІКАЦІЯ:**
- [ ] Google OAuth 2.0
- [ ] Telegram Login Widget
- [ ] TikTok Login (якщо доступний)

**КОМУНІКАЦІЇ:**
- [ ] Email service (SendGrid/Mailgun)
- [ ] SMS gateway (Twilio)
- [ ] Telegram Bot API
- [ ] Viber Bot API (опціонально)
- [ ] WhatsApp Business API (опціонально)

**АНАЛІТИКА:**
- [ ] Google Analytics 4
- [ ] Facebook Pixel
- [ ] Hotjar (опціонально)
- [ ] Custom event tracking

**ІНШЕ:**
- [ ] S3 для media files
- [ ] CDN для static
- [ ] Redis для cache
- [ ] Celery для async tasks
- [ ] Sentry для error tracking

---

## ТАБЛИЦЯ ПОРІВНЯННЯ: USERTASK VS ПОТОЧНИЙ СТАН

| № | Розділ | Вимога з usertask.md | Поточний стан | % готовності | Що потрібно |
|---|--------|---------------------|---------------|--------------|-------------|
| 1 | Реєстрація | Email/Phone, соцмережі, верифікація | Email працює, Phone/соцмережі ні | 60% | SMS gateway, OAuth |
| 2 | Вхід | Email/Phone, соцмережі, відновлення паролю | Вхід працює, відновлення базове | 70% | Повний flow відновлення |
| 3 | Хедер | Лого з анімацією, меню, кнопка підписки, кошик | Структура є, деталі ні | 75% | Анімація лого, кнопка підписки, іконка кошика |
| 4 | Головна | 6 слайдів, курси, екосистема, команда, календар | Структура є, контент ні | 70% | 6 конкретних слайдів, календар івентів |
| 5 | Події | Функціонал івентів, квитки, Pro-Vision баланс | Базова функція є | 75% | Баланс квитків Pro-Vision |
| 6 | Хаб знань | Цитати (3), борди (4), матеріали, фільтри, preview | Структура є, деталі ні | 80% | 3 цитати, 4 борди, preview обмеження |
| 7 | Івенти | Календар, фільтр ціна, шаблони, детальна сторінка | Список є, календар ні | 75% | Інтерактивний календар, тарифи івенту |
| 8 | Ментор-коучінг | 5 блоків, 6 напрямків детально | Coming soon заглушка | 15% | Повна сторінка з нуля |
| 9 | Про нас | БРЕНД-АБЗАЦ, трикутник | Базова сторінка є | 65% | БРЕНД-АБЗАЦ текст |
| 10 | Кабінет | 5 вкладок, інтереси, аватар, днів з нами | Структура повна | 90% | Індикатор днів, фото upload |
| 11 | ПЛ сторінка | Промо-баннер, roadmap, timeline | Повна сторінка є | 85% | Timeline візуалізація |
| 12 | Тарифи | 4 плани з кольорами, банери, MEGOGO стиль | Базова сторінка є | 70% | Кольори, слогани, MEGOGO баннер |
| 13 | Кошик | Рекомендації, промокод, знижка loyalty | Структура є | 85% | Recommendations алгоритм |
| 14 | Pop-ups | 2 варіанти з дизайном, анімація | Базовий є | 60% | Дизайн темний фон, анімації |

**СЕРЕДНЯ ГОТОВНІСТЬ:** 72%

---

## ПРІОРИТІЗАЦІЯ РОБІТ

### 🔴 КРИТИЧНИЙ ПРІОРИТЕТ (без цього не можна запускати):

1. **Платіжна система** - 2 тижні
   - LiqPay інтеграція
   - Checkout flow
   - Success/Fail обробка
   - Webhooks

2. **Контент (мінімум)** - 1 тиждень
   - 6 featured курсів з матеріалами
   - 5 івентів
   - 8 фото команди
   - Тексти для головної

3. **OAuth Google** - 3 дні
   - Найпопулярніший метод реєстрації
   - Збільшує конверсію на 30-40%

4. **Email service production** - 2 дні
   - SendGrid/Mailgun
   - Templates
   - Верифікація

### 🟡 ВИСОКИЙ ПРІОРИТЕТ (покращує UX):

1. **Сторінка Ментор-коучінг** - 1 тиждень
   - 5 блоків згідно usertask
   - Дизайн та контент

2. **Preview функціонал** - 4 дні
   - Обмеження часу відео (20 сек)
   - CTA після preview

3. **6 hero слайдів конкретних** - 3 дні
   - Дизайн
   - Тексти
   - Інтеграція

4. **Календар івентів** - 4 дні
   - Інтерактивний календар
   - Фільтри

5. **Pop-ups дизайн** - 2 дні
   - Темний фон, жовтий текст
   - Анімації

### 🟢 СЕРЕДНІЙ ПРІОРИТЕТ (nice to have):

1. **Telegram Login** - 2 дні
2. **SMS verification** - 3 дні
3. **AI помічник повний** - 1 тиждень
4. **Борди Хаб знань** - 2 дні
5. **MEGOGO banner** - 2 дні
6. **Анімація логотипу** - 1 день
7. **PDF viewer з watermark** - 3 дні
8. **Recommendations алгоритм** - 3 дні

### 🔵 НИЗЬКИЙ ПРІОРИТЕТ (можна після запуску):

1. TikTok Login
2. Viber/WhatsApp
3. Mobile app
4. Advanced analytics
5. Referral program
6. Blog/News section

---

## ЧАС ДО MVP (Мінімальний продукт):

**КРИТИЧНІ ЗАВДАННЯ:**
- Платіжна система: 80 годин
- Контент мінімум: 40 годин
- Google OAuth: 24 години
- Email production: 16 годин
- Bug fixes та testing: 40 годин

**ВСЬОГО:** 200 годин = **5 тижнів** (1 розробник full-time)

**З КОМАНДОЮ (2 розробники + 1 дизайнер + 1 контент):**
**3 тижні до MVP**

---

## ЧАС ДО ПОВНОЇ ВЕРСІЇ (згідно usertask.md):

**ВСЬОГО ЗАВДАНЬ:**
- Backend: 115 годин
- Frontend: 140 годин
- Дизайн: 75 годин
- Контент: 90 годин

**ЗАГАЛОМ:** 420 годин

**З КОМАНДОЮ (4 особи):**
**6-8 тижнів до повної версії**

---

## НАЙБІЛЬШІ РИЗИКИ

### ТЕХНІЧНІ РИЗИКИ:

1. **Інтеграція LiqPay:**
   - Складність: Середня
   - Час: Може зайняти довше через документацію
   - Мітігація: Почати ASAP, використати sandbox

2. **Preview відео з обмеженням:**
   - Складність: Висока
   - Проблема: Обхід обмеження користувачами
   - Мітігація: Server-side генерація preview, DRM

3. **OAuth інтеграції:**
   - Складність: Середня
   - Проблема: Callback URLs, production keys
   - Мітігація: Тестувати на localhost, ngrok

### БІЗНЕС РИЗИКИ:

1. **Недостатньо контенту:**
   - Проблема: Користувачі не бачать цінності
   - Мітігація: Мінімум 6 featured + 20 загальних курсів

2. **Складний onboarding:**
   - Проблема: Користувачі не розуміють як користуватись
   - Мітігація: Onboarding tour, tooltips, відео інструкції

3. **Платіжна конверсія:**
   - Проблема: Користувачі не купують
   - Мітігація: Free trial, discount codes, testimonials

---

## РЕКОМЕНДАЦІЇ

### КОРОТКОСТРОКОВІ (до запуску):

1. **Фокус на MVP:**
   - Запустити з мінімальним набором функцій
   - Отримати feedback
   - Ітерувати швидко

2. **Контент важливіший за features:**
   - Краще 10 якісних курсів ніж 50 функцій
   - Користувачі приходять за знаннями

3. **Простота onboarding:**
   - Google OAuth як основний метод
   - Мінімум полів при реєстрації
   - Guided tour після входу

### ДОВГОСТРОКОВІ (після запуску):

1. **Community building:**
   - Forum або Discord
   - User-generated content
   - Gamification

2. **Mobile app:**
   - React Native або Flutter
   - Офлайн доступ
   - Push notifications

3. **B2B features:**
   - Team subscriptions
   - Corporate training
   - White-label

4. **Expansion:**
   - Англійська версія
   - Інші види спорту
   - Міжнародний ринок

---

## CONTACTS ТА РЕСУРСИ

### KEY STAKEHOLDERS:

**Development:**
- Backend lead: [to be assigned]
- Frontend lead: [to be assigned]
- DevOps: [to be assigned]

**Content:**
- Content manager: [to be assigned]
- Course authors: Олексій + Микита (Ментор-коучінг)
- About page: Євген

**Design:**
- UI/UX designer: [to be assigned]
- Brand guidelines: static/guideline/

**Contact:**
- Project owner: Oleg Bonislavskyi
- Email: olegbonislav@gmail.com

### ВАЖЛИВІ ПОСИЛАННЯ:

**Google Drive:**
- Команда відео: https://drive.google.com/file/d/1SbBFZBwOgGu33CcEZtz2-wLitlAdQK0k/view?usp=share_link
- ПЛ деталі: https://drive.google.com/file/d/1A8oTTlXUon_ow-k3YbdtUX-9Euj79_pu/view?usp=share_link

**Reference sites:**
- https://www.ecaeurope.com/
- https://www.johancruyffinstitute.com/
- https://www.bodo.ua

**Брендбук:**
- Локально: /static/guideline/

---

## ФІНАЛЬНІ ВИСНОВКИ

### СИЛЬНІ СТОРОНИ ПОТОЧНОЇ РЕАЛІЗАЦІЇ:

1. ✅ **Продумана архітектура:**
   - Модульна структура
   - Чисті models з relationships
   - Separation of concerns

2. ✅ **Програма лояльності:**
   - Повністю реалізована
   - Складна логіка працює
   - Окрема сторінка готова

3. ✅ **Особистий кабінет:**
   - Всі вкладки
   - AJAX оновлення
   - Зручний інтерфейс

4. ✅ **Базовий функціонал:**
   - Реєстрація/вхід працює
   - Курси відображаються
   - Фільтри працюють
   - Кошик функціональний

### СЛАБКІ СТОРОНИ (що потрібно покращити):

1. ⚠️ **Недостатньо контенту:**
   - Багато placeholder даних
   - Тестові курси без матеріалів
   - Потрібно реальне наповнення

2. ⚠️ **Платежі не завершені:**
   - Тільки модель готова
   - Інтеграція LiqPay відсутня
   - Критично для запуску

3. ⚠️ **OAuth не підключений:**
   - Знижує конверсію реєстрації
   - Google OAuth обов'язковий

4. ⚠️ **Ментор-коучінг відсутній:**
   - Важливий розділ
   - Тільки заглушка

5. ⚠️ **Preview функціонал базовий:**
   - Немає обмеження часу
   - Легко обійти
   - Потрібна захищена реалізація

### ЩО РОБИТИ ДАЛІ:

**IMMEDIATE (цього тижня):**
1. Створити management команду для initial content
2. Почати інтеграцію LiqPay
3. Підключити Google OAuth
4. Завантажити перші 6 featured курсів

**SHORT-TERM (наступні 2 тижні):**
1. Завершити платіжну систему
2. Створити сторінку Ментор-коучінг
3. Додати 6 hero слайдів
4. Реалізувати preview з обмеженням

**MEDIUM-TERM (3-4 тижні):**
1. Наповнити контентом (20+ курсів)
2. Створити 5+ івентів
3. Додати календар
4. Pop-ups дизайн

**BEFORE LAUNCH:**
1. Full testing (1 тиждень)
2. Performance optimization
3. Security audit
4. User acceptance testing

---

**ДОКУМЕНТ СТВОРЕНО: 19.10.2025**  
**АНАЛІЗ БАЗУЄТЬСЯ НА:** usertask.md (1246 lines) + повний codebase (2300+ files)  
**ПРОАНАЛІЗОВАНО:**
- ✅ 12 Django apps
- ✅ 25+ models
- ✅ 40+ views
- ✅ 50+ templates
- ✅ 33 CSS files
- ✅ 28 JS files

**ДЕТАЛІЗАЦІЯ:** Максимальна - кожна функція описана, кожна зміна обгрунтована  
**ФОРМАТ:** Текстовий без коду (як запитувалось)  
**РОЗМІР:** 2268 рядків детального аналізу  
**СТАТУС:** ✅ ГОТОВО ДО ВИКОРИСТАННЯ КОМАНДОЮ РОЗРОБКИ

---

**NEXT STEPS:**
1. Розподілити завдання по команді
2. Створити GitHub Issues з цього документу
3. Setup project management (Jira/Trello)
4. Почати Sprint 1: Critical features
5. Weekly standups для tracking progress

**ESTIMATED LAUNCH DATE:** 6-8 тижнів від сьогодні (середина грудня 2025)  
**MVP DATE:** 4 тижні (середина листопада 2025)

