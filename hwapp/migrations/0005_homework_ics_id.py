# Generated by Django 3.2.8 on 2022-04-22 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hwapp', '0004_homework_notion_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='homework',
            name='ics_id',
            field=models.CharField(blank=True, default=False, max_length=256, null=True),
        ),
    ]
