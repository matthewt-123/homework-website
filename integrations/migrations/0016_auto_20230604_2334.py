# Generated by Django 3.2.13 on 2023-06-05 06:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hwapp', '0019_homework_archive'),
        ('integrations', '0015_auto_20230604_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notiondata',
            name='tag',
            field=models.CharField(blank='homework', default='homework', max_length=128, null='homework'),
        ),
 
    ]
