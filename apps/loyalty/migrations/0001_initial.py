# Generated migration for loyalty app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoyaltyTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('points_required', models.PositiveIntegerField(help_text='Points needed to reach this tier')),
                ('discount_percentage', models.PositiveIntegerField(default=0, help_text='Discount percentage for this tier')),
                ('color', models.CharField(default='#666666', help_text='Hex color for UI display', max_length=7)),
                ('benefits', models.JSONField(default=list, help_text='List of tier benefits')),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order')),
            ],
            options={
                'verbose_name': 'Loyalty Tier (Legacy)',
                'verbose_name_plural': 'Loyalty Tiers (Legacy)',
                'db_table': 'loyalty_tiers',
                'ordering': ['order', 'points_required'],
            },
        ),
        migrations.CreateModel(
            name='LoyaltyAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveIntegerField(default=0, help_text='Поточний баланс балів')),
                ('lifetime_points', models.PositiveIntegerField(default=0, help_text='Всього балів зароблено за весь час')),
                ('lifetime_spent_points', models.PositiveIntegerField(default=0, help_text='Всього балів витрачено')),
                ('lifetime_purchases', models.DecimalField(decimal_places=2, default=0, help_text='Всього витрачено грошей', max_digits=10)),
                ('tier_achieved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_tier', models.ForeignKey(blank=True, help_text='Legacy tier (для зворотної сумісності)', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='loyalty.loyaltytier')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='loyalty_account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Loyalty Account',
                'verbose_name_plural': 'Loyalty Accounts',
                'db_table': 'loyalty_accounts',
            },
        ),
        migrations.CreateModel(
            name='PointEarningRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_type', models.CharField(choices=[('purchase', 'За покупку'), ('subscription', 'За підписку')], max_length=20)),
                ('subscription_tier', models.CharField(choices=[('none', 'Без підписки'), ('c_vision', 'C-Vision'), ('b_vision', 'B-Vision'), ('a_vision', 'A-Vision'), ('pro_vision', 'Pro-Vision')], default='none', help_text='Рівень підписки для розрахунку', max_length=20)),
                ('min_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Мінімальна сума покупки (для правил "За покупку")', max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('max_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Максимальна сума покупки (null = без ліміту)', max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('subscription_duration_months', models.PositiveIntegerField(blank=True, help_text='Термін підписки в місяцях (для правил "За підписку")', null=True)),
                ('points', models.PositiveIntegerField(help_text='Скільки балів нарахувати')),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Порядок застосування')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Point Earning Rule',
                'verbose_name_plural': 'Point Earning Rules',
                'db_table': 'point_earning_rules',
                'ordering': ['order', 'min_amount'],
            },
        ),
        migrations.CreateModel(
            name='RedemptionOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_type', models.CharField(choices=[('discount', 'Знижка'), ('content_access', 'Доступ до контенту'), ('subscription_month', 'Місяць підписки')], max_length=30)),
                ('name', models.CharField(help_text='Назва опції', max_length=100)),
                ('description', models.TextField(blank=True)),
                ('points_required', models.PositiveIntegerField(help_text='Скільки балів потрібно')),
                ('discount_percentage', models.PositiveIntegerField(blank=True, help_text='Відсоток знижки (5, 10)', null=True)),
                ('subscription_tier', models.CharField(blank=True, choices=[('c_vision', 'C-Vision'), ('b_vision', 'B-Vision')], help_text='Рівень підписки (тільки C/B-Vision)', max_length=20)),
                ('requires_subscription', models.BooleanField(default=False, help_text='Чи потрібна активна підписка для використання')),
                ('is_active', models.BooleanField(default=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Redemption Option',
                'verbose_name_plural': 'Redemption Options',
                'db_table': 'redemption_options',
                'ordering': ['display_order', 'points_required'],
            },
        ),
        migrations.CreateModel(
            name='PointTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(help_text='Додатнє - нараховано, від\'ємне - витрачено')),
                ('transaction_type', models.CharField(choices=[('purchase', 'За покупку'), ('subscription', 'За підписку'), ('spent_discount', 'Витрачено на знижку'), ('spent_content', 'Витрачено на контент'), ('spent_subscription_month', 'Обмін на місяць підписки'), ('bonus', 'Бонус'), ('expired', 'Згоріли'), ('adjusted', 'Коригування')], max_length=50)),
                ('reason', models.CharField(help_text='Опис транзакції', max_length=255)),
                ('reference_type', models.CharField(blank=True, help_text='order, subscription, etc.', max_length=50)),
                ('reference_id', models.PositiveIntegerField(blank=True, null=True)),
                ('balance_after', models.PositiveIntegerField(help_text='Баланс після транзакції')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='loyalty.loyaltyaccount')),
            ],
            options={
                'verbose_name': 'Point Transaction',
                'verbose_name_plural': 'Point Transactions',
                'db_table': 'point_transactions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pointtransaction',
            index=models.Index(fields=['account', '-created_at'], name='point_trans_account_idx'),
        ),
        migrations.AddIndex(
            model_name='pointtransaction',
            index=models.Index(fields=['reference_type', 'reference_id'], name='point_trans_reference_idx'),
        ),
    ]

