# Generated by Django 3.2.13 on 2023-07-10 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('external', '0003_helpform_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helpform',
            name='subject',
            field=models.CharField(blank='', default='', max_length=256, null=''),
        ),
    ]
