#!/usr/bin/env python3
"""
Скрипт для створення демо даних для тестування кабінету користувача
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Додати шлях до проєкту
sys.path.append('/Users/olegbonislavskyi/Play_Vision')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings')

# Ініціалізувати Django
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.loyalty.models import LoyaltyTier, LoyaltyAccount, PointTransaction
from apps.subscriptions.models import SubscriptionPlan as Plan, Subscription
from apps.content.models import Category, Course, Material, Tag, UserCourseProgress, Favorite
from apps.accounts.models import Profile

User = get_user_model()


def create_loyalty_tiers():
    """Створити рівні лояльності"""
    print("Створення рівнів лояльності...")
    
    tiers_data = [
        {
            'name': 'Bronze',
            'points_required': 0,
            'discount_percentage': 0,
            'color': '#cd7f32',
            'benefits': ['Базовий доступ до контенту'],
            'order': 1
        },
        {
            'name': 'Silver',
            'points_required': 200,
            'discount_percentage': 5,
            'color': '#c0c0c0',
            'benefits': ['5% знижка на матеріали', 'Пріоритетна підтримка'],
            'order': 2
        },
        {
            'name': 'Gold',
            'points_required': 500,
            'discount_percentage': 10,
            'color': '#ffd700',
            'benefits': ['10% знижка на матеріали', 'Ексклюзивні вебінари', 'Персональні рекомендації'],
            'order': 3
        },
        {
            'name': 'Platinum',
            'points_required': 1000,
            'discount_percentage': 15,
            'color': '#e5e4e2',
            'benefits': ['15% знижка на матеріали', 'VIP доступ до івентів', 'Персональний менеджер', 'Ранній доступ до новинок'],
            'order': 4
        }
    ]

    for tier_data in tiers_data:
        tier, created = LoyaltyTier.objects.get_or_create(
            name=tier_data['name'],
            defaults=tier_data
        )
        if created:
            print(f"  ✅ Створено рівень: {tier.name}")
        else:
            print(f"  ⚠️ Рівень вже існує: {tier.name}")


def create_subscription_plans():
    """Створити плани підписок"""
    print("Створення планів підписок...")
    
    plans_data = [
        {
            'name': 'Базовий',
            'slug': 'basic',
            'duration': '1_month',
            'duration_months': 1,
            'price': Decimal('9.99'),
            'features': [
                'Доступ до базових курсів',
                'Мобільний додаток',
                'Email підтримка'
            ],
            'is_popular': False
        },
        {
            'name': 'Стандарт',
            'slug': 'standard',
            'duration': '1_month',
            'duration_months': 1,
            'price': Decimal('19.99'),
            'features': [
                'Доступ до всіх курсів',
                'Офлайн перегляд',
                'Чат підтримка',
                'Сертифікати'
            ],
            'is_popular': True
        },
        {
            'name': 'Преміум',
            'slug': 'premium',
            'duration': '1_month',
            'duration_months': 1,
            'price': Decimal('39.99'),
            'features': [
                'Все з тарифу Стандарт',
                'Персональні консультації',
                'Ексклюзивні вебінари',
                'Пріоритетна підтримка'
            ],
            'is_popular': False
        }
    ]

    for plan_data in plans_data:
        plan, created = Plan.objects.get_or_create(
            slug=plan_data['slug'],
            defaults=plan_data
        )
        if created:
            print(f"  ✅ Створено план: {plan.name}")
        else:
            print(f"  ⚠️ План вже існує: {plan.name}")


def create_content_structure():
    """Створити категорії та теги"""
    print("Створення категорій та тегів...")
    
    # Категорії
    categories_data = [
        {'name': 'Аналітика', 'slug': 'analytics', 'icon': 'chart-bar'},
        {'name': 'Тренерство', 'slug': 'coaching', 'icon': 'users'},
        {'name': 'Психологія', 'slug': 'psychology', 'icon': 'brain'},
        {'name': 'Харчування', 'slug': 'nutrition', 'icon': 'apple-alt'}
    ]

    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            print(f"  ✅ Створено категорію: {category.name}")

    # Теги
    tags_data = [
        'Аналітика', 'Тренерство', 'Психологія', 'Харчування',
        'Статистика', 'Мотивація', 'Стрес', 'Відновлення',
        'Командна робота', 'Лідерство'
    ]

    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': tag_name.lower().replace(' ', '-')}
        )
        if created:
            print(f"  ✅ Створено тег: {tag.name}")


def create_demo_user(email):
    """Створити демо користувача"""
    print(f"Створення демо користувача: {email}")
    
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email,
            'first_name': 'Демо',
            'last_name': 'Користувач',
            'is_email_verified': True
        }
    )
    
    if created:
        user.set_password('demo123456')
        user.save()
        print(f"  ✅ Створено користувача: {user.email}")
        print(f"  🔑 Пароль: demo123456")
    else:
        print(f"  ⚠️ Користувач вже існує: {user.email}")
    
    return user


def setup_user_profile(user):
    """Налаштувати профіль користувача"""
    print("Налаштування профілю користувача...")
    
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            'first_name': 'Олег',
            'last_name': 'Бониславський',
            'birth_date': datetime(1990, 5, 15).date(),
            'profession': 'Аналітик / Тренер',
            'completed_survey': True,
            'survey_completed_at': timezone.now()
        }
    )
    
    if created:
        # Додати інтереси
        tags = Tag.objects.filter(name__in=['Аналітика', 'Тренерство', 'Психологія'])
        profile.interests.set(tags)
        print(f"  ✅ Створено профіль для користувача")


def create_user_subscription(user):
    """Створити активну підписку"""
    print("Створення активної підписки...")
    
    plan = Plan.objects.filter(slug='standard').first()
    if not plan:
        print("  ⚠️ План 'standard' не знайдено")
        return

    subscription, created = Subscription.objects.get_or_create(
        user=user,
        plan=plan,
        status='active',
        defaults={
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=30),
            'auto_renew': True
        }
    )
    
    if created:
        print(f"  ✅ Створено активну підписку: {plan.name}")


def setup_loyalty_account(user):
    """Налаштувати аккаунт лояльності"""
    print("Налаштування аккаунту лояльності...")
    
    try:
        loyalty_account = user.loyalty_account
        created = False
        print(f"  ⚠️ Аккаунт лояльності вже існує")
    except LoyaltyAccount.DoesNotExist:
        silver_tier = LoyaltyTier.objects.filter(name='Silver').first()
        loyalty_account = LoyaltyAccount.objects.create(
            user=user,
            points=250,  # Silver рівень
            lifetime_points=300,
            lifetime_spent=Decimal('89.99'),
            current_tier=silver_tier,
            tier_achieved_at=timezone.now()
        )
        created = True

    if created:
        # Створити історію транзакцій
        transactions_data = [
            {'points': 50, 'reason': 'Заповнення профілю', 'days_ago': 30},
            {'points': 20, 'reason': 'Завершення курсу "Базова аналітика"', 'days_ago': 25},
            {'points': 100, 'reason': 'Покупка підписки', 'days_ago': 20},
            {'points': 30, 'reason': 'Відвідування вебінару', 'days_ago': 15},
            {'points': 25, 'reason': 'Завершення курсу "Психологія спорту"', 'days_ago': 10},
            {'points': 25, 'reason': 'Рефери програма', 'days_ago': 5}
        ]
        
        current_points = 0
        for trans_data in transactions_data:
            current_points += trans_data['points']
            PointTransaction.objects.create(
                account=loyalty_account,
                points=trans_data['points'],
                transaction_type='earned',
                reason=trans_data['reason'],
                balance_after=current_points,
                created_at=timezone.now() - timedelta(days=trans_data['days_ago'])
            )
        
        print(f"  ✅ Налаштовано аккаунт лояльності: {loyalty_account.current_tier.name}")


def create_demo_courses(user):
    """Створити демо курси та матеріали"""
    print("Створення демо курсів...")
    
    # Отримати категорії
    analytics_cat = Category.objects.filter(slug='analytics').first()
    coaching_cat = Category.objects.filter(slug='coaching').first()
    psychology_cat = Category.objects.filter(slug='psychology').first()
    
    if not all([analytics_cat, coaching_cat, psychology_cat]):
        print("  ⚠️ Не всі категорії знайдено")
        return

    courses_data = [
        {
            'title': 'Базова спортивна аналітика',
            'slug': 'basic-sports-analytics',
            'category': analytics_cat,
            'difficulty': 'beginner',
            'duration_minutes': 180,
            'price': Decimal('29.99'),
            'is_published': True,
            'materials': [
                {'title': 'Вступ до аналітики', 'content_type': 'video', 'order': 1},
                {'title': 'Основні метрики', 'content_type': 'pdf', 'order': 2},
                {'title': 'Інструменти аналізу', 'content_type': 'video', 'order': 3},
                {'title': 'Практичні завдання', 'content_type': 'article', 'order': 4}
            ]
        },
        {
            'title': 'Психологія спортсмена',
            'slug': 'athlete-psychology',
            'category': psychology_cat,
            'difficulty': 'intermediate',
            'duration_minutes': 240,
            'price': Decimal('39.99'),
            'is_published': True,
            'materials': [
                {'title': 'Основи спортивної психології', 'content_type': 'video', 'order': 1},
                {'title': 'Робота зі стресом', 'content_type': 'pdf', 'order': 2},
                {'title': 'Мотивація атлетів', 'content_type': 'video', 'order': 3}
            ]
        },
        {
            'title': 'Сучасні методи тренування',
            'slug': 'modern-training-methods',
            'category': coaching_cat,
            'difficulty': 'advanced',
            'duration_minutes': 300,
            'price': Decimal('49.99'),
            'is_published': True,
            'materials': [
                {'title': 'Планування тренувань', 'content_type': 'video', 'order': 1},
                {'title': 'Методики розвитку', 'content_type': 'pdf', 'order': 2}
            ]
        }
    ]

    for course_data in courses_data:
        materials_data = course_data.pop('materials', [])
        
        course, created = Course.objects.get_or_create(
            slug=course_data['slug'],
            defaults={
                **course_data,
                'description': f'Опис курсу: {course_data["title"]}',
                'short_description': f'Короткий опис для {course_data["title"]}',
                'published_at': timezone.now()
            }
        )
        
        if created:
            print(f"  ✅ Створено курс: {course.title}")
            
            # Створити матеріали
            for material_data in materials_data:
                Material.objects.create(
                    course=course,
                    **material_data,
                    slug=material_data['title'].lower().replace(' ', '-'),
                    video_duration_seconds=300 if material_data['content_type'] == 'video' else 0
                )
            
            # Створити прогрес для користувача
            progress = UserCourseProgress.objects.create(
                user=user,
                course=course,
                progress_percentage=75 if course_data['slug'] == 'basic-sports-analytics' else 30
            )
            
            # Позначити деякі матеріали як завершені
            if course_data['slug'] == 'basic-sports-analytics':
                completed_materials = course.materials.all()[:3]
                progress.materials_completed.set(completed_materials)
                progress.update_progress()
            
            # Додати до улюблених
            if course_data['slug'] in ['basic-sports-analytics', 'athlete-psychology']:
                Favorite.objects.create(user=user, course=course)

    print(f"  ✅ Створено демо курси та прогрес")


def main():
    """Головна функція"""
    print("🚀 Створення демо даних для кабінету користувача...")
    print("=" * 50)
    
    email = 'demo@playvision.com'
    
    # 1. Створити рівні лояльності
    create_loyalty_tiers()
    
    # 2. Створити плани підписок
    create_subscription_plans()
    
    # 3. Створити категорії та теги
    create_content_structure()
    
    # 4. Створити демо користувача
    user = create_demo_user(email)
    
    # 5. Налаштувати профіль
    setup_user_profile(user)
    
    # 6. Створити активну підписку
    create_user_subscription(user)
    
    # 7. Створити аккаунт лояльності
    setup_loyalty_account(user)
    
    # 8. Створити демо курси та матеріали
    create_demo_courses(user)
    
    print("=" * 50)
    print("✅ Демо дані успішно створено!")
    print(f"🔗 Email: {email}")
    print("🔑 Пароль: demo123456")
    print("🌐 Увійдіть в аккаунт та перейдіть до /account/")


if __name__ == '__main__':
    main()
