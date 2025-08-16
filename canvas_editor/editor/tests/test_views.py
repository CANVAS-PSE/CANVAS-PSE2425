import io
import os

import h5py
from artist.util import config_dictionary
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from project_management.models import Heliostat, LightSource, Project, Receiver


class EditorViewTest(TestCase):
    """
    Test suite for the EditorView.
    This test suite includes tests for both GET and POST methods of the editor view.
    It ensures that the editor view behaves correctly when accessed and when form data is submitted.

    Methods
    -------
    setUp(self):
        Set up the test environment by creating a user and a project.
    test_get_method(self):
        Test the GET method of the editor view to ensure it returns the correct status code and context data.
    test_post_method(self):
        Test the POST method of the editor view to ensure it handles form submissions correctly, including:
        - Submitting a project with an existing name.
        - Submitting a unique project without a file attached.
        - Submitting a unique project with an HDF5 file attached.
        - Submitting a project with an existing name and an HDF5 file attached.
    """

    def setUp(self):
        # create new user
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        # create new project
        project = Project()
        project.name = "testProject"
        project.description = "This is a test project."
        project.owner = user
        project.save()

    def test_get_method(self):
        self.editor = reverse("editor", kwargs={"project_name": "testProject"})
        response = self.client.get(self.editor)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project_name"], "testProject")

    def test_get_method_logged_out(self):
        self.client.logout()
        self.editor = reverse("editor", kwargs={"project_name": "testProject"})
        response = self.client.get(self.editor)
        self.assertEqual(response.status_code, 302)


class DownloadViewTest(TestCase):
    def setUp(self):
        self.download = reverse("download", kwargs={"project_name": "testProject"})
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        project = Project()
        project.name = "testProject"
        project.description = "This is a test project."
        project.owner = user
        project.save()

        # Add a heliostat to the project
        heliostat = Heliostat()
        heliostat.name = "testHeliostat"
        heliostat.project = project
        heliostat.position_x = 42
        heliostat.save()

        # Add a receiver to the project
        receiver = Receiver()
        receiver.name = "testReceiver"
        receiver.project = project
        receiver.normal_x = 42
        receiver.save()

        # Add a light source to the project
        light_source = LightSource()
        light_source.name = "testLightSource"
        light_source.project = project
        light_source.number_of_rays = 42
        light_source.save()

    def test_download(self):
        response = self.client.get(self.download)

        # assert that response is a file response containing a hdf5 file
        self.assertTrue(response.has_header("Content-Disposition"))
        self.assertIn(
            'attachment; filename="testProject.h5"', response["Content-Disposition"]
        )

        downloaded_hdf5_bytes = b"".join(response.streaming_content)
        downloaded_file_buffer = io.BytesIO(downloaded_hdf5_bytes)

        with h5py.File(downloaded_file_buffer, "r") as hdf5_file:
            # Check if the datasets contain the expected data
            heliostats = hdf5_file.get(config_dictionary.heliostat_key)
            receivers = hdf5_file.get(config_dictionary.target_area_key)
            light_sources = hdf5_file.get(config_dictionary.light_source_key)

            self.assertIsNotNone(heliostats)
            self.assertIsNotNone(light_sources)
            self.assertIsNotNone(light_sources)

            for heliostat in heliostats:
                self.assertEqual(
                    42, heliostats[heliostat][config_dictionary.heliostat_position][0]
                )

            for receiver in receivers:
                self.assertEqual(42, receivers[receiver]["normal_vector"][0])

            for light_source in light_sources:
                self.assertEqual(42, light_sources[light_source]["number_of_rays"][()])

    def test_download_logged_out(self):
        self.client.logout()
        response = self.client.get(self.download)
        self.assertEqual(response.status_code, 302)


class PreviewViewTest(TestCase):
    def setUp(self):
        self.upload = reverse("upload", kwargs={"project_name": "testProject"})
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        project = Project()
        project.name = "testProject"
        project.description = "This is a test project."
        project.owner = user
        project.save()

    def test_upload(self):
        test_file_path = os.path.join(settings.BASE_DIR, "static/img/emptyEditor.png")
        with open(test_file_path, "rb") as hdf5_file:
            data = {
                "preview": hdf5_file,
            }
            self.client.post(self.upload, data=data)
        project = Project.objects.get(name="testProject")
        # As the project has no file attribute assiciated with it when created, checking if it now exits tests the upload functionality
        self.assertIsNotNone(project.preview.file)

    def test_wrong_method(self):
        response = self.client.get(self.upload)
        self.assertEqual(response.status_code, 405)

    def test_upload_logged_out(self):
        self.client.logout()
        response = self.client.get(self.upload)
        self.assertEqual(response.status_code, 302)
