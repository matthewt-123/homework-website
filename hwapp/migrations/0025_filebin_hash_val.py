# Generated by Django 4.2.7 on 2023-12-17 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hwapp', '0024_filebin'),
    ]

    operations = [
        migrations.AddField(
            model_name='filebin',
            name='hash_val',
            field=models.CharField(default=0, max_length=128),
            preserve_default=False,
        ),
    ]
