from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from rest_framework import status
from rest_framework.test import APIClient

from autosave_api.serializers import (
    HeliostatSerializer,
    LightSourceSerializer,
    ReceiverSerializer,
)
from canvas import view_name_dict
from project_management.models import (
    Heliostat,
    LightSource,
    Project,
    Receiver,
    Settings,
)


class APITestCase(TestCase):
    """Contains test cases for the autosave api for all valid end points and methods."""

    def setUp(self):
        """Set up a test user, log in, and create a test project for use in all tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.project = Project.objects.create(name="Test Project", owner=self.user)

    def test_create_project(self):
        """Test creating a new project via the API."""
        url = reverse(view_name_dict.project_list_view)
        data = {"name": "New Project"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.get(id=response.data["id"]).owner, self.user)

    def test_get_projects(self):
        """Test retrieving the list of projects for the logged-in user."""
        url = reverse(view_name_dict.project_list_view)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.project.name)

    def test_get_project_detail(self):
        """Test retrieving the details of a specific project."""
        url = reverse(
            view_name_dict.project_detail_list_view, kwargs={"pk": self.project.id}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.project.name)

    def test_get_heliostat_detail(self):
        """Test retrieving the details of a specific heliostat."""
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
            view_name_dict.heliostat_detail_view,
            kwargs={"project_id": self.project.id, "pk": heliostat.id},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, HeliostatSerializer(heliostat).data)

    def test_get_receiver_detail(self):
        """Test retrieving the details of a specific receiver."""
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
            view_name_dict.receiver_detail_view,
            kwargs={"project_id": self.project.id, "pk": receiver.id},
        )
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ReceiverSerializer(receiver).data)

    def test_get_lightsource_detail(self):
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
            view_name_dict.light_source_detail_view,
            kwargs={"project_id": self.project.id, "pk": light_source.id},
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, LightSourceSerializer(light_source).data)

    def test_update_settings(self):
        """Test updating the settings for a project."""
        settings = Settings.objects.get(project=self.project)
        url = reverse(
            view_name_dict.settings_detail_view, kwargs={"project_id": self.project.id}
        )
        data = {"shadows": False, "fog": False}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settings.refresh_from_db()
        self.assertEqual(settings.shadows, False)
        self.assertEqual(settings.fog, False)

    def create_object(self, url_list_name, data_name, model_class):
        """Create an object (heliostat, receiver, or light source) for a project."""
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
            (view_name_dict.heliostat_list_view, "New Heliostat", Heliostat),
            (view_name_dict.receiver_list_view, "New Receiver", Receiver),
            (view_name_dict.light_source_list_view, "New Light source", LightSource),
        ]
    )
    def test_create_object(self, url_list_name, data_name, model_class):
        """Parameterized test for creating heliostat, receiver, or light source objects."""
        self.create_object(url_list_name, data_name, model_class)

    def get_objects(self, model_class, model_name, url_list_name):
        """Retrieve a list of objects (heliostats, receivers, or light sources) for a project."""
        model_class.objects.create(name=model_name, project=self.project)
        url = reverse(url_list_name, kwargs={"project_id": self.project.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], model_name)

    @parameterized.expand(
        [
            (Heliostat, "Heliostat 1", view_name_dict.heliostat_list_view),
            (Receiver, "Receiver 1", view_name_dict.receiver_list_view),
            (LightSource, "Light source 1", view_name_dict.light_source_list_view),
        ]
    )
    def test_get_objects(self, model_class, model_name, url_list_name):
        """Parameterized test for retrieving lists of heliostats, receivers, or light sources."""
        self.get_objects(model_class, model_name, url_list_name)
