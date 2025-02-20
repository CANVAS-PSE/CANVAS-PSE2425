from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from project_management.models import (
    Project,
    Heliostat,
    Receiver,
    Lightsource,
    Settings,
)
from django.contrib.auth.models import User

# TODO: Update the get detail tests to include all parameters


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.project = Project.objects.create(name="Test Project", owner=self.user)

    def test_create_project(self):
        url = reverse("project_list")
        data = {"name": "New Project"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.get(id=response.data["id"]).owner, self.user)

    def test_get_projects(self):
        url = reverse("project_list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.project.name)

    def test_get_project_detail(self):
        url = reverse("project_detail", kwargs={"pk": self.project.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.project.name)

    def test_create_heliostat(self):
        url = reverse("heliostat_list", kwargs={"project_id": self.project.id})
        data = {"name": "New Heliostat"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Heliostat.objects.count(), 1)
        self.assertEqual(
            Heliostat.objects.get(id=response.data["id"]).project, self.project
        )

    def test_get_heliostats(self):
        Heliostat.objects.create(name="Heliostat 1", project=self.project)
        url = reverse("heliostat_list", kwargs={"project_id": self.project.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Heliostat 1")

    def test_get_heliostat_detail(self):
        heliostat = Heliostat.objects.create(name="Heliostat 1", project=self.project)
        url = reverse(
            "heliostat_detail",
            kwargs={"project_id": self.project.id, "pk": heliostat.id},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], heliostat.name)

    def test_create_receiver(self):
        url = reverse("receiver_list", kwargs={"project_id": self.project.id})
        data = {"name": "New Receiver"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Receiver.objects.count(), 1)
        self.assertEqual(
            Receiver.objects.get(id=response.data["id"]).project, self.project
        )

    def test_get_receivers(self):
        Receiver.objects.create(name="Receiver 1", project=self.project)
        url = reverse("receiver_list", kwargs={"project_id": self.project.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Receiver 1")

    def test_get_receiver_detail(self):
        receiver = Receiver.objects.create(name="Receiver 1", project=self.project)
        url = reverse(
            "receiver_detail", kwargs={"project_id": self.project.id, "pk": receiver.id}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], receiver.name)

    def test_create_lightsource(self):
        url = reverse("lightsource_list", kwargs={"project_id": self.project.id})
        data = {"name": "New Lightsource"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lightsource.objects.count(), 1)
        self.assertEqual(
            Lightsource.objects.get(id=response.data["id"]).project, self.project
        )

    def test_get_lightsources(self):
        Lightsource.objects.create(name="Lightsource 1", project=self.project)
        url = reverse("lightsource_list", kwargs={"project_id": self.project.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Lightsource 1")

    def test_get_lightsource_detail(self):
        lightsource = Lightsource.objects.create(
            name="Lightsource 1", project=self.project
        )
        url = reverse(
            "lightsource_detail",
            kwargs={"project_id": self.project.id, "pk": lightsource.id},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], lightsource.name)

    def test_update_settings(self):
        settings = Settings.objects.get(project=self.project)
        url = reverse("settings_detail", kwargs={"project_id": self.project.id})
        data = {"shadows": False}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settings.refresh_from_db()
        self.assertEqual(settings.shadows, False)
