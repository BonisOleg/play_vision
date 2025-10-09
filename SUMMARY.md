# PLAY VISION - ПОВНИЙ ОПИС ПРОЕКТУ

## 1. 🚀 ЗАГАЛЬНА ІНФОРМАЦІЯ

### 1.1 Про проект
- **Назва:** Play Vision
- **Тип:** Освітня платформа для футбольних фахівців
- **Цільова аудиторія:** 
  - Тренери (дитячі, професійні)
  - Аналітики та скаути
  - Футболісти (юніори, професіонали)
  - Батьки юних футболістів
- **Основна цінність:** Доступ до професійних знань у футбольній сфері

### 1.2 Технічні деталі
- **Backend:** Django 5.x, Python 3.12, Postgres 15, Redis, Celery
- **Frontend:** Django Templates + HTML/CSS/JS, progressive enhancement
- **Безпека:** HTTPS+HSTS, CSP nonce, CSRF/XSS/SQLi захист
- **Відео:** HLS + AES-128, підписані URL, динамічний watermark
- **PWA:** manifest.json, service worker, offline публічних сторінок
- **Мови:** uk (дефолт), en (готовність)

### 1.3 Параметри проекту
- **Дедлайн:** 01.10.2025 до 22:00
- **Вартість:** 2,781 USD
- **Схема оплати:**
  - I платіж: 927 USD — після підписання договору
  - II платіж: 927 USD — після завершення етапу 1
  - III платіж: 927 USD — до старту продакшену (етап 3)

## 2. 🏗️ АРХІТЕКТУРА СИСТЕМИ

### 2.1 Типи користувачів та ролі
- **Гості:** публічні сторінки, прев'ю 20с/10%, кошик → реєстрація при оплаті
- **Користувачі:** безкоштовне, разові покупки
- **Підписники L1/L2/L3/L4:** доступ за тегами/entitlements
- **Адмін/Редактор:** керування контентом/подіями/цінами

### 2.2 Основні моделі бази даних

#### Користувачі (accounts):
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    profession = models.CharField(max_length=100, blank=True)
    interests = models.ManyToManyField('core.Interest', blank=True)
    completed_survey = models.BooleanField(default=False)
```

#### Курси та матеріали (courses):
```python
class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Початковий'),
        ('intermediate', 'Середній'),
        ('advanced', 'Експертний'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Доступ та контроль
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    requires_subscription = models.BooleanField(default=True)
    subscription_tiers = models.JSONField(default=list)  # ['tier1', 'tier2']

class CourseLesson(models.Model):
    CONTENT_TYPES = [
        ('video', 'Відео'),
        ('pdf', 'PDF'),
        ('article', 'Стаття'),
        ('quiz', 'Тест'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    order = models.PositiveIntegerField()
    
    # Контент
    video_file = models.FileField(upload_to='lessons/videos/', blank=True)
    pdf_file = models.FileField(upload_to='lessons/pdfs/', blank=True)
    article_content = models.TextField(blank=True)
```

#### Події (events):
```python
class Event(models.Model):
    EVENT_TYPES = [
        ('forum_professionals', 'Форум футбольних фахівців'),
        ('forum_parents', 'Форум футбольних батьків'),
        ('internship', 'Стажування в професійних клубах'),
        ('seminar', 'Практичні семінари і хакатони'),
        ('psychology', 'Воркшопи зі спортивної психології'),
        ('selection_camp', 'Селекційні табори'),
        ('webinar', 'Онлайн-теорії і вебінари'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    
    # Дата та місце
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)  # Або онлайн
    zoom_link = models.URLField(blank=True)
    
    # Білети та ціни
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_attendees = models.PositiveIntegerField()
    tickets_sold = models.PositiveIntegerField(default=0)
```

#### Підписки та платежі (payments):
```python
class SubscriptionPlan(models.Model):
    PLAN_TYPES = [
        ('monthly', 'Місячна'),
        ('quarterly', '3 місяці'),
        ('yearly', 'Річна'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    
    # Особливості плану
    features = models.JSONField(default=list)  # ['Доступ до всіх курсів', 'Підтримка 24/7']
    event_tickets_balance = models.PositiveIntegerField(default=0)  # Для Pro-Vision

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Очікує'),
        ('processing', 'Обробляється'),
        ('completed', 'Завершено'),
        ('failed', 'Помилка'),
        ('refunded', 'Повернено'),
    ]
    
    PAYMENT_TYPE = [
        ('subscription', 'Підписка'),
        ('course', 'Курс'),
        ('event_ticket', 'Квиток на івент'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
```

#### Кошик (cart):
```python
class CartItem(models.Model):
    # ... існуючі поля ...
    
    # ДОДАТКОВІ ПОЛЯ
    content_type_display = models.CharField(max_length=50, blank=True, 
                                      help_text='VIDEO • 95 ХВ, PDF, etc')
    thumbnail_url = models.URLField(blank=True, help_text='Product thumbnail')
    
    # Metadata з реального об'єкта (JSON для гнучкості)
    item_metadata = models.JSONField(default=dict, help_text='Tags, badges, etc')

class Cart(models.Model):
    # ... існуючі поля ...
    
    # НОВІ ПОЛЯ
    applied_coupon = models.ForeignKey('payments.Coupon', null=True, blank=True, 
                                     on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tips_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
```

### 2.3 Безпека та захист контенту
- **HLS + AES-128:** Шифрування відео для захисту від скачування
- **Підписані URL:** TTL 60-300с URL для доступу до відео
- **Водяні знаки:** Email+userID+timecode на відео
- **PDF захист:** Вьювер з watermark, прев'ю 10%, заборона копіювання
- **Paywall:** Blur+замочок для блокування контенту без доступу
- **Безпека автентифікації:** Rate-limit, reCAPTCHA v3, email/phone verification
- **Платіжна безпека:** 3D Secure для платежів, PCI-DSS шлюз

## 3. 📱 ФУНКЦІОНАЛЬНІСТЬ СИСТЕМИ

### 3.1 Хаб знань
- **Каталог курсів:** Мозаїка з карточками, фільтри, пошук
- **Теги та категорії:** Сортування за напрямками, складністю, типом
- **Картка курсу:** Назва, опис, тривалість, теги, ціна, рейтинг
- **Додаткові маркери:** "топ-продажів", "новинка", "для вас"
- **Детальна сторінка курсу:** Повний опис, відгуки, програма, доступ
- **Матеріали:** Відео (з захистом), PDF, статті, тести
- **Прев'ю контенту:** 20с відео, 10% PDF/статті з водяним знаком

### 3.2 Система подій (Івенти)
- **Календар подій:** Місячний календар з можливістю вибору дати
- **Типи подій:**
  - Форуми для фахівців
  - Форуми для батьків
  - Стажування в клубах
  - Семінари і хакатони
  - Воркшопи з психології
  - Селекційні табори
  - Онлайн-вебінари
- **Реєстрація на події:** Оплата, QR-коди, підтвердження
- **Баланс квитків:** Pro-Vision підписка включає квоту квитків
- **Інтеграція з Zoom:** Автоматичне генерування посилань

### 3.3 Особистий кабінет
- **Профіль:** 
  - ФІО, дата народження, професія
  - Аватар, методи входу, зміна пароля
  - Напрямки інтересів (чекбокси)
  - Бонус за заповнення профілю
- **Підписка:**
  - Інформація про поточний план
  - Дати початку/закінчення
  - Можливість зміни плану
  - Автопролонгація (вкл/викл)
- **Історія оплат:**
  - Всі транзакції
  - Статус оплат
  - Рахунки та чеки
- **Мої файли:**
  - Доступні курси та матеріали
  - Прогрес перегляду
  - Улюблені (зірочка)
  - Рекомендації
- **Програма лояльності:**
  - Рівень (Bronze, Silver, Gold, Platinum)
  - Прогрес-бар накопичення балів
  - Доступні знижки та бонуси

### 3.4 Система підписок та монетизації
- **Плани підписок:**
  - Місячний
  - 3 місяці (квартальний)
  - 6 місяців
  - Річний
  - Pro-Vision (розширений)
- **Оплата:**
  - Банківські картки
  - Apple Pay
  - Google Pay
  - 3D Secure
  - Рекурентні платежі
- **Промокоди та знижки:**
  - Фіксовані знижки
  - Відсоткові знижки
  - Обмеження за часом
  - Обмеження за кількістю використань
- **Програма лояльності:**
  - Нарахування балів за активність
  - Знижки за рівнем (0%, 5%, 10%, 15%)
  - Реферальна програма

### 3.5 Кошик та процес оплати
- **Функціонал кошика:**
  - Додавання/видалення товарів
  - Зміна кількості
  - Застосування промокодів
  - Розрахунок знижки
  - Система рекомендацій "Ідеальний додаток до кошика"
  - Чайові авторам (опціонально)
- **Чекаут:**
  - Вибір способу оплати
  - Введення даних карти
  - Підтвердження замовлення
  - Обробка 3D Secure
  - Підтвердження/відмова оплати

### 3.6 AI-помічник
- **Загальна концепція:** Розумний помічник для футбольних фахівців
- **Основні функції:**
  - FAQ про Play Vision (15-20%)
  - База футбольних знань (70-80%)
  - Монетизація через підписку (100% запитів)
- **Ключові теми:**
  - Тренерство (методики, плани, вправи)
  - Аналітика (метрики, відеоаналіз)
  - Скаутинг (оцінка гравців)
  - ЗФП (загальна фізична підготовка)
  - Статистика та метрики
  - Термінологія футбольна
  - Тактика та стратегія
  - Психологія спорту
- **Стиль відповідей:**
  - Короткі, конкретні (4-6 абзаців)
  - Проста мова, без пафосу
  - Партнерський тон
  - Завжди українською мовою
  - Посилання на матеріали
- **Монетизація:** Кожна відповідь містить CTA на підписку

## 4. 📋 ДЕТАЛЬНИЙ ПЛАН ІМПЛЕМЕНТАЦІЇ

### 4.1 Підготовка (Phase 0)
- **Створення резервної копії:** `python3 manage.py dumpdata > backups/backup_$(date +%Y%m%d).json`
- **Git гілка:** `git checkout -b feature/screenshot-changes-v2`
- **Структура файлів:**
  - Створення необхідних директорій
  - Підготовка шаблонів CSS/JS/HTML

### 4.2 Backend (Phase 1)
- **Моделі даних:**
  - Додавання полів до Tag (tag_type, display_order)
  - Створення MonthlyQuote моделі
  - Додавання training_specialization до Course
  - Розширення моделі CartItem

- **Views:**
  - Видалення difficulty/price фільтрів з CourseListView
  - Видалення price фільтру з EventListView
  - Створення LoyaltyRulesView

- **Адмін-панель:**
  - Налаштування для нових моделей
  - Фільтри та пошук
  - Inline-редагування

- **Міграції:**
  - Генерація міграцій для нових полів
  - Застосування міграцій

### 4.3 Компоненти (Phase 2)
- **Scroll popup:**
  - HTML структура
  - CSS стилізація
  - JavaScript функціонал
  - Інтеграція на сторінки

- **Іконка кошика:**
  - Оновлення SVG коду
  - Додавання badge для кількості
  - Анімація додавання товару

### 4.4 Головна сторінка (Phase 3)
- **Hero-карусель:**
  - 7 слайдів з автопрокруткою
  - Оновлення контенту

- **Секція курсів:**
  - 6 курсів (карусель)
  - Оновлення вигляду карток

- **Секція ментор-коучинг:**
  - Нова секція з шестикутниками
  - Додавання контенту

- **Секція експертів:**
  - Перейменування на "Команда професіоналів"
  - Оновлення контенту

- **Видалення секції цінностей**

### 4.5 Хаб знань (Phase 4)
- **Банер:**
  - Додавання кнопки закриття (X)
  - Оновлення тексту

- **Цитати:**
  - Зміна на 1 цитату замість багатьох
  - Оновлення стилізації

- **Фільтри:**
  - Видалення 3 фільтрів
  - Додавання 3 нових фільтрів
  - Оновлення логіки фільтрації

### 4.6 Івенти та кабінет (Phase 5-6)
- **Календар подій:**
  - Оновлення на 1 подію на день
  - Покращення відображення

- **Кабінет:**
  - Оновлення інтересів (8 у порядку 1-8)
  - Створення сторінки правил програми лояльності

### 4.7 Тестування та деплой (Phase 7)
- **Unit тести:**
  - Тестування нових моделей
  - Тестування views і контроллерів
  - Тестування бізнес-логіки

- **Мануальне тестування:**
  - Перевірка всіх змін
  - Перевірка адаптивності
  - iOS Safari тестування

- **Деплой:**
  - Застосування міграцій на продакшн
  - Збирання статики
  - Моніторинг логів

## 5. ⚠️ КРИТИЧНІ ПИТАННЯ ТА ЗАВДАННЯ

### 5.1 Блокуючі питання
- **SVG-код кошика:** Потрібен новий SVG код для іконки кошика
- **Виправлення слова "коучІнг":** Узгодити правильне написання

### 5.2 Нетермінові питання
- **Описи експертів:** Потрібні для секції "Команда"
- **Механіка знижок:** Уточнити для реферальних посилань

### 5.3 Статистика змін
- **Файли:**
  - Нових: 7 файлів
  - Модифікувати: 15 файлів
  - Міграцій: 4 файли

- **Код:**
  - Python: ~500 рядків нового коду
  - CSS: ~1200 рядків нового коду
  - JavaScript: ~300 рядків нового коду
  - HTML: ~800 рядків нового коду

- **Часові оцінки:**
  - Мінімум: 13 годин
  - Максимум: 18 годин
  - Середнє: 15.5 годин

## 6. 🔧 ТЕХНІЧНІ ДЕТАЛІ ТА ОСОБЛИВОСТІ

### 6.1 PWA (Progressive Web App)
- **manifest.json:**
  - name: "Play Vision"
  - short_name: "PlayVision"
  - start_url: "/"
  - display: "standalone"
  - Іконки різних розмірів

- **Service Worker:**
  - Стратегія Cache-First для статики
  - Стратегія Network-First для контенту
  - no-cache для приватних даних
  - Offline fallback для публічних сторінок

- **iOS специфіка:**
  - meta-теги для Apple
  - splash-екрани
  - специфіка додавання на домашній екран

### 6.2 Аналітика та трекінг
- **Google Analytics 4:**
  - Події: view_item, add_to_cart, purchase, subscribe
  - Конверсійні воронки
  - Відстеження користувачів

- **Meta Pixel:**
  - Трекінг конверсій
  - Ремаркетинг
  - Оптимізація кампаній

- **Pixel Manager:**
  - Керування аналітикою з адмін-панелі
  - Налаштування відстежуваних подій
  - Consent-категорії для GDPR

### 6.3 Paywall система
- **GatedBlock модель:**
  - Поля: title, slug, placement, preview_type, access rules
  - UI-стани: locked (blur+🔒), preview (20с/10%), unlocked
  - CTA кнопки: Оформити підписку, Купити, Увійти

- **Система доступу:**
  - Перевірка entitlements
  - Безпека: серверна перевірка доступу
  - Preview режим для незареєстрованих

- **Події для аналітики:**
  - paywall_impression
  - paywall_preview_end
  - paywall_cta_click
  - unlock_success

### 6.4 Платіжна система
- **3D Secure інтеграція:**
  - Обробка challenge в iframe
  - Вебхуки Success/Fail
  - Стан-машина для відстеження

- **Рекурентні платежі:**
  - Токени для автосписань
  - Керування в кабінеті
  - Налаштування частоти списань

- **Apple Pay / Google Pay:**
  - Інтеграція з Web Payment API
  - Адаптація для мобільних пристроїв
  - Fallback на стандартну форму

### 6.5 Безпека контенту
- **Відео захист:**
  - HLS стрімінг
  - AES-128 шифрування
  - Підписані URL з коротким TTL
  - Динамічний watermark

- **PDF захист:**
  - Вбудований viewer
  - Обмеження копіювання
  - Водяні знаки на документах
  - Обмеження доступу за IP

- **Захист API:**
  - Авторизація через JWT
  - Rate limiting
  - IP блокування
  - CORS налаштування

## 7. 🎨 ДИЗАЙН ТА ІНТЕРФЕЙС

### 7.1 Загальний стиль
- **Кольорова схема:**
  - Основний: Червоний (#FF5252)
  - Додатковий: Темно-сірий (#333)
  - Акцент: Білий (#FFF)
  - Фон: Світло-сірий (#F9F9F9)

- **Типографіка:**
  - Заголовки: Montserrat Bold
  - Основний текст: Open Sans
  - Акцентний текст: Roboto Medium
  - Розміри: 14px/16px/18px/24px/32px

- **Компоненти:**
  - Кнопки (первинні/вторинні)
  - Картки (курсів, експертів, івентів)
  - Форми і поля вводу
  - Навігація та хедер

### 7.2 Адаптивність
- **Брейкпоінти:**
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
  - Large Desktop: > 1440px

- **Особливості iOS Safari:**
  - Фікси для bottom navigation bar
  - PWA встановлення
  - Специфічні поведінки форм

- **Responsive елементи:**
  - Гнучкі контейнери
  - Зображення з різними розмірами
  - Адаптивна навігація
  - Mobile-first підхід

### 7.3 Доступність (WCAG 2.1 AA)
- **Контраст:** Не менше 4.5:1
- **Масштабування:** Підтримка до 200%
- **Клавіатурна навігація:** Повна підтримка Tab
- **Aria атрибути:** Для скрінрідерів
- **Reduced motion:** Для користувачів з вестибулярними розладами

## 8. 📈 МЕТРИКИ ТА ОЦІНКА ЕФЕКТИВНОСТІ

### 8.1 Технічні метрики
- **Core Web Vitals:**
  - LCP ≤ 2.5s (Largest Contentful Paint)
  - CLS ≤ 0.1 (Cumulative Layout Shift)
  - INP ≤ 200ms (Interaction to Next Paint)

- **Швидкість завантаження:**
  - Time to First Byte ≤ 0.8s
  - First Contentful Paint ≤ 1.5s
  - Speed Index ≤ 3.0s

### 8.2 Бізнес-метрики
- **Конверсія:**
  - Реєстрації (% від відвідувань)
  - Підписки (% від зареєстрованих)
  - Утримання (% продовжень підписки)

- **Залучення:**
  - Середній час на сайті
  - Глибина перегляду сторінок
  - Повторні відвідування

### 8.3 AI асистент метрики
- **Answer Coverage:** ≥90% на Core-50
- **First-Contact Resolution:** ≥70%
- **User Rating:** ≥4.5/5
- **Unknown Intents/Week:** Постійне зменшення
- **Source Quality:** % відповідей з релевантними посиланнями

## 9. 📚 ДОДАТКОВІ МАТЕРІАЛИ

### 9.1 Корисні команди
```bash
# Міграції
python3 manage.py makemigrations
python3 manage.py migrate

# Створення резервної копії
python3 manage.py dumpdata > backups/backup_$(date +%Y%m%d_%H%M%S).json

# Запуск сервера
python3 manage.py runserver

# Збирання статики
python3 manage.py collectstatic --noinput
```

### 9.2 Контакти та підтримка
- **Технічні питання:** Перевірити документацію Django і Alpine.js
- **Бізнес-логіка:** Уточнити у клієнта
- **Виявлені баги:** Перевірити консоль (F12) та Django logs

### 9.3 Гарантії якості
- ✅ БЕЗ конфліктів з існуючим кодом
- ✅ БЕЗ дублювання (DRY principle)
- ✅ БЕЗ !important (0 знайдено)
- ✅ БЕЗ inline styles
- ✅ Використання існуючих компонентів
- ✅ Responsive для всіх пристроїв
- ✅ iOS Safari compatibility

---

**Документ оновлено:** 9 жовтня 2025