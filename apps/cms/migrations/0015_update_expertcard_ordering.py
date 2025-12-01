# Generated migration for updating ExpertCard ordering

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0014_add_page_selection_expertcard'),
        ('events', '0014_add_experts_to_event'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expertcard',
            options={
                'db_table': 'cms_expert_cards',
                'verbose_name': 'Спеціаліст',
                'verbose_name_plural': 'Команда (використовується скрізь)',
                'ordering': ['order_home', 'order_about', 'order_mentoring'],
            },
        ),
    ]

