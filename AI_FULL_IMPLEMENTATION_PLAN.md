# 🤖 AI ПОВНА РЕАЛІЗАЦІЯ - КОРОТКИЙ ПЛАН

## МЕТА
AI шукає відповіді СПОЧАТКУ в нашій базі знань → якщо немає → в загальній LLM базі

## КРОК 1: ПІДГОТОВКА (10 хв)
- [ ] Отримати OpenAI API ключ від клієнта
- [ ] Додати в .env: `OPENAI_API_KEY=sk-...`
- [ ] Перевірити чи працює: `python -c "import openai"`

## КРОК 2: БАЗА ЗНАНЬ (1 год)
- [ ] Дописати решту Core-50 питань (38 шт)
- [ ] Створити `load_core50.py` команду
- [ ] Завантажити в KnowledgeBase з metadata
- [ ] Додати існуючі MD файли (faq_public.md etc)

## КРОК 3: ОНОВИТИ AIAgentService (2 год)

### 3.1 Логіка пошуку
```python
def process_query(query, user):
    # 1. Шукаємо в НАШІЙ базі (векторний пошук)
    our_docs = vector_store.search(query, limit=5)
    
    if our_docs and relevance_score > 0.7:
        # Є хороші результати в нашій базі
        response = llm.generate(prompt_with_our_docs)
        sources = our_docs
    else:
        # Немає в нашій базі - загальний LLM
        response = llm.generate(general_prompt)
        sources = []
    
    # 2. Форматування (4-6 абзаців)
    # 3. Додати CTA (після 2-3 запитів)
    # 4. Додати дисклеймер якщо потрібно
    # 5. Логування
```

### 3.2 ResponseFormatter
```python
- Обмежити до 4-6 абзаців
- Структура: Суть → Кроки → Очікування → Джерела
- Emoji для читабельності
```

### 3.3 CTAManager
```python
- Після 2-3 запитів: м'який CTA
- Якщо є матеріал: прямий CTA з посиланням
- Динамічні ціни
```

### 3.4 DisclaimerManager
```python
HEALTH_KEYWORDS = ['біль', 'травма', 'втома']
LEGAL_KEYWORDS = ['контракт', 'договір']
# Авто-вставка дисклеймерів
```

## КРОК 4: ФАЙЛОВА СИСТЕМА (30 хв)
```python
# apps/ai/management/commands/add_knowledge.py
class Command:
    def handle(self, file_path):
        # Зчитати MD/TXT файл
        # Створити KnowledgeBase запис
        # Додати metadata, теги
        # Індексувати для пошуку
```

## КРОК 5: ADMIN ПАНЕЛЬ (30 хв)
- [ ] Кнопка "Завантажити файл" в admin
- [ ] Список всіх документів + видалення
- [ ] Тестування AI з різними запитами
- [ ] Dashboard метрик

## КРОК 6: СИСТЕМА ОЦІНОК (30 хв)
```python
# AIQuery додати поля:
thumbs_up/thumbs_down
feedback_text
sources_used = JSONField
```

## КРОК 7: ТЕСТУВАННЯ (1 год)
```bash
# 1. Завантажити базу
python manage.py load_core50
python manage.py load_knowledge_base

# 2. Тестові запити
# - Є в базі → має дати відповідь з джерелами
# - Немає в базі → загальна відповідь LLM
# - CTA показується правильно
# - Дисклеймери де потрібно

# 3. Різні рівні користувачів
```

## ФАЙЛИ ДЛЯ СТВОРЕННЯ/ОНОВЛЕННЯ
1. `apps/ai/services.py` - оновити AIAgentService
2. `apps/ai/management/commands/load_core50.py` - нова команда
3. `apps/ai/management/commands/add_knowledge.py` - додавання файлів
4. `apps/ai/admin.py` - admin інтерфейс
5. `apps/ai/models.py` - додати поля для оцінок
6. Дописати Core-50 питання

## КОМАНДИ ЗАПУСКУ
```bash
# Завантажити API ключ
export OPENAI_API_KEY=sk-...

# Завантажити базу
python manage.py load_core50
python manage.py load_knowledge_base

# Додати новий файл
python manage.py add_knowledge path/to/file.md --category=training --access=subscriber

# Тест
python manage.py test apps.ai
```

## ПРІОРИТЕТ ВИКОНАННЯ
1. API ключ + перевірка (5 хв)
2. Дописати Core-50 (1-2 год)
3. Створити load_core50 (30 хв)
4. Оновити AIAgentService (2 год)
5. Тестування (1 год)
**TOTAL: ~5-6 годин роботи**

## SUCCESS CRITERIA
✅ AI відповідає на Core-50 з нашої бази
✅ Якщо питання нове - відповідає з LLM
✅ Формат: 4-6 абзаців, структурно
✅ CTA показується після 2-3 запитів
✅ Можна додавати нові MD файли
✅ Дисклеймери автоматичні
✅ Користувачі можуть оцінювати відповіді

---

**ГОТОВИЙ ПОЧАТИ? СКАЖИ "СТАРТ" І ПОЧИНАЮ З КРОКУ 1** 🚀

