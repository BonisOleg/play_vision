#!/usr/bin/env python
"""
Скрипт для виправлення подвійних Cloudinary URL в базі даних.
Використання: python fix_cloudinary_urls.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings.production')
django.setup()

from django.db import transaction


def fix_image_field(instance, field_name):
    """Виправити ImageField якщо містить подвійний Cloudinary URL"""
    field = getattr(instance, field_name)
    
    if not field or not field.name:
        return False
    
    original_name = field.name
    
    # Перевірити чи містить подвійний URL
    if 'https:/' in original_name or 'http:/' in original_name or 'res.cloudinary.com' in original_name:
        # Витягти тільки шлях після останнього /upload/
        parts = original_name.split('/upload/')
        if len(parts) > 1:
            correct_path = parts[-1]
            
            # Видалити протокол якщо залишився
            correct_path = correct_path.replace('https:/', '').replace('http:/', '')
            correct_path = correct_path.lstrip('/')
            
            # Оновити поле
            field.name = correct_path
            return True
    
    return False


def fix_cloudinary_urls():
    """Виправити всі подвійні Cloudinary URL в базі"""
    print("🔧 Починаємо виправлення Cloudinary URL...\n")
    
    fixed_count = 0
    models_to_check = []
    
    # HeroSlide
    try:
        from apps.cms.models import HeroSlide
        models_to_check.append(('HeroSlide', HeroSlide, ['image', 'video']))
    except ImportError:
        pass
    
    # ExpertCard
    try:
        from apps.cms.models import ExpertCard
        models_to_check.append(('ExpertCard', ExpertCard, ['photo']))
    except ImportError:
        pass
    
    # Course
    try:
        from apps.content.models import Course
        models_to_check.append(('Course', Course, ['thumbnail', 'logo', 'preview_video']))
    except ImportError:
        pass
    
    # Material
    try:
        from apps.content.models import Material
        models_to_check.append(('Material', Material, ['video_file', 'pdf_file']))
    except ImportError:
        pass
    
    # MonthlyQuote
    try:
        from apps.content.models import MonthlyQuote
        models_to_check.append(('MonthlyQuote', MonthlyQuote, ['expert_photo']))
    except ImportError:
        pass
    
    # Event
    try:
        from apps.events.models import Event
        models_to_check.append(('Event', Event, ['thumbnail', 'banner_image']))
    except ImportError:
        pass
    
    # Speaker
    try:
        from apps.events.models import Speaker
        models_to_check.append(('Speaker', Speaker, ['photo']))
    except ImportError:
        pass
    
    # EventTicket
    try:
        from apps.events.models import EventTicket
        models_to_check.append(('EventTicket', EventTicket, ['qr_code']))
    except ImportError:
        pass
    
    # User
    try:
        from apps.accounts.models import User
        models_to_check.append(('User', User, ['avatar']))
    except ImportError:
        pass
    
    # Обробити всі моделі
    with transaction.atomic():
        for model_name, model_class, fields in models_to_check:
            print(f"📋 Перевіряємо {model_name}...")
            
            for instance in model_class.objects.all():
                instance_fixed = False
                
                for field_name in fields:
                    if hasattr(instance, field_name):
                        if fix_image_field(instance, field_name):
                            if not instance_fixed:
                                print(f"   ✅ Виправлено {model_name} #{instance.pk}")
                                instance_fixed = True
                            print(f"      - {field_name}: {getattr(instance, field_name).name}")
                            fixed_count += 1
                
                if instance_fixed:
                    instance.save()
    
    print(f"\n🎉 Готово! Виправлено {fixed_count} полів з зображеннями.")
    
    # Показати приклад виправленого URL
    print("\n📸 Перевірка виправлених URL:")
    try:
        from apps.cms.models import HeroSlide
        slide = HeroSlide.objects.filter(is_active=True).first()
        if slide and slide.image:
            print(f"   HeroSlide URL: {slide.image.url}")
            print(f"   Шлях в БД: {slide.image.name}")
            
            if 'https:/' in slide.image.url or slide.image.url.count('cloudinary.com') > 1:
                print("   ⚠️ УВАГА: URL все ще містить подвоєння!")
            else:
                print("   ✅ URL правильний!")
    except Exception as e:
        print(f"   Не вдалося перевірити: {e}")


if __name__ == '__main__':
    try:
        fix_cloudinary_urls()
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

