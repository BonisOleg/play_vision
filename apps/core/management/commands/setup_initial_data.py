"""
Management команда для створення початкових даних
Fallback для випадків, коли build.sh не може виконати Python код
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Створює початкові дані: superuser та AI конфігурацію'
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        # Створення superuser
        try:
            if not User.objects.filter(email='admin@playvision.com').exists():
                User.objects.create_superuser(
                    email='admin@playvision.com',
                    username='admin@playvision.com', 
                    password='changeme123'
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ Superuser created: admin@playvision.com')
                )
            else:
                self.stdout.write('👤 Superuser already exists')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Superuser creation error: {e}')
            )
        
        # Створення AI конфігурації
        try:
            from apps.ai.models import AIConfiguration
            if not AIConfiguration.objects.exists():
                AIConfiguration.objects.create(
                    llm_provider='openai',
                    llm_model='gpt-3.5-turbo',
                    is_enabled=True
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ AI Configuration created')
                )
            else:
                self.stdout.write('🤖 AI Configuration already exists')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ AI configuration error: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Initial data setup completed')
        )
