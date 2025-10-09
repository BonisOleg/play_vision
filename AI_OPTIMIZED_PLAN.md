# 🎯 ОПТИМІЗОВАНИЙ ПЛАН AI (використовує існуючий код)

## ✅ ВЖЕ Є В КОДІ (НЕ ТРЕБА СТВОРЮВАТИ!)

### 1. CTA логіка ✅
```python
# apps/ai/services.py:344
class AIAccessPolicy:
    def filter_response(response, access_level):
        # ВЖЕ додає CTA!
        if policy.get('cta_message'):
            response += f"\n\n{policy['cta_message']}"
```
**НЕ СТВОРЮВАТИ CTAManager - вже є!**

### 2. Session tracking ✅
```python
# apps/ai/views.py:62
session_id = request.session.session_key
# AIQuery вже зберігає session_id
```
**НЕ СТВОРЮВАТИ - вже працює!**

### 3. Система оцінок ✅
```python
# apps/ai/models.py:79-81
user_rating = models.PositiveIntegerField(null=True)
user_feedback = models.TextField(blank=True)
```
**Модель ГОТОВА! Треба тільки UI та API endpoint**

### 4. Inline styles та !important ✅
- Inline styles - тільки для динамічних значень (progress bars, modals)
- !important - тільки в accessibility (prefers-reduced-motion)
**Все OK! Нічого виправляти**

---

## ❌ ЩО ТРЕБА ДОРОБИТИ (3 години)

### КРОК 1: Логіка "наша база → LLM" (30 хв)

**ОНОВИТИ:** `apps/ai/services.py` метод `process_query()` (рядок 53)

```python
# ПІСЛЯ рядка 76 (relevant_docs = ...)
# ДОДАТИ:

# Перевірка релевантності
best_score = max([d['score'] for d in relevant_docs]) if relevant_docs else 0
has_good_sources = best_score > 0.5

# ЗАМІНИТИ рядок 79 (_build_prompt):
if has_good_sources:
    # Є хороші джерела в НАШІЙ базі
    prompt = self._build_prompt(query, relevant_docs, access_level)
else:
    # Немає в базі - використати загальний промпт
    prompt = self._build_general_prompt(query, access_level)
    relevant_docs = []  # Очистити джерела
```

**ДОДАТИ НОВИЙ МЕТОД** після `_build_prompt()` (після рядка 168):

```python
def _build_general_prompt(self, query: str, access_level: str) -> str:
    """Промпт без контексту - для загальних питань"""
    return f"""Ти - AI помічник Play Vision, освітньої платформи для футбольних фахівців.

Користувач запитує: {query}

Рівень доступу: {access_level}

Інструкції:
1. Відповідай українською мовою
2. Дай корисну загальну відповідь (4-6 абзаців максимум)
3. Структура: Суть → Кроки → Поради
4. Згадай що Play Vision може мати курси на цю тему

Відповідь:"""
```

---

### КРОК 2: ResponseFormatter (1 год)

**ОНОВИТИ:** `apps/ai/services.py` метод `filter_response()` в AIAccessPolicy (рядок 344)

```python
def filter_response(self, response: str, access_level: str, sources: List = None) -> str:
    """Фільтрація + форматування відповіді"""
    policy = self.POLICIES.get(access_level, self.POLICIES['guest'])
    
    # 1. ФОРМАТУВАННЯ: Обрізати до 4-6 абзаців
    paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
    if len(paragraphs) > 6:
        paragraphs = paragraphs[:6]
        paragraphs[-1] += "..."
    response = '\n\n'.join(paragraphs)
    
    # 2. Обмеження довжини (існуюче)
    if policy.get('max_response_length') and len(response) > policy['max_response_length']:
        response = response[:policy['max_response_length']] + "..."
    
    # 3. ДОДАТИ ДЖЕРЕЛА (якщо є)
    if sources and len(sources) > 0:
        response += "\n\n📚 **Джерела з бази Play Vision:**"
        for source in sources[:3]:
            response += f"\n• {source['title']}"
    
    # 4. CTA (існуюче - залишити як є)
    if policy.get('cta_message'):
        response += f"\n\n{policy['cta_message']}"
    
    return response
```

**ОНОВИТИ ВИКЛИК** в `process_query()` (рядок 85):
```python
# БУЛО:
filtered_response = self.access_policy.filter_response(llm_response, access_level)

# СТАЛО:
filtered_response = self.access_policy.filter_response(
    llm_response, 
    access_level,
    sources=relevant_docs  # ДОДАТИ параметр
)
```

---

### КРОК 3: Динамічний CTA (30 хв)

**ОНОВИТИ:** `apps/ai/services.py` в POLICIES (рядок 310)

```python
# ЗАМІНИТИ статичні cta_message на функцію
# ДОДАТИ метод в AIAccessPolicy після filter_response:

def _get_dynamic_cta(self, access_level: str, has_sources: bool, queries_count: int) -> str:
    """Динамічний CTA на основі контексту"""
    
    # Підписники - без CTA
    if access_level in ['subscriber_l1', 'subscriber_l2', 'admin']:
        return ""
    
    # Перші 1-2 запити - без CTA
    if queries_count < 2:
        return ""
    
    # Якщо є джерела - прямий CTA
    if has_sources:
        return "\n\n💎 **Детальніше в наших курсах**\nДоступні за підпискою C-Vision або окремо від 399 грн\n👉 [Переглянути тарифи](/pricing/)"
    
    # М'який CTA
    if access_level == 'guest':
        return "\n\n💡 Зареєструйтесь для більш детальних відповідей та доступу до експертних матеріалів"
    else:
        return "\n\n💡 Підписка відкриває доступ до всіх курсів та експертних консультацій"

# ОНОВИТИ filter_response (видалити static CTA, використати dynamic):
def filter_response(self, response, access_level, sources=None, queries_count=1):
    # ... форматування ...
    
    # Замість static cta_message:
    cta = self._get_dynamic_cta(access_level, bool(sources), queries_count)
    if cta:
        response += cta
    
    return response
```

**ДОДАТИ queries_count** в `process_query()`:

```python
# ДОДАТИ параметр:
def process_query(self, query, user=None, session_id=None, queries_count=1):
    # ...
    
    # Передати в filter_response:
    filtered_response = self.access_policy.filter_response(
        llm_response, access_level, relevant_docs, queries_count
    )
```

---

### КРОК 4: DisclaimerManager (30 хв)

**ДОДАТИ КЛАС** в `apps/ai/services.py` після AIAccessPolicy (рядок ~357):

```python
class DisclaimerManager:
    """Автоматичні дисклеймери"""
    
    HEALTH_KEYWORDS = ['біль', 'травма', 'втома', 'хвороба', 'лікар', 'медицин']
    LEGAL_KEYWORDS = ['контракт', 'договір', 'права', 'закон', 'юрист']
    FINANCIAL_KEYWORDS = ['гроші', 'оплата', 'ціна', 'кредит', 'позика']
    
    @staticmethod
    def add_disclaimer(query: str, response: str) -> str:
        """Додати дисклеймер якщо потрібно"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in DisclaimerManager.HEALTH_KEYWORDS):
            response += "\n\n⚠️ **Важливо:** Це освітня інформація, не медична порада. При болях/травмах - обов'язково до лікаря!"
        
        elif any(word in query_lower for word in DisclaimerManager.LEGAL_KEYWORDS):
            response += "\n\n⚠️ **Важливо:** Юридичні питання - до спортивного юриста."
        
        elif any(word in query_lower for word in DisclaimerManager.FINANCIAL_KEYWORDS):
            response += "\n\n⚠️ **Важливо:** Фінансові рішення індивідуальні, консультуйтесь з фахівцем."
        
        return response
```

**ДОДАТИ В process_query()** після filter_response:

```python
# Після рядка 85:
filtered_response = self.access_policy.filter_response(...)

# ДОДАТИ:
filtered_response = DisclaimerManager.add_disclaimer(query, filtered_response)
```

---

### КРОК 5: Трекінг кількості запитів (15 хв)

**ОНОВИТИ:** `apps/ai/views.py` в AIAskAPIView (рядок 43)

```python
def post(self, request):
    # ... існуючий код ...
    
    # ДОДАТИ ПІСЛЯ рядка 62 (session_id = ...):
    # Підрахунок запитів в сесії
    from django.core.cache import cache
    session_key = f"ai_queries_{session_id}"
    queries_count = cache.get(session_key, 0) + 1
    cache.set(session_key, queries_count, timeout=3600)  # 1 година
    
    # ОНОВИТИ виклик (рядок ~67):
    result = ai_service.process_query(
        query,
        user=request.user if request.user.is_authenticated else None,
        session_id=session_id,
        queries_count=queries_count  # ДОДАТИ
    )
```

---

### КРОК 6: UI для оцінок (30 хв)

**СТВОРИТИ:** `apps/ai/urls.py` - ДОДАТИ endpoint:

```python
# ДОДАТИ до urlpatterns:
path('rate/<int:query_id>/', views.AIRateView.as_view(), name='rate'),
```

**СТВОРИТИ:** `apps/ai/views.py` - ДОДАТИ клас після AIAskAPIView:

```python
class AIRateView(View):
    """Оцінка відповіді AI"""
    
    def post(self, request, query_id):
        try:
            query = get_object_or_404(AIQuery, id=query_id)
            data = json.loads(request.body)
            
            # Thumbs up (True) or down (False)
            if 'thumbs_up' in data:
                query.user_rating = 5 if data['thumbs_up'] else 1
            
            # Текстовий feedback
            if 'feedback' in data:
                query.user_feedback = data['feedback']
            
            query.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
```

**ОНОВИТИ:** `templates/ai/chat.html` - ДОДАТИ кнопки оцінки (знайти де виводиться response):

```html
<!-- Після відповіді AI додати: -->
<div class="ai-rating" data-query-id="{{ query.id }}">
    <button class="rating-btn thumbs-up" onclick="rateAI({{ query.id }}, true)">
        👍 Корисно
    </button>
    <button class="rating-btn thumbs-down" onclick="rateAI({{ query.id }}, false)">
        👎 Не корисно
    </button>
</div>
```

**ОНОВИТИ:** `static/js/components/ai-chat.js` - ДОДАТИ функцію:

```javascript
function rateAI(queryId, thumbsUp) {
    fetch(`/ai/rate/${queryId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ thumbs_up: thumbsUp })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Показати повідомлення "Дякуємо!"
            const btn = event.target;
            btn.classList.add('rated');
            btn.disabled = true;
        }
    });
}
```

---

### КРОК 7: Міграції (5 хв)

**AIQuery вже має всі поля!** Перевірити чи треба міграція:

```bash
python manage.py makemigrations ai
# Якщо є зміни:
python manage.py migrate
```

---

## ПОСЛІДОВНІСТЬ ВИКОНАННЯ

### ✅ КРОК 1: Логіка пошуку (30 хв)
1. Додати `_build_general_prompt()`
2. Оновити `process_query()` - перевірка relevance
3. Тест: запит в базі vs поза базою

### ✅ КРОК 2: Форматування (1 год)
1. Оновити `filter_response()` - 4-6 абзаців + джерела
2. Оновити виклик в `process_query()`
3. Тест: перевірити формат відповідей

### ✅ КРОК 3: Динамічний CTA (30 хв)
1. Додати `_get_dynamic_cta()`
2. Інтегрувати в `filter_response()`
3. Додати `queries_count` параметр
4. Тест: CTA після 2-3 запитів

### ✅ КРОК 4: Дисклеймери (30 хв)
1. Створити `DisclaimerManager`
2. Інтегрувати в `process_query()`
3. Тест: запити з health/legal keywords

### ✅ КРОК 5: Трекінг (15 хв)
1. Додати cache в `AIAskAPIView`
2. Передати `queries_count`
3. Тест: перевірити підрахунок

### ✅ КРОК 6: UI оцінок (30 хв)
1. Додати endpoint `/rate/`
2. Створити `AIRateView`
3. Додати UI в template
4. Додати JS функцію
5. Тест: оцінити відповідь

### ✅ КРОК 7: Тестування (30 хв)
```bash
# Завантажити базу
python manage.py load_knowledge_base --clear

# Запустити сервер
python manage.py runserver

# Тести:
# 1. Запит в базі → має джерела, форматування OK
# 2. Запит поза базою → загальна відповідь
# 3. 3 запити → CTA з'являється
# 4. Запит з "біль" → дисклеймер
# 5. Оцінка → зберігається
```

---

## TOTAL: 3 години

**БЕЗ дублювання коду!**
**БЕЗ нових inline styles!**
**БЕЗ !important!**
**Максимум використання існуючого!**

---

## ФАЙЛИ ДЛЯ РЕДАГУВАННЯ

1. ✏️ `apps/ai/services.py` - основна логіка (7 змін)
2. ✏️ `apps/ai/views.py` - трекінг + rating endpoint (2 додавання)
3. ✏️ `apps/ai/urls.py` - 1 новий URL
4. ✏️ `templates/ai/chat.html` - UI оцінок (1 блок)
5. ✏️ `static/js/components/ai-chat.js` - функція rating (1 функція)

**НОВИХ ФАЙЛІВ: 0**
**НОВИХ КЛАСІВ: 1** (DisclaimerManager)
**ВСЬОГО РЕДАГУВАНЬ: ~10**

---

**ГОТОВИЙ ПОЧИНАТИ ВИКОНАННЯ? 🚀**

