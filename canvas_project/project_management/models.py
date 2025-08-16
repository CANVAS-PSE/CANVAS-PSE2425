from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    """
    Represents a project in the database, contains all the necessary fields to configure a project
    """

    name = models.CharField(max_length=300)
    description = models.CharField(max_length=500, blank=True, default="")
    last_edited = models.DateTimeField(default=timezone.now)
    last_shared = models.DateTimeField(null=True, blank=True)
    favorite = models.CharField(max_length=5, default="false")
    preview = models.ImageField(
        upload_to="project_previews/",
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")

    class Meta:
        # Make each combination of owner and project name unique
        unique_together = [["name", "owner"]]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not hasattr(self, "settings"):
            Settings.objects.create(project=self)

    def __str__(self) -> str:
        return self.name


class Heliostat(models.Model):
    """
    Represents a Heliostat in the database, contains all the necessary fields to configure a heliostat
    """

    project = models.ForeignKey(
        # related name is needed for accessing the foreign key
        Project,
        related_name="heliostats",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200, blank=True, default="Heliostat")
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    position_z = models.FloatField(default=0)

    aimpoint_x = models.FloatField(default=0)
    aimpoint_y = models.FloatField(default=50)
    aimpoint_z = models.FloatField(default=0)

    # surface config
    number_of_facets = models.IntegerField(default=4)

    # kinematic config
    kinematic_type = models.CharField(max_length=300, default="ideal")

    # actuator config
    def __str__(self) -> str:
        return str(self.project) + " Heliostat " + str(self.pk)


class Receiver(models.Model):
    """
    Represents a receiver in the database, contains all the necessary fields to configure a receiver
    """

    project = models.ForeignKey(
        Project, related_name="receivers", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, blank=True, default="Receiver")
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=50)
    position_z = models.FloatField(default=0)

    normal_x = models.FloatField(default=0)
    normal_y = models.FloatField(default=1)
    normal_z = models.FloatField(default=0)

    rotation_y = models.FloatField(default=0)
    receiver_type = models.CharField(max_length=300, default="planar")

    # optional fields
    curvature_e = models.FloatField(default=0)
    curvature_u = models.FloatField(default=0)

    # normal_vector
    plane_e = models.FloatField(default=8.629666667)
    plane_u = models.FloatField(default=7.0)
    resolution_e = models.IntegerField(default=256)
    resolution_u = models.IntegerField(default=256)

    def __str__(self) -> str:
        return str(self.project) + " Receiver " + str(self.pk)


class Lightsource(models.Model):
    """
    Represents a lightsource in the database, contains all the necessary fields to configure a lightsource
    """

    project = models.ForeignKey(
        Project, related_name="lightsources", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, blank=True, default="Light source")
    number_of_rays = models.IntegerField(default=100)
    lightsource_type = models.CharField(max_length=300, default="sun")
    distribution_type = models.CharField(max_length=300, default="normal")
    mean = models.FloatField(default=0)
    covariance = models.FloatField(default=4.3681e-06)

    def __str__(self) -> str:
        return str(self.project) + " Lightsource " + str(self.pk)


class Settings(models.Model):
    """
    Represents the settings in the database, contains all the necessary fields to configure the settings for a project
    """

    project = models.OneToOneField(
        Project, related_name="settings", on_delete=models.CASCADE
    )

    # Graphic settings
    shadows = models.BooleanField(default=True)
    fog = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.project) + " Settings"
