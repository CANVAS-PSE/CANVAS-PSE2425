# Generated by Django 5.1.4 on 2025-01-20 22:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("project_management", "0007_alter_project_favorite_alter_project_preview"),
    ]

    operations = [
        migrations.AddField(
            model_name="lightsource",
            name="name",
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="receiver",
            name="name",
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
