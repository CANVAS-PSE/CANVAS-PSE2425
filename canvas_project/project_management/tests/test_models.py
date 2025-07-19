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
        self.assertEqual(str(self.project), "Test project")
        self.assertEqual(self.project.description, "Test project description")
        self.assertEqual(project2.description, "")
        self.assertEqual(self.project.owner, self.user)
        self.assertEqual(self.project.favorite, "false")
        self.assertTrue(
            (self.project.last_edited - timezone.now()).total_seconds() <= 3
        )
        self.assertEqual(self.project.last_shared, None)
        self.assertFalse(self.project.preview)
        try:
            Project.objects.create(
                name="Test project",
                description="Test project description",
                owner=self.user,
            )
        except IntegrityError as e:
            duplicate_exception = e
        self.assertEqual(
            str(duplicate_exception),
            "UNIQUE constraint failed: project_management_project.name, project_management_project.owner_id",
        )

    def test_heliostat(self):
        heliostat = Heliostat.objects.create(project=self.project)

        self.assertTrue(isinstance(heliostat, Heliostat))
        self.assertEqual(heliostat.project, self.project)
        self.assertEqual(heliostat.name, "Heliostat")
        self.assertEqual(heliostat.position_x, 0)
        self.assertEqual(heliostat.position_y, 0)
        self.assertEqual(heliostat.position_z, 0)
        self.assertEqual(heliostat.aimpoint_x, 0)
        self.assertEqual(heliostat.aimpoint_y, 50)
        self.assertEqual(heliostat.aimpoint_z, 0)
        self.assertEqual(heliostat.number_of_facets, 4)
        self.assertEqual(heliostat.kinematic_type, "ideal")
        self.assertEqual(
            str(heliostat), str(heliostat.project) + " Heliostat " + str(heliostat.pk)
        )

    def test_receiver(self):
        receiver = Receiver.objects.create(project=self.project)

        self.assertTrue(isinstance(receiver, Receiver))
        self.assertEqual(receiver.name, "Receiver")
        self.assertEqual(receiver.position_x, 0)
        self.assertEqual(receiver.position_y, 50)
        self.assertEqual(receiver.position_z, 0)
        self.assertEqual(receiver.normal_x, 0)
        self.assertEqual(receiver.normal_y, 1)
        self.assertEqual(receiver.normal_z, 0)
        self.assertEqual(receiver.rotation_y, 0)
        self.assertEqual(receiver.receiver_type, "planar")
        self.assertEqual(receiver.curvature_e, 0)
        self.assertEqual(receiver.curvature_u, 0)
        self.assertEqual(receiver.plane_e, 8.629666667)
        self.assertEqual(receiver.plane_u, 7.0)
        self.assertEqual(receiver.resolution_e, 256)
        self.assertEqual(receiver.resolution_u, 256)
        self.assertEqual(
            str(receiver), str(receiver.project) + " Receiver " + str(receiver.pk)
        )

    def test_lightsource(self):
        lightsource = Lightsource.objects.create(project=self.project)

        self.assertTrue(isinstance(lightsource, Lightsource))
        self.assertEqual(lightsource.name, "Light source")
        self.assertEqual(lightsource.number_of_rays, 100)
        self.assertEqual(lightsource.lightsource_type, "sun")
        self.assertEqual(lightsource.distribution_type, "normal")
        self.assertEqual(lightsource.mean, 0)
        self.assertEqual(lightsource.covariance, 4.3681e-06)
        self.assertEqual(
            str(lightsource),
            str(lightsource.project) + " Lightsource " + str(lightsource.pk),
        )

    def test_settings(self):
        settings = self.project.settings

        self.assertTrue(isinstance(settings, Settings))
        self.assertTrue(settings.shadows)
        self.assertTrue(settings.fog)
        self.assertEqual(str(settings), str(settings.project) + " Settings")
