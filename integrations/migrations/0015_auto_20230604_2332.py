# Generated by Django 3.2.13 on 2023-06-05 06:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hwapp', '0019_homework_archive'),
        ('integrations', '0014_auto_20230112_2313'),
    ]

    operations = [
        migrations.AddField(
            model_name='notiondata',
            name='tag',
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),

    ]
