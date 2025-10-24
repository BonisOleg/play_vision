from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.events.models import Event


class Command(BaseCommand):
    help = 'Update production events with categories and future dates'

    def handle(self, *args, **options):
        self.stdout.write('Оновлюю події на production...')
        
        now = timezone.now()
        
        # Оновити ФФФ 5
        try:
            event = Event.objects.get(slug='forum-fff-5')
            event.event_category = 'football_experts_forum'
            event.start_datetime = now + timedelta(days=1, hours=18)
            event.end_datetime = now + timedelta(days=1, hours=21)
            event.save()
            self.stdout.write(self.style.SUCCESS(f'✅ {event.title}'))
        except Event.DoesNotExist:
            pass
        
        # Оновити Майстер-клас xG
        try:
            event = Event.objects.get(slug='masterclass-xg')
            event.event_category = 'seminars_hackathons'
            event.start_datetime = now + timedelta(days=2, hours=19)
            event.end_datetime = now + timedelta(days=2, hours=21)
            event.save()
            self.stdout.write(self.style.SUCCESS(f'✅ {event.title}'))
        except Event.DoesNotExist:
            pass
        
        # Оновити Круглий стіл
        try:
            event = Event.objects.get(slug='roundtable-academies')
            event.event_category = 'seminars_hackathons'
            event.start_datetime = now + timedelta(days=3, hours=17)
            event.end_datetime = now + timedelta(days=3, hours=19)
            event.save()
            self.stdout.write(self.style.SUCCESS(f'✅ {event.title}'))
        except Event.DoesNotExist:
            pass
        
        # Оновити Стажування
        try:
            event = Event.objects.get(slug='internship-dynamo')
            event.event_category = 'internships'
            event.start_datetime = now + timedelta(days=5, hours=10)
            event.end_datetime = now + timedelta(days=5, hours=18)
            event.save()
            self.stdout.write(self.style.SUCCESS(f'✅ {event.title}'))
        except Event.DoesNotExist:
            pass
        
        # ФФФ 6
        try:
            event = Event.objects.get(slug='forum-fff-6')
            event.event_category = 'football_experts_forum'
            event.start_datetime = now + timedelta(days=45, hours=10)
            event.end_datetime = now + timedelta(days=45, hours=18)
            event.save()
            self.stdout.write(self.style.SUCCESS(f'✅ {event.title}'))
        except Event.DoesNotExist:
            pass
        
        updated_count = Event.objects.exclude(event_category='').count()
        total_count = Event.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Оновлено {updated_count}/{total_count} подій'))
        self.stdout.write(self.style.SUCCESS('Тепер запустіть create_test_events для додавання нових'))

