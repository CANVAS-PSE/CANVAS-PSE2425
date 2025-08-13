from django.test import TestCase, Client
from django.contrib.auth.models import User
from project_management.models import (
    Project,
    Heliostat,
    Receiver,
    Lightsource,
)
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
import pathlib
from django.utils.http import urlsafe_base64_encode


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.project = Project.objects.create(
            name="Test_project", description="Test project description", owner=self.user
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
            "sharedProjects",
            args=[
                urlsafe_base64_encode(str(self.user.pk).encode()),
                urlsafe_base64_encode(str(self.project.name).encode()),
            ],
        )

    def test_project_GET(self):
        response = self.client.get(self.projects_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_management/projects.html")

    def test_projects_GET_logged_out(self):
        self.client.logout()

        response = self.client.get(self.projects_url)

        self.assertEqual(response.status_code, 302)

    def test_projects_POST_no_file(self):
        response = self.client.post(
            self.projects_url,
            {
                "name": "Test project 2",
                "description": "Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.last().name, "Test_project_2")
        self.assertEqual(Project.objects.last().description, "Test project description")
        self.assertEqual(Project.objects.last().owner, self.user)

    def test_projects_POST_no_file_name_duplicate(self):
        response = self.client.post(
            self.projects_url,
            {
                "name": "Test project",
                "description": "Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.last().name, "Test_project")
        self.assertEqual(Project.objects.last().description, "Test project description")
        self.assertEqual(Project.objects.last().owner, self.user)

    def test_projects_POST_with_file(self):
        file_path = (
            pathlib.Path(settings.BASE_DIR)
            / "hdf5_management/testScenarios/testScenario.h5"
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

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.last().name, "Test_project_2")
        self.assertEqual(Project.objects.last().description, "Test project description")
        self.assertEqual(Project.objects.last().owner, self.user)

    def test_projects_POST_with_file_name_duplicate(self):
        file_path = (
            pathlib.Path(settings.BASE_DIR)
            / "hdf5_management/testScenarios/testScenario.h5"
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 1)
        self.assertTemplateUsed(response, "project_management/projects.html")

    def test_projects_POST_with_file_space_in_name(self):
        file_path = (
            pathlib.Path(settings.BASE_DIR)
            / "hdf5_management/testScenarios/testScenario.h5"
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

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.last().name, "Test_project_2")
        self.assertEqual(Project.objects.last().description, "Test project description")
        self.assertEqual(Project.objects.last().owner, self.user)
        self.assertEqual(
            Project.objects.last().heliostats.count(), 3
        )  # Number of heliostats in the testScenario.h5 file
        self.assertEqual(
            Project.objects.last().heliostats.all()[0].position_x, -3
        )  # Position x of heliostat 0 in the testScenario.h5 file
        self.assertEqual(
            Project.objects.last().heliostats.all()[0].aimpoint_y, 70
        )  # Aimpoint y of heliostat 0 in the testScenario.h5 file
        self.assertEqual(
            Project.objects.last().receivers.count(), 1
        )  # Number of receivers in the testScenario.h5 file
        self.assertEqual(
            Project.objects.last().receivers.all()[0].position_y, 70
        )  # Position y of receiver 0 in the testScenario.h5 file
        self.assertEqual(
            Project.objects.last().lightsources.count(), 1
        )  # Number of receivers in the testScenario.h5 file

    def test_projects_POST_no_data(self):
        response = self.client.post(self.projects_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 1)

    def test_update_project_POST_name_description_changed(self):
        response = self.client.post(
            self.update_project_url,
            {
                "name": "Updated Test project",
                "description": "Updated Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.first().name, "Updated_Test_project")
        self.assertEqual(
            Project.objects.first().description, "Updated Test project description"
        )
        self.assertEqual(Project.objects.count(), 1)

    def test_update_project_POST_name_description_changed_description_is_empty(self):
        response = self.client.post(
            self.update_project_url,
            {
                "name": "Updated Test project",
                "owner": self.user.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.first().name, "Updated_Test_project")
        self.assertEqual(Project.objects.first().description, "")
        self.assertEqual(Project.objects.count(), 1)

    def test_update_project_POST_name_not_changed(self):
        response = self.client.post(
            self.update_project_url,
            {
                "name": "Test project",
                "description": "Updated Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.first().name, "Test_project")
        self.assertEqual(
            Project.objects.first().description, "Updated Test project description"
        )
        self.assertEqual(Project.objects.count(), 1)

    def test_update_project_POST_description_not_changed(self):
        response = self.client.post(
            self.update_project_url,
            {
                "name": "Updated Test project",
                "description": "Test project description",
                "owner": self.user.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.first().name, "Updated_Test_project")
        self.assertEqual(
            Project.objects.first().description, "Test project description"
        )
        self.assertEqual(Project.objects.count(), 1)

    def test_update_project_POST_name_duplicate(self):
        Project.objects.create(
            name="Test_project_2",
            description="Test project description",
            owner=self.user,
        )

        response = self.client.post(
            self.update_project_url,
            {
                "name": "Test project 2",
                "owner": self.user.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.last().name, "Test_project_2")
        self.assertEqual(
            Project.objects.first().description, "Test project description"
        )
        self.assertEqual(Project.objects.count(), 2)

    def test_update_project_GET(self):
        response = self.client.get(self.update_project_url)

        self.assertEqual(response.status_code, 405)

    def test_delete_project_POST(self):
        response = self.client.post(self.delete_project_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 0)

    def test_favor_project_POST(self):
        response = self.client.post(self.favor_project_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.last().favorite, "true")

    def test_defavor_project_POST(self):
        response = self.client.post(self.defavor_project_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.last().favorite, "false")

    def test_duplicate_project_POST(self):
        response = self.client.post(self.duplicate_project_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.last().name, self.project.name + "_copy")
        self.assertEqual(Project.objects.last().description, self.project.description)
        self.assertNotEqual(Project.objects.last().pk, self.project.pk)
        self.assertEqual(
            Project.objects.last().heliostats.count(), self.project.heliostats.count()
        )
        self.assertEqual(
            Project.objects.last().heliostats.all()[0].project, Project.objects.last()
        )
        self.assertEqual(
            Project.objects.last().heliostats.all()[0].position_x,
            self.project.heliostats.all()[0].position_x,
        )
        self.assertEqual(
            Project.objects.last().heliostats.all()[0].kinematic_type,
            self.project.heliostats.all()[0].kinematic_type,
        )
        self.assertEqual(
            Project.objects.last().receivers.count(), self.project.receivers.count()
        )
        self.assertEqual(
            Project.objects.last().receivers.all()[0].project, Project.objects.last()
        )
        self.assertEqual(
            Project.objects.last().lightsources.count(),
            self.project.lightsources.count(),
        )
        self.assertEqual(
            Project.objects.last().lightsources.all()[0].project,
            Project.objects.last(),
        )

    def test_shareProject_POST(self):
        response = self.client.post(self.share_project_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            (
                Project.objects.get(owner=self.user, name=self.project.name).last_shared
                - timezone.now()
            ).total_seconds()
            <= 3
        )

    def test_sharedProjects_GET(self):
        self.client.post(self.share_project_url)
        response = self.client.get(self.shared_projects_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_management/sharedProject.html")

    def test_sharedProjects_wrong_values(self):
        response = self.client.get(
            reverse(
                "sharedProjects",
                args=["2", "name"],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_sharedProjects_not_shared(self):
        response = self.client.get(self.shared_projects_url)

        self.assertEqual(response.status_code, 404)

    def test_sharedProjects_POST(self):
        self.client.post(self.share_project_url)
        response = self.client.post(self.shared_projects_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.last().name, self.project.name + "_shared")
        self.assertEqual(Project.objects.last().description, self.project.description)
        self.assertNotEqual(Project.objects.last().pk, self.project.pk)
        self.assertEqual(
            Project.objects.last().heliostats.count(), self.project.heliostats.count()
        )
        self.assertEqual(
            Project.objects.last().heliostats.all()[0].project, Project.objects.last()
        )
        self.assertEqual(
            Project.objects.last().heliostats.all()[0].position_x,
            self.project.heliostats.all()[0].position_x,
        )
        self.assertEqual(
            Project.objects.last().heliostats.all()[0].kinematic_type,
            self.project.heliostats.all()[0].kinematic_type,
        )
        self.assertEqual(
            Project.objects.last().receivers.count(), self.project.receivers.count()
        )
        self.assertEqual(
            Project.objects.last().receivers.all()[0].project, Project.objects.last()
        )
        self.assertEqual(
            Project.objects.last().lightsources.count(),
            self.project.lightsources.count(),
        )
        self.assertEqual(
            Project.objects.last().lightsources.all()[0].project,
            Project.objects.last(),
        )
