# Data migration to fix experts visibility on about and mentoring pages
# This migration sets show_on_about and show_on_mentoring to True for experts
# that are currently shown on home page

from django.db import migrations


def fix_experts_visibility(apps, schema_editor):
    """Встановити show_on_about та show_on_mentoring для експертів на головній"""
    ExpertCard = apps.get_model('cms', 'ExpertCard')
    for expert in ExpertCard.objects.filter(is_active=True, show_on_home=True):
        expert.show_on_about = True
        expert.show_on_mentoring = True
        # Якщо order_about або order_mentoring = 0, копіюємо з order_home
        if expert.order_about == 0:
            expert.order_about = expert.order_home
        if expert.order_mentoring == 0:
            expert.order_mentoring = expert.order_home
        expert.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0015_update_expertcard_ordering'),
    ]

    operations = [
        migrations.RunPython(fix_experts_visibility),
    ]

