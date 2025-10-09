# 🎯 ТОЧНИЙ ПЛАН ДОРОБКИ AI (враховує існуючий код)

## ЩО ВЖЕ ПРАЦЮЄ ✅
- SimpleVectorStore (пошук в базі)
- load_knowledge_base.py (завантаження MD/TXT)
- AIAccessPolicy (є CTA, але не динамічний)
- OpenAI/Anthropic клієнти
- Логування AIQuery

## ЩО ТРЕБА ДОРОБИТИ ❌

### 1. ЛОГІКА "НАША БАЗА → LLM" (30 хв)
```python
# apps/ai/services.py - process_query()

# ЗАРАЗ:
relevant_docs = self.vector_store.search(query, access_level, limit=5)
prompt = self._build_prompt(query, relevant_docs, access_level)
llm_response = self.llm_client.generate(prompt)

# ТРЕБА:
relevant_docs = self.vector_store.search(query, access_level, limit=5)

# Перевірка релевантності
best_score = max([doc['score'] for doc in relevant_docs]) if relevant_docs else 0

if best_score > 0.5:  # Є хороші результати
    # Відповідь на основі НАШОЇ бази
    prompt = self._build_prompt_with_docs(query, relevant_docs)
    sources = relevant_docs
else:
    # Відповідь з ЗАГАЛЬНОЇ LLM бази
    prompt = self._build_general_prompt(query)
    sources = []

llm_response = self.llm_client.generate(prompt)
```

### 2. RESPONSEFORMATTER (1 год)
```python
# apps/ai/services.py - додати новий клас

class ResponseFormatter:
    """Форматує відповіді згідно вимог клієнта"""
    
    def format(self, raw_response, sources, user_level):
        # 1. Обрізати до 4-6 абзаців
        paragraphs = raw_response.split('\n\n')
        if len(paragraphs) > 6:
            paragraphs = paragraphs[:6]
        
        # 2. Додати структуру (якщо немає)
        # 3. Додати emoji
        # 4. Додати джерела якщо є
        if sources:
            response += "\n\n📚 Джерела:\n"
            for source in sources[:3]:
                response += f"• {source['title']}\n"
        
        return response
```

### 3. CTAMANAGER (1 год)
```python
# apps/ai/services.py - додати клас

class CTAManager:
    """Динамічний вибір CTA"""
    
    def get_cta(self, session_queries_count, has_sources, user_level):
        # session_queries_count - скільки запитів в сесії
        
        if user_level in ['subscriber_l1', 'subscriber_l2', 'admin']:
            return ""  # Підписники - без CTA
        
        if session_queries_count < 2:
            return ""  # Перші 1-2 запити - без CTA
        
        if has_sources:
            # Є матеріал - прямий CTA
            return "\n\n💎 Детальніше в курсі за 399 грн або в підписці C-Vision\n👉 /pricing/"
        else:
            # М'який CTA
            return "\n\n💡 Оформіть підписку для експертних відповідей та доступу до курсів\n👉 /pricing/"
```

### 4. DISCLAIMERMANAGER (30 хв)
```python
# apps/ai/services.py

class DisclaimerManager:
    HEALTH = ['біль', 'травма', 'втома', 'хвороба']
    LEGAL = ['контракт', 'договір', 'права', 'закон']
    
    def add_disclaimer(self, query, response):
        query_lower = query.lower()
        
        if any(word in query_lower for word in self.HEALTH):
            return response + "\n\n⚠️ Освітня інформація, не медична порада. При болях - до лікаря!"
        
        if any(word in query_lower for word in self.LEGAL):
            return response + "\n\n⚠️ Юридичні питання - до спортивного юриста."
        
        return response
```

### 5. СИСТЕМА ОЦІНОК (30 хв)
```python
# apps/ai/models.py - додати до AIQuery

user_thumbs_up = models.BooleanField(null=True, blank=True)
user_feedback_text = models.TextField(blank=True)
sources_used = models.JSONField(default=list)
cta_shown = models.CharField(max_length=200, blank=True)

# apps/ai/views.py - новий endpoint

class AIRateView(View):
    def post(self, request, query_id):
        query = get_object_or_404(AIQuery, id=query_id)
        data = json.loads(request.body)
        
        query.user_thumbs_up = data.get('thumbs_up')
        query.user_feedback_text = data.get('feedback', '')
        query.save()
        
        return JsonResponse({'success': True})
```

### 6. ТРЕКІНГ СЕСІЇ (15 хв)
```python
# apps/ai/views.py - AIAskAPIView

# Додати підрахунок запитів в сесії
session_key = f"ai_queries_{request.session.session_key or 'anonymous'}"
queries_count = cache.get(session_key, 0) + 1
cache.set(session_key, queries_count, timeout=3600)  # 1 година

# Передати в process_query
result = ai_service.process_query(
    query, 
    user=request.user,
    session_queries_count=queries_count  # НОВИЙ параметр
)
```

### 7. ІНТЕГРАЦІЯ ВСЬОГО (1 год)
```python
# apps/ai/services.py - оновити process_query()

def process_query(self, query, user=None, session_id=None, session_queries_count=1):
    # ... existing code ...
    
    # Пошук в базі
    relevant_docs = self.vector_store.search(query, access_level, limit=5)
    best_score = max([d['score'] for d in relevant_docs]) if relevant_docs else 0
    
    # Вибір стратегії
    if best_score > 0.5:
        prompt = self._build_prompt_with_docs(query, relevant_docs)
        sources = relevant_docs
    else:
        prompt = self._build_general_prompt(query)
        sources = []
    
    # LLM генерація
    llm_response = self.llm_client.generate(prompt)
    
    # НОВI: Форматування
    formatter = ResponseFormatter()
    formatted = formatter.format(llm_response, sources, access_level)
    
    # НОВI: CTA
    cta_manager = CTAManager()
    cta = cta_manager.get_cta(session_queries_count, bool(sources), access_level)
    formatted += cta
    
    # НОВI: Дисклеймер
    disclaimer_manager = DisclaimerManager()
    final_response = disclaimer_manager.add_disclaimer(query, formatted)
    
    # Логування (зберегти sources, cta)
    query_log = self._log_query(
        query, final_response, user, session_id, access_level, 
        sources, response_time, tokens_used,
        cta_shown=cta,  # НОВЕ
        sources_used=[s['title'] for s in sources]  # НОВЕ
    )
    
    return {
        'success': True,
        'response': final_response,
        'query_id': query_log.id,
        'sources': sources,
        'has_sources': bool(sources)
    }
```

## ПОСЛІДОВНІСТЬ ВИКОНАННЯ

**5 ГОДИН РОБОТИ:**

1. ✅ API ключ (5 хв)
2. ✅ Дописати Core-50 (1-2 год) → можна пропустити спочатку
3. ✅ Логіка "наша база → LLM" (30 хв)
4. ✅ ResponseFormatter (1 год)
5. ✅ CTAManager (1 год)
6. ✅ DisclaimerManager (30 хв)
7. ✅ Система оцінок (30 хв)
8. ✅ Трекінг сесії (15 хв)
9. ✅ Інтеграція (1 год)
10. ✅ Тестування (30 хв)

## МІГРАЦІЇ
```bash
python manage.py makemigrations ai
python manage.py migrate
```

## ТЕСТУВАННЯ
```bash
# 1. Завантажити існуючу базу
python manage.py load_knowledge_base --clear

# 2. Тест "є в базі"
curl -X POST /ai/ask/ -d '{"query": "Що таке Play Vision?"}'
# Має: джерела, без загального LLM

# 3. Тест "немає в базі"
curl -X POST /ai/ask/ -d '{"query": "Хто виграв Чемпіонат світу 2022?"}'
# Має: без джерел, загальний LLM

# 4. Тест CTA
# Запит 1-2: без CTA
# Запит 3+: з CTA

# 5. Тест дисклеймер
curl -X POST /ai/ask/ -d '{"query": "У мене болить коліно"}'
# Має: дисклеймер про здоров'я
```

---

**ГОТОВИЙ СТАРТУВАТИ З КРОКУ 1?** 🚀

