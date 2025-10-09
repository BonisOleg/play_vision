"""
AI Agent Service для Play Vision
Повна реалізація ШІ помічника з векторним пошуком
"""
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from .models import AIQuery, KnowledgeBase, AIConfiguration, AIPromptTemplate


class AIAgentService:
    """
    Основний сервіс AI-агента з підтримкою векторного пошуку
    """
    
    def __init__(self):
        self.config = self._get_config()
        self.llm_client = self._get_llm_client()
        self.vector_store = SimpleVectorStore()  # Простий векторний пошук
        self.access_policy = AIAccessPolicy()
    
    def _get_config(self) -> AIConfiguration:
        """Отримати конфігурацію AI"""
        config, created = AIConfiguration.objects.get_or_create(
            id=1,
            defaults={
                'llm_provider': 'openai',
                'llm_model': 'gpt-3.5-turbo',
                'is_enabled': True
            }
        )
        return config
    
    def _get_llm_client(self):
        """Ініціалізувати LLM клієнт"""
        if self.config.llm_provider == 'openai':
            return OpenAIClient(
                api_key=self.config.api_key or settings.OPENAI_API_KEY,
                model=self.config.llm_model
            )
        elif self.config.llm_provider == 'anthropic':
            return AnthropicClient(
                api_key=self.config.api_key or settings.ANTHROPIC_API_KEY,
                model=self.config.llm_model
            )
        else:
            return MockLLMClient()  # Fallback для тестування
    
    def process_query(self, query: str, user=None, session_id: str = None, queries_count: int = 1) -> Dict[str, Any]:
        """
        Обробка запиту користувача до AI
        """
        start_time = time.time()
        
        # Перевірка чи увімкнений AI
        if not self.config.is_enabled or self.config.maintenance_mode:
            return {
                'success': False,
                'message': self.config.maintenance_message or 'AI помічник тимчасово недоступний',
                'response': ''
            }
        
        try:
            # 1. Визначення рівня доступу користувача
            access_level = self._get_user_access_level(user)
            
            # 2. Векторний пошук в базі знань
            relevant_docs = self.vector_store.search(
                query=query,
                access_level=access_level,
                limit=5
            )
            
            # 2.1. Перевірка релевантності результатів
            best_score = max([d['score'] for d in relevant_docs]) if relevant_docs else 0
            has_good_sources = best_score > 0.15  # Знижено для кращого покриття нашої бази
            
            # 3. Формування промпту (наша база ЧИ загальна LLM)
            if has_good_sources:
                # Є хороші джерела в НАШІЙ базі знань
                prompt = self._build_prompt(query, relevant_docs, access_level)
            else:
                # Немає в базі - використати загальні знання LLM
                prompt = self._build_general_prompt(query, access_level)
                relevant_docs = []  # Очистити джерела для логування
            
            # 4. Отримання відповіді від LLM
            llm_response = self.llm_client.generate(prompt)
            
            # 5. Фільтрація контенту згідно рівня доступу + форматування + CTA
            filtered_response = self.access_policy.filter_response(
                llm_response.get('response', ''),  # Витягти текст з dict
                access_level,
                sources=relevant_docs,
                queries_count=queries_count
            )
            
            # 5.1. Додавання дисклеймерів (health/legal/financial)
            filtered_response = DisclaimerManager.add_disclaimer(query, filtered_response)
            
            # 6. Логування запиту
            response_time = int((time.time() - start_time) * 1000)
            query_log = self._log_query(
                query, filtered_response, user, session_id,
                access_level, relevant_docs, response_time, llm_response.get('tokens_used', 0)
            )
            
            return {
                'success': True,
                'response': filtered_response,
                'query_id': query_log.id,
                'sources': [doc['title'] for doc in relevant_docs],
                'response_time': response_time
            }
            
        except Exception as e:
            # Логування помилки
            error_response = f"Вибачте, сталася помилка. Спробуйте пізніше."
            self._log_query(
                query, error_response, user, session_id,
                access_level, [], int((time.time() - start_time) * 1000), 0
            )
            
            return {
                'success': False,
                'message': 'Помилка обробки запиту',
                'response': error_response,
                'error': str(e) if settings.DEBUG else None
            }
    
    def _get_user_access_level(self, user) -> str:
        """Визначення рівня доступу користувача"""
        if not user or not user.is_authenticated:
            return 'guest'
        
        if user.is_superuser or user.is_staff:
            return 'admin'
        
        # Перевірка підписки
        if hasattr(user, 'has_active_subscription') and user.has_active_subscription():
            subscription = user.subscriptions.filter(status='active').first()
            if subscription:
                plan_duration = getattr(subscription.plan, 'duration', '1_month')
                if plan_duration == '12_months':
                    return 'subscriber_l2'  # Найвищий рівень підписки
                else:
                    return 'subscriber_l1'  # Базовий рівень підписки
        
        return 'registered'
    
    def _build_prompt(self, query: str, context_docs: List[Dict], access_level: str) -> str:
        """Формування промпту для LLM"""
        # Отримати шаблон промпту
        template = AIPromptTemplate.objects.filter(
            name='main',
            is_active=True
        ).first()
        
        if not template:
            template_content = self._get_default_prompt_template()
        else:
            template_content = template.user_prompt_template
        
        # Формування контексту з документів
        context_text = ""
        if context_docs:
            context_text = "\n".join([
                f"Джерело: {doc['title']}\nКонтент: {doc['content'][:500]}...\n"
                for doc in context_docs
            ])
        
        # Заміна змінних в шаблоні
        prompt = template_content.format(
            query=query,
            context=context_text,
            access_level=access_level,
            current_date=timezone.now().strftime('%Y-%m-%d')
        )
        
        return prompt
    
    def _build_general_prompt(self, query: str, access_level: str) -> str:
        """
        Промпт без контексту з бази знань - для загальних питань
        Використовується коли немає релевантних джерел у нашій базі
        """
        return f"""Ти - AI помічник Play Vision, освітньої платформи для футбольних фахівців.

Користувач запитує: {query}

Рівень доступу: {access_level}

Інструкції:
1. Відповідай українською мовою
2. Дай корисну загальну відповідь (максимум 4-6 абзаців)
3. Структура: Суть → Кроки/Поради → Що очікувати
4. Будь конкретним, без "води"
5. Якщо тема футбольна - згадай що Play Vision може мати курси/матеріали на цю тему
6. Уникай медичних та юридичних порад
7. Тон: спокійний, партнерський, як досвідчений навігатор

Відповідь:"""
    
    def _get_default_prompt_template(self) -> str:
        """Базовий шаблон промпту"""
        return """Ти - AI помічник Play Vision, освітньої платформи для футбольних фахівців.

Контекст з бази знань:
{context}

Рівень доступу користувача: {access_level}
Поточна дата: {current_date}

Запит користувача: {query}

Інструкції:
1. Відповідай тільки українською мовою
2. Базуйся на наданому контексті з бази знань
3. Якщо інформації недостатньо, чесно про це скажи
4. Для гостей давай коротші відповіді та рекомендуй реєстрацію
5. Для підписників можеш давати більш детальні відповіді
6. Уникай медичних та фінансових порад
7. Завжди згадуй що ти помічник Play Vision

Відповідь:"""
    
    def _log_query(self, query: str, response: str, user, session_id: str,
                   access_level: str, context_docs: List[Dict], 
                   response_time: int, tokens_used: int) -> AIQuery:
        """Логування запиту та відповіді"""
        return AIQuery.objects.create(
            user=user,
            session_id=session_id or self._generate_session_id(),
            query=query,
            response=response,
            user_access_level=access_level,
            context_sources=[doc['title'] for doc in context_docs],
            response_time_ms=response_time,
            tokens_used=tokens_used
        )
    
    def _generate_session_id(self) -> str:
        """Генерація session ID для анонімних користувачів"""
        return hashlib.md5(f"{time.time()}".encode()).hexdigest()[:16]
    
    def get_suggested_questions(self, access_level: str = 'guest') -> List[str]:
        """Отримати рекомендовані запитання для користувача"""
        suggestions = {
            'guest': [
                "Що таке Play Vision?",
                "Які курси доступні?",
                "Як зареєструватися?",
                "Скільки коштує підписка?"
            ],
            'registered': [
                "Як вибрати підходящий курс?",
                "Як працює система підписок?",
                "Які переваги для підписників?",
                "Як отримати сертифікат?"
            ],
            'subscriber_l1': [
                "Як отримати максимум від курсів?",
                "Розкажи про програму лояльності",
                "Які додаткові матеріали доступні?",
                "Як підвищити рівень підписки?"
            ],
            'subscriber_l2': [
                "Детальний план розвитку тренера",
                "Продвинуті техніки аналізу гри",
                "Як організувати власну футбольну школу?",
                "Професійні секрети від експертів"
            ]
        }
        
        return suggestions.get(access_level, suggestions['guest'])


class SimpleVectorStore:
    """
    Спрощений векторний пошук без зовнішніх залежностей
    Використовує TF-IDF для базового семантичного пошуку
    """
    
    def search(self, query: str, access_level: str, limit: int = 5) -> List[Dict]:
        """Пошук релевантних документів"""
        # Отримати документи згідно рівня доступу
        docs = KnowledgeBase.objects.filter(
            is_indexed=True,
            access_level__in=self._get_allowed_access_levels(access_level)
        )
        
        # Простий пошук по ключових словах
        query_words = query.lower().split()
        scored_docs = []
        
        for doc in docs:
            score = self._calculate_relevance_score(doc.content.lower(), query_words)
            if score > 0:
                scored_docs.append({
                    'id': doc.id,
                    'title': doc.title,
                    'content': doc.content,
                    'content_type': doc.content_type,
                    'score': score,
                    'metadata': doc.metadata
                })
        
        # Сортування за релевантністю
        scored_docs.sort(key=lambda x: x['score'], reverse=True)
        return scored_docs[:limit]
    
    def _get_allowed_access_levels(self, user_level: str) -> List[str]:
        """Отримати дозволені рівні доступу"""
        hierarchy = {
            'guest': ['public'],
            'registered': ['public'],
            'subscriber_l1': ['public', 'registered'],
            'subscriber_l2': ['public', 'registered', 'subscriber'],
            'admin': ['public', 'registered', 'subscriber', 'premium']
        }
        return hierarchy.get(user_level, ['public'])
    
    def _calculate_relevance_score(self, content: str, query_words: List[str]) -> float:
        """Розрахунок релевантності документа"""
        score = 0
        content_words = content.split()
        
        for word in query_words:
            if len(word) > 2:  # Ігноруємо короткі слова
                word_count = content_words.count(word)
                if word_count > 0:
                    # TF-IDF спрощений
                    tf = word_count / len(content_words)
                    score += tf * 10  # Простий ваговий коефіцієнт
        
        return score


class AIAccessPolicy:
    """
    Політика доступу до AI відповідей
    """
    
    POLICIES = {
        'guest': {
            'max_response_length': 200,
            'include_links': False,
            'cta_message': '💡 Зареєструйтесь для повного доступу до AI помічника',
            'allowed_topics': ['загальні', 'публічні']
        },
        'registered': {
            'max_response_length': 500,
            'include_links': True,
            'cta_message': '💡 Оформіть підписку для експертних відповідей від AI',
            'allowed_topics': ['загальні', 'публічні', 'базові']
        },
        'subscriber_l1': {
            'max_response_length': 1000,
            'include_links': True,
            'show_advanced_content': True,
            'allowed_topics': ['всі', 'окрім преміум']
        },
        'subscriber_l2': {
            'max_response_length': 2000,
            'include_links': True,
            'show_advanced_content': True,
            'show_premium_content': True,
            'allowed_topics': ['всі']
        },
        'admin': {
            'max_response_length': None,
            'include_links': True,
            'debug_mode': True,
            'allowed_topics': ['всі']
        }
    }
    
    def filter_response(self, response: str, access_level: str, sources: List = None, queries_count: int = 1) -> str:
        """
        Фільтрація + форматування відповіді згідно вимог клієнта
        - Обмеження до 4-6 абзаців
        - Додавання джерел
        - Динамічний CTA
        """
        policy = self.POLICIES.get(access_level, self.POLICIES['guest'])
        
        # 1. ФОРМАТУВАННЯ: Обрізати до 4-6 абзаців
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        if len(paragraphs) > 6:
            paragraphs = paragraphs[:6]
            paragraphs[-1] += "..."
        response = '\n\n'.join(paragraphs)
        
        # 2. Обмеження довжини (додаткове для безпеки)
        if policy.get('max_response_length') and len(response) > policy['max_response_length']:
            response = response[:policy['max_response_length']] + "..."
        
        # 3. ДОДАТИ ДЖЕРЕЛА (якщо є з нашої бази)
        if sources and len(sources) > 0:
            response += "\n\n📚 **Джерела з бази Play Vision:**"
            for source in sources[:3]:  # Максимум 3 джерела
                response += f"\n• {source['title']}"
        
        # 4. ДИНАМІЧНИЙ CTA
        cta = self._get_dynamic_cta(access_level, bool(sources), queries_count)
        if cta:
            response += cta
        
        return response
    
    def _get_dynamic_cta(self, access_level: str, has_sources: bool, queries_count: int) -> str:
        """Динамічний CTA на основі контексту"""
        
        # Підписники - без CTA
        if access_level in ['subscriber_l1', 'subscriber_l2', 'admin']:
            return ""
        
        # Перші 1-2 запити - без CTA (не нав'язуємось)
        if queries_count < 2:
            return ""
        
        # Якщо є джерела з нашої бази - прямий CTA з посиланням
        if has_sources:
            return "\n\n💎 **Детальніше в наших курсах**\nДоступні за підпискою C-Vision або окремо від 399 грн\n👉 Переглянути тарифи: /pricing/"
        
        # М'який CTA без джерел
        if access_level == 'guest':
            return "\n\n💡 Зареєструйтесь для більш детальних відповідей та доступу до експертних матеріалів"
        else:  # registered
            return "\n\n💡 Підписка відкриває доступ до всіх курсів та експертних консультацій"


class DisclaimerManager:
    """
    Автоматичні дисклеймери для відповідей
    Додає попередження якщо питання стосується здоров'я, права чи фінансів
    """
    
    HEALTH_KEYWORDS = ['біль', 'травма', 'втома', 'хвороба', 'лікар', 'медицин', 'болить', 'операція']
    LEGAL_KEYWORDS = ['контракт', 'договір', 'права', 'закон', 'юрист', 'судов', 'позов']
    FINANCIAL_KEYWORDS = ['гроші', 'оплата', 'ціна', 'кредит', 'позика', 'інвестиц', 'податк']
    
    @staticmethod
    def add_disclaimer(query: str, response: str) -> str:
        """Додати дисклеймер якщо потрібно"""
        query_lower = query.lower()
        
        # Перевірка на здоров'я/медицину
        if any(word in query_lower for word in DisclaimerManager.HEALTH_KEYWORDS):
            response += "\n\n⚠️ **Важливо:** Це освітня інформація, не медична порада. При болях, травмах чи будь-яких проблемах зі здоров'ям - обов'язково до лікаря!"
        
        # Перевірка на юридичні питання
        elif any(word in query_lower for word in DisclaimerManager.LEGAL_KEYWORDS):
            response += "\n\n⚠️ **Важливо:** Юридичні питання індивідуальні. Для офіційних консультацій зверніться до спортивного юриста."
        
        # Перевірка на фінансові питання
        elif any(word in query_lower for word in DisclaimerManager.FINANCIAL_KEYWORDS):
            response += "\n\n⚠️ **Важливо:** Фінансові рішення індивідуальні. Консультуйтесь з фінансовим радником."
        
        return response


class LLMClientInterface:
    """Базовий інтерфейс для LLM клієнтів"""
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAIClient(LLMClientInterface):
    """
    OpenAI API клієнт
    """
    
    def __init__(self, api_key: str, model: str = 'gpt-3.5-turbo'):
        self.api_key = api_key
        self.model = model
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """Генерація відповіді через OpenAI API"""
        if not self.api_key:
            return {
                'response': 'OpenAI API ключ не налаштований. Зверніться до адміністратора.',
                'tokens_used': 0
            }
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ти - професійний AI помічник Play Vision для футбольних фахівців."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                'response': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens
            }
            
        except ImportError:
            return {
                'response': 'OpenAI бібліотека не встановлена. Встановіть: pip install openai',
                'tokens_used': 0
            }
        except Exception as e:
            return {
                'response': f'Помилка OpenAI API: {str(e)}',
                'tokens_used': 0
            }


class AnthropicClient(LLMClientInterface):
    """
    Anthropic Claude API клієнт
    """
    
    def __init__(self, api_key: str, model: str = 'claude-3-sonnet-20240229'):
        self.api_key = api_key
        self.model = model
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """Генерація відповіді через Anthropic API"""
        if not self.api_key:
            return {
                'response': 'Anthropic API ключ не налаштований. Зверніться до адміністратора.',
                'tokens_used': 0
            }
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                'response': response.content[0].text,
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens
            }
            
        except ImportError:
            return {
                'response': 'Anthropic бібліотека не встановлена. Встановіть: pip install anthropic',
                'tokens_used': 0
            }
        except Exception as e:
            return {
                'response': f'Помилка Anthropic API: {str(e)}',
                'tokens_used': 0
            }


class MockLLMClient(LLMClientInterface):
    """
    Mock клієнт для тестування без API ключів
    """
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """Генерація mock відповіді"""
        query = prompt.split('Запит користувача:')[-1].strip()
        
        mock_responses = {
            'що таке play vision': 'Play Vision - це освітня платформа для футбольних фахівців, що надає доступ до курсів, івентів та ментор-коучінгу від провідних експертів галузі.',
            'як зареєструватися': 'Для реєстрації натисніть кнопку "Реєстрація" у верхньому правому куті сайту. Ви можете зареєструватися через email або соціальні мережі.',
            'підписка': 'Play Vision пропонує різні плани підписки: місячний, 3-місячний та річний. Підписка дає доступ до всіх курсів та ексклюзивних матеріалів.',
        }
        
        # Простий пошук відповіді
        query_lower = query.lower()
        for key, response in mock_responses.items():
            if key in query_lower:
                return {
                    'response': response + '\n\n💡 Це тестова відповідь. Для повного функціоналу підключіть OpenAI або Anthropic API.',
                    'tokens_used': 50
                }
        
        return {
            'response': 'Дякую за запитання! Це тестовий режим AI помічника. Для отримання детальних відповідей адміністратор має налаштувати API ключ.',
            'tokens_used': 25
        }


class KnowledgeBaseLoader:
    """
    Сервіс для завантаження бази знань з файлів
    """
    
    def load_from_directory(self, directory_path: str) -> int:
        """Завантаження файлів з директорії в базу знань"""
        import os
        loaded_count = 0
        
        for filename in os.listdir(directory_path):
            if filename.endswith(('.md', '.txt')):
                file_path = os.path.join(directory_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Створення запису в базі знань
                    title = filename.replace('.md', '').replace('.txt', '').replace('_', ' ')
                    
                    knowledge_entry, created = KnowledgeBase.objects.get_or_create(
                        title=title,
                        content_type='manual',
                        defaults={
                            'content': content,
                            'access_level': self._determine_access_level(filename),
                            'metadata': {
                                'source_file': filename,
                                'loaded_at': timezone.now().isoformat()
                            },
                            'is_indexed': True
                        }
                    )
                    
                    if created:
                        loaded_count += 1
                        
                except Exception as e:
                    print(f"Помилка завантаження {filename}: {e}")
        
        return loaded_count
    
    def _determine_access_level(self, filename: str) -> str:
        """Визначення рівня доступу на основі імені файла"""
        filename_lower = filename.lower()
        
        if 'public' in filename_lower or 'faq' in filename_lower:
            return 'public'
        elif 'premium' in filename_lower or 'advanced' in filename_lower:
            return 'premium'
        elif 'subscriber' in filename_lower:
            return 'subscriber'
        else:
            return 'registered'
    
    def index_course_content(self, course_id: int) -> bool:
        """Індексування контенту курсу в базу знань"""
        try:
            from apps.content.models import Course
            
            course = Course.objects.get(id=course_id)
            
            # Індексуємо опис курсу
            KnowledgeBase.objects.get_or_create(
                content_type='course',
                content_id=course_id,
                defaults={
                    'title': f"Курс: {course.title}",
                    'content': f"{course.description}\n\nКоротко: {course.short_description}",
                    'access_level': 'subscriber' if course.requires_subscription else 'public',
                    'metadata': {
                        'course_category': course.category.name,
                        'course_tags': list(course.tags.values_list('name', flat=True)),
                        'course_difficulty': course.difficulty,
                        'course_duration': course.duration_minutes
                    },
                    'is_indexed': True
                }
            )
            
            # Індексуємо матеріали курсу
            for material in course.materials.filter(content_type='article'):
                if material.article_content:
                    KnowledgeBase.objects.get_or_create(
                        content_type='lesson',
                        content_id=material.id,
                        defaults={
                            'title': f"Урок: {material.title}",
                            'content': material.article_content[:2000],  # Обмежуємо розмір
                            'access_level': 'subscriber' if course.requires_subscription else 'public',
                            'metadata': {
                                'course_title': course.title,
                                'material_type': material.content_type
                            },
                            'is_indexed': True
                        }
                    )
            
            return True
            
        except Exception as e:
            print(f"Помилка індексування курсу {course_id}: {e}")
            return False
