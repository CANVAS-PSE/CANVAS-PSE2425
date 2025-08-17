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
from autosave_api.serializers import (
    ReceiverSerializer,
    HeliostatSerializer,
    LightsourceSerializer,
)
from django.contrib.auth.models import User
from parameterized import parameterized


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

    def test_get_lightsource_detail(self):
        lightsource = Lightsource.objects.create(
            name="Lightsource 1", project=self.project
        )
        lightsource.number_of_rays = 42
        lightsource.lightsource_type = "test"
        lightsource.distribution_type = "test"
        lightsource.mean = 4.2
        lightsource.covariance = 4.2
        lightsource.save()

        url = reverse(
            "lightsource_detail",
            kwargs={"project_id": self.project.id, "pk": lightsource.id},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, LightsourceSerializer(lightsource).data)

    def test_update_settings(self):
        settings = Settings.objects.get(project=self.project)
        url = reverse("settings_detail", kwargs={"project_id": self.project.id})
        data = {"shadows": False, "fog": False}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settings.refresh_from_db()
        self.assertEqual(settings.shadows, False)
        self.assertEqual(settings.fog, False)

    def create_object(self, url_list_name, data_name, model_class):
        url = reverse(url_list_name, kwargs={"project_id": self.project.id})
        data = {"name": data_name}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(model_class.objects.count(), 1)
        self.assertEqual(
            model_class.objects.get(id=response.data["id"]).project, self.project
        )

    @parameterized.expand(
        [
            ("heliostat_list", "New Heliostat", Heliostat),
            ("receiver_list", "New Receiver", Receiver),
            ("lightsource_list", "New Lightsource", Lightsource),
        ]
    )
    def test_create_object(self, url_list_name, data_name, model_class):
        self.create_object(url_list_name, data_name, model_class)

    def get_objects(self, model_class, model_name, url_list_name):
        model_class.objects.create(name=model_name, project=self.project)
        url = reverse(url_list_name, kwargs={"project_id": self.project.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], model_name)

    @parameterized.expand(
        [
            (Heliostat, "Heliostat 1", "heliostat_list"),
            (Receiver, "Receiver 1", "receiver_list"),
            (Lightsource, "Lightsource 1", "lightsource_list"),
        ]
    )
    def test_get_objects(self, model_class, model_name, url_list_name):
        self.get_objects(model_class, model_name, url_list_name)
