# Generated by Django 4.2.7 on 2023-12-31 06:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('integrations', '0024_auto_20230813_2321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='googledata',
            name='google_user',
        ),
        migrations.DeleteModel(
            name='GoogleCalendar',
        ),
        migrations.DeleteModel(
            name='GoogleData',
        ),
    ]
