from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("project_management", "0012_merge_20250201_1311"),
    ]

    operations = [
        migrations.AlterField(
            model_name="heliostat",
            name="name",
            field=models.CharField(blank=True, default="Heliostat", max_length=200),
        ),
        migrations.AlterField(
            model_name="lightsource",
            name="name",
            field=models.CharField(blank=True, default="Light source", max_length=200),
        ),
        migrations.AlterField(
            model_name="receiver",
            name="name",
            field=models.CharField(blank=True, default="Receiver", max_length=200),
        ),
        migrations.CreateModel(
            name="SharedProject",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("link", models.CharField(max_length=15)),
                ("time_stamp", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="project_management.project",
                    ),
                ),
            ],
        ),
    ]
