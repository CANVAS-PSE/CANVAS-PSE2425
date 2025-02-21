from django.test import TestCase
from django.contrib.auth.models import User
from project_management.models import (
    Project,
    Heliostat,
    Receiver,
    Lightsource,
    Settings,
)
from django.utils import timezone
from django.db.utils import IntegrityError


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.project = Project.objects.create(
            name="Test project", description="Test project description", owner=self.user
        )

    def test_project(self):
        project2 = Project.objects.create(name="Test project 2", owner=self.user)

        self.assertTrue(isinstance(self.project, Project))
        self.assertEquals(str(self.project), "Test project")
        self.assertEquals(self.project.description, "Test project description")
        self.assertEquals(project2.description, "")
        self.assertEquals(self.project.owner, self.user)
        self.assertEquals(self.project.favorite, "false")
        self.assertTrue(
            (self.project.last_edited - timezone.now()).total_seconds() <= 3
        )
        self.assertEquals(self.project.last_shared, None)
        self.assertFalse(self.project.preview)
        try:
            Project.objects.create(
                name="Test project",
                description="Test project description",
                owner=self.user,
            )
        except IntegrityError as e:
            duplicateException = e
        self.assertEquals(
            str(duplicateException),
            "UNIQUE constraint failed: project_management_project.name, project_management_project.owner_id",
        )

    def test_heliostat(self):
        heliostat = Heliostat.objects.create(project=self.project)

        self.assertTrue(isinstance(heliostat, Heliostat))
        self.assertEquals(heliostat.project, self.project)
        self.assertEquals(heliostat.name, "Heliostat")
        self.assertEquals(heliostat.position_x, 0)
        self.assertEquals(heliostat.position_y, 0)
        self.assertEquals(heliostat.position_z, 0)
        self.assertEquals(heliostat.aimpoint_x, 0)
        self.assertEquals(heliostat.aimpoint_y, 50)
        self.assertEquals(heliostat.aimpoint_z, 0)
        self.assertEquals(heliostat.number_of_facets, 4)
        self.assertEquals(heliostat.kinematic_type, "ideal")
        self.assertEquals(
            str(heliostat), str(heliostat.project) + " Heliostat " + str(heliostat.pk)
        )

    def test_receiver(self):
        receiver = Receiver.objects.create(project=self.project)

        self.assertTrue(isinstance(receiver, Receiver))
        self.assertEquals(receiver.name, "Receiver")
        self.assertEquals(receiver.position_x, 0)
        self.assertEquals(receiver.position_y, 50)
        self.assertEquals(receiver.position_z, 0)
        self.assertEquals(receiver.normal_x, 0)
        self.assertEquals(receiver.normal_y, 1)
        self.assertEquals(receiver.normal_z, 0)
        self.assertEquals(receiver.rotation_y, 0)
        self.assertEquals(receiver.receiver_type, "planar")
        self.assertEquals(receiver.curvature_e, 0)
        self.assertEquals(receiver.curvature_u, 0)
        self.assertEquals(receiver.plane_e, 8.629666667)
        self.assertEquals(receiver.plane_u, 7.0)
        self.assertEquals(receiver.resolution_e, 256)
        self.assertEquals(receiver.resolution_u, 256)
        self.assertEquals(
            str(receiver), str(receiver.project) + " Receiver " + str(receiver.pk)
        )

    def test_lightsource(self):
        lightsource = Lightsource.objects.create(project=self.project)

        self.assertTrue(isinstance(lightsource, Lightsource))
        self.assertEquals(lightsource.name, "Light source")
        self.assertEquals(lightsource.number_of_rays, 100)
        self.assertEquals(lightsource.lightsource_type, "sun")
        self.assertEquals(lightsource.distribution_type, "normal")
        self.assertEquals(lightsource.mean, 0)
        self.assertEquals(lightsource.covariance, 4.3681e-06)
        self.assertEquals(
            str(lightsource),
            str(lightsource.project) + " Lightsource " + str(lightsource.pk),
        )

    def test_settings(self):
        settings = self.project.settings

        self.assertTrue(isinstance(settings, Settings))
        self.assertTrue(settings.shadows)
        self.assertTrue(settings.fog)
        self.assertEquals(str(settings), str(settings.project) + " Settings")
