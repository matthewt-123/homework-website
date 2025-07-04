# Generated by Django 3.2.13 on 2023-08-05 01:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hwapp', '0022_auto_20230804_1856'),
        ('integrations', '0021_auto_20230710_1306'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('message', models.TextField(blank=True, default=None, null=True)),
                ('error', models.BooleanField(blank=True, default=False, null=True)),
                ('log_type', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
