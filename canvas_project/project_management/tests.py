from django.test import TestCase, Client
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
from django.urls import reverse
from django.conf import settings
import pathlib


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


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.project = Project.objects.create(
            name="Test project", description="Test project description", owner=self.user
        )
        Heliostat.objects.create(project=self.project)
        Receiver.objects.create(project=self.project)
        Lightsource.objects.create(project=self.project)
        self.client.login(username="testuser", password="testpassword")

        # urls
        self.projects_url = reverse("projects")
        self.update_project_url = reverse("updateProject", args=[self.project.name])
        self.delete_project_url = reverse("deleteProject", args=[self.project.name])
        self.favor_project_url = reverse("favorProject", args=[self.project.name])
        self.defavor_project_url = reverse("defavorProject", args=[self.project.name])
        self.duplicate_project_url = reverse(
            "duplicateProject", args=[self.project.name]
        )
        self.share_project_url = reverse("shareProject", args=[self.project.name])
        self.shared_projects_url = reverse(
            "sharedProjects", args=[self.user.pk, self.project.name]
        )

    def test_project_GET(self):
        response = self.client.get(self.projects_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "project_management/projects.html")

    def test_projects_GET_logged_out(self):
        self.client.logout()

        response = self.client.get(self.projects_url)

        self.assertEquals(response.status_code, 302)

    def test_projects_POST_no_file(self):
        response = self.client.post(
            self.projects_url,
            {
                "name": "Test project 2",
                "description": "Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.count(), 2)
        self.assertEquals(Project.objects.last().name, "Test project 2")
        self.assertEquals(
            Project.objects.last().description, "Test project description"
        )
        self.assertEquals(Project.objects.last().owner, self.user)

    def test_projects_POST_no_file_name_duplicate(self):
        response = self.client.post(
            self.projects_url,
            {
                "name": "Test project",
                "description": "Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(Project.objects.count(), 1)
        self.assertEquals(Project.objects.last().name, "Test project")
        self.assertEquals(
            Project.objects.last().description, "Test project description"
        )
        self.assertEquals(Project.objects.last().owner, self.user)

    def test_projects_POST_with_file(self):
        file_path = (
            pathlib.Path(settings.BASE_DIR)
            / "hdfCreation/testScenarios/testScenario.h5"
        )
        with open(file_path, "rb") as file:
            response = self.client.post(
                self.projects_url,
                {
                    "name": "Test project 2",
                    "description": "Test project description",
                    "owner": self.user.id,
                    "file": file,
                },
            )

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.count(), 2)
        self.assertEquals(Project.objects.last().name, "Test project 2")
        self.assertEquals(
            Project.objects.last().description, "Test project description"
        )
        self.assertEquals(Project.objects.last().owner, self.user)

    def test_projects_POST_with_file_name_duplicate(self):
        file_path = (
            pathlib.Path(settings.BASE_DIR)
            / "hdfCreation/testScenarios/testScenario.h5"
        )
        with open(file_path, "rb") as file:
            response = self.client.post(
                self.projects_url,
                {
                    "name": "Test project",
                    "description": "Test project description",
                    "owner": self.user.id,
                    "file": file,
                },
            )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(Project.objects.count(), 1)
        self.assertTemplateUsed(response, "project_management/projects.html")

    def test_projects_POST_with_file_space_in_name(self):
        file_path = (
            pathlib.Path(settings.BASE_DIR)
            / "hdfCreation/testScenarios/testScenario.h5"
        )
        with open(file_path, "rb") as file:
            response = self.client.post(
                self.projects_url,
                {
                    "name": " Test project 2 ",
                    "description": " Test project description ",
                    "owner": self.user.id,
                    "file": file,
                },
            )

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.count(), 2)
        self.assertEquals(Project.objects.last().name, "Test project 2")
        self.assertEquals(
            Project.objects.last().description, "Test project description"
        )
        self.assertEquals(Project.objects.last().owner, self.user)
        self.assertEquals(
            Project.objects.last().heliostats.count(), 3
        )  # Number of heliostats in the testScenario.h5 file
        self.assertEquals(
            Project.objects.last().heliostats.all()[0].position_x, -3
        )  # Position x of heliostat 0 in the testScenario.h5 file
        self.assertEquals(
            Project.objects.last().heliostats.all()[0].aimpoint_y, 70
        )  # Aimpoint y of heliostat 0 in the testScenario.h5 file
        self.assertEquals(
            Project.objects.last().receivers.count(), 1
        )  # Number of receivers in the testScenario.h5 file
        self.assertEquals(
            Project.objects.last().receivers.all()[0].position_y, 70
        )  # Position y of receiver 0 in the testScenario.h5 file
        self.assertEquals(
            Project.objects.last().lightsources.count(), 1
        )  # Number of receivers in the testScenario.h5 file

    def test_projects_POST_no_data(self):
        response = self.client.post(self.projects_url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(Project.objects.count(), 1)

    def test_update_project_POST_name_description_changed(self):
        response = self.client.post(
            self.update_project_url,
            {
                "name": "Updated Test project",
                "description": "Updated Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.first().name, "Updated Test project")
        self.assertEquals(
            Project.objects.first().description, "Updated Test project description"
        )
        self.assertEquals(Project.objects.count(), 1)

    def test_update_project_POST_name_not_changed(self):
        response = self.client.post(
            self.update_project_url,
            {
                "name": "Test project",
                "description": "Updated Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.first().name, "Test project")
        self.assertEquals(
            Project.objects.first().description, "Updated Test project description"
        )
        self.assertEquals(Project.objects.count(), 1)

    def test_update_project_POST_description_not_changed(self):
        response = self.client.post(
            self.update_project_url,
            {
                "name": "Updated Test project",
                "owner": self.user.id,
            },
        )

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.first().name, "Updated Test project")
        self.assertEquals(
            Project.objects.first().description, "Test project description"
        )
        self.assertEquals(Project.objects.count(), 1)

    def test_update_project_POST_name_duplicate(self):
        Project.objects.create(
            name="Test project2",
            description="Test project description",
            owner=self.user,
        )

        response = self.client.post(
            self.update_project_url,
            {
                "name": "Test project2",
                "owner": self.user.id,
            },
        )

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.first().name, "Test project")
        self.assertEquals(
            Project.objects.first().description, "Test project description"
        )
        self.assertEquals(Project.objects.count(), 2)

    def test_update_project_GET(self):
        response = self.client.get(self.update_project_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "project_management/projects.html")

    def test_delete_project_DELETE(self):
        response = self.client.delete(self.delete_project_url)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.count(), 0)

    def test_favor_project_POST(self):
        response = self.client.post(self.favor_project_url)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.last().favorite, "true")

    def test_defavor_project_POST(self):
        response = self.client.post(self.defavor_project_url)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.last().favorite, "false")

    def test_duplicate_project_POST(self):
        response = self.client.post(self.duplicate_project_url)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Project.objects.count(), 2)
        self.assertEquals(Project.objects.last().name, self.project.name + "copy")
        self.assertEquals(Project.objects.last().description, self.project.description)
        self.assertNotEquals(Project.objects.last().pk, self.project.pk)
        self.assertEquals(
            Project.objects.last().heliostats.count(), self.project.heliostats.count()
        )
        self.assertEquals(
            Project.objects.last().heliostats.all()[0].project, Project.objects.last()
        )
        self.assertEquals(
            Project.objects.last().heliostats.all()[0].position_x,
            self.project.heliostats.all()[0].position_x,
        )
        self.assertEquals(
            Project.objects.last().heliostats.all()[0].kinematic_type,
            self.project.heliostats.all()[0].kinematic_type,
        )
        self.assertEquals(
            Project.objects.last().receivers.count(), self.project.receivers.count()
        )
        self.assertEquals(
            Project.objects.last().receivers.all()[0].project, Project.objects.last()
        )
        self.assertEquals(
            Project.objects.last().lightsources.count(),
            self.project.lightsources.count(),
        )
        self.assertEquals(
            Project.objects.last().lightsources.all()[0].project,
            Project.objects.last(),
        )

    def test_shareProject_POST(self):
        response = self.client.post(self.share_project_url)
        self.assertEquals(response.status_code, 302)
        print(response)
         self.assertTrue(
            (self.project.last_shared - timezone.now()).total_seconds() <= 3
         )

    def test_sharedProjects_POST(self):
        response = self.client.post(self.shared_projects_url)
        pass

    def test_sharedProjects_GET(self):
        response = self.client.get(self.shared_projects_url)
        pass

    