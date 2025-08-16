from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from autosave_api.serializers import (
    HeliostatSerializer,
    LightSourceSerializer,
    ReceiverSerializer,
)
from project_management.models import (
    Heliostat,
    LightSource,
    Project,
    Receiver,
    Settings,
)


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
        heliostat.position_x = 42
        heliostat.position_y = 42
        heliostat.position_z = 42
        heliostat.aimpoint_x = 42
        heliostat.aimpoint_y = 42
        heliostat.aimpoint_z = 42
        heliostat.number_of_facets = 42
        heliostat.kinematic_type = "test"
        heliostat.save()
        url = reverse(
            "heliostat_detail",
            kwargs={"project_id": self.project.id, "pk": heliostat.id},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, HeliostatSerializer(heliostat).data)

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
        receiver.position_x = 42
        receiver.position_y = 42
        receiver.position_z = 42
        receiver.normal_x = 42
        receiver.normal_y = 42
        receiver.normal_z = 42
        receiver.rotation_y = 42
        receiver.receiver_type = "ideal"
        receiver.curvature_e = 42
        receiver.curvature_u = 42
        receiver.plane_e = 42
        receiver.plane_u = 42
        receiver.resolution_e = 42
        receiver.resolution_u = 42
        receiver.save()
        url = reverse(
            "receiver_detail", kwargs={"project_id": self.project.id, "pk": receiver.id}
        )
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ReceiverSerializer(receiver).data)

    def test_create_light_source(self):
        url = reverse("light_source_list", kwargs={"project_id": self.project.id})
        data = {"name": "New Lightsource"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LightSource.objects.count(), 1)
        self.assertEqual(
            LightSource.objects.get(id=response.data["id"]).project, self.project
        )

    def test_get_light_sources(self):
        LightSource.objects.create(name="Lightsource 1", project=self.project)
        url = reverse("light_source_list", kwargs={"project_id": self.project.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Lightsource 1")

    def test_get_light_source_detail(self):
        light_source = LightSource.objects.create(
            name="Lightsource 1", project=self.project
        )
        light_source.number_of_rays = 42
        light_source.light_source_type = "test"
        light_source.distribution_type = "test"
        light_source.mean = 4.2
        light_source.covariance = 4.2
        light_source.save()

        url = reverse(
            "light_source_detail",
            kwargs={"project_id": self.project.id, "pk": light_source.id},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, LightSourceSerializer(light_source).data)

    def test_update_settings(self):
        settings = Settings.objects.get(project=self.project)
        url = reverse("settings_detail", kwargs={"project_id": self.project.id})
        data = {"shadows": False, "fog": False}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settings.refresh_from_db()
        self.assertEqual(settings.shadows, False)
        self.assertEqual(settings.fog, False)
