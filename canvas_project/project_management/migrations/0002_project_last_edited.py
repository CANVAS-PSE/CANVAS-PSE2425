# Generated by Django 4.2.17 on 2025-01-16 14:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('project_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='last_edited',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date edited'),
            preserve_default=False,
        ),
    ]