from django.core.management.base import BaseCommand
from apps.subscriptions.models import Plan


class Command(BaseCommand):
    help = 'Створити 4 тарифи підписки з кольорами та слоганами (C/B/A/PRO-VISION)'

    def handle(self, *args, **options):
        self.stdout.write('Створюємо тарифні плани...\n')
        
        plans_data = [
            {
                'name': 'C-VISION',
                'tier_name': 'c_vision',
                'tier_slogan': 'Знайди свій PRO-VISION',
                'color_indicator': '#3b82f6',  # Синій
                'duration': 'monthly',
                'price': 299.00,
                'features': [
                    'Базовий контент: до 50 годин навчальних матеріалів',
                    'Вибірка матеріалів для початківців',
                    'Підтримка команди',
                    'Електронний сертифікат про проходження курсів',
                    'Доступ до спільноти',
                ],
                'description': 'Початковий рівень для знайомства з платформою',
                'order': 1,
                'is_active': True,
            },
            {
                'name': 'B-VISION',
                'tier_name': 'b_vision',
                'tier_slogan': 'Розвивай свій PRO-VISION',
                'color_indicator': '#f97316',  # Помаранчевий
                'duration': 'monthly',
                'price': 599.00,
                'features': [
                    'Все з C-VISION',
                    'Повний доступ до базових курсів',
                    'Пріоритетна підтримка',
                    'Знижка 5% на покупки',
                    'Ексклюзивні матеріали щомісяця',
                    'Раніше оголошення про події',
                ],
                'description': 'Покращений план для активного навчання',
                'order': 2,
                'is_active': True,
            },
            {
                'name': 'A-VISION',
                'tier_name': 'a_vision',
                'tier_slogan': 'Вдосконали свій PRO-VISION',
                'color_indicator': '#e11d48',  # Червоний
                'duration': 'monthly',
                'price': 999.00,
                'features': [
                    'Все з B-VISION',
                    'Доступ до всіх курсів та матеріалів',
                    'Матеріали преміум рівня + ексклюзив',
                    'Знижка 10% на всі покупки',
                    'Доступ до закритих вебінарів',
                    'Пріоритетна реєстрація на івенти',
                    'Персональні консультації 1 раз на місяць',
                ],
                'description': 'Професійний рівень для серйозних фахівців',
                'order': 3,
                'is_active': True,
            },
            {
                'name': 'PRO-VISION',
                'tier_name': 'pro_vision',
                'tier_slogan': 'Ти є PRO-VISION',
                'color_indicator': '#ec4899',  # Рожевий
                'duration': 'monthly',
                'price': 1499.00,
                'features': [
                    'Все з A-VISION',
                    'Безлімітний доступ до всієї платформи',
                    'Знижка 15% на всі покупки',
                    'Баланс квитків на івенти (3 квитки/місяць)',
                    'Персональний ментор-коуч',
                    'Індивідуальна траєкторія розвитку',
                    'Доступ до закритої спільноти PRO',
                    'Можливість створювати власний контент',
                ],
                'description': 'Максимальний рівень для еліти',
                'order': 4,
                'is_active': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for data in plans_data:
            # Створюємо features як JSON
            features_json = data.pop('features')
            
            plan, created = Plan.objects.update_or_create(
                tier_name=data['tier_name'],
                defaults={**data, 'features': features_json}
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Створено план: {data["name"]}'))
            else:
                updated_count += 1
                self.stdout.write(f'  Оновлено план: {data["name"]}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Готово! Створено: {created_count}, Оновлено: {updated_count}'))
        self.stdout.write('')
        self.stdout.write('💡 Перевірте плани в Django Admin:')
        self.stdout.write('   http://localhost:8000/admin/subscriptions/plan/')

