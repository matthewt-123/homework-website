# Generated by Django 3.2.8 on 2022-08-02 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hwapp', '0006_allauth'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
