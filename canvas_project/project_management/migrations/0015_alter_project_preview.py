# Generated by Django 4.2.17 on 2025-02-04 20:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "project_management",
            "0014_alter_heliostat_name_alter_lightsource_name_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="preview",
            field=models.ImageField(upload_to="project_previews/"),
        ),
    ]
