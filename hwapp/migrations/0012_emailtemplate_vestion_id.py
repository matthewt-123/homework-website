# Generated by Django 3.2.8 on 2023-01-29 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hwapp', '0011_emailtemplate_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='vestion_id',
            field=models.IntegerField(default=False, max_length=64, null=True),
        ),
    ]
