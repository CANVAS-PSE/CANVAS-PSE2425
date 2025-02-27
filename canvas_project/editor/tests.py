from django.test import TestCase, Client
from project_management.models import Project, Heliostat, Receiver, Lightsource
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
import os
from django.conf import settings
import datetime
import h5py


class EditorViewTest(TestCase):
    """
    Test suite for the EditorView.
    This test suite includes tests for both GET and POST methods of the editor view.
    It ensures that the editor view behaves correctly when accessed and when form data is submitted.

    Methods
    --------
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

    def test_post_method(self):
        self.editor = reverse("editor", kwargs={"project_name": "testProject"})

        # Create a project with an already existing name
        form_data = {"name": "testProject", "description": "This is a test project"}

        response = self.client.post(self.editor, data=form_data)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "A project with this name already exists. Please choose a different name.",
        )

        # Create a unique project with no file attached
        form_data_unique = {
            "name": "uniqueProject",
            "description": "This is a unique test project",
        }
        response_unique = self.client.post(self.editor, data=form_data_unique)
        self.assertEqual(
            response_unique.status_code, 302
        )  # tests if the user gets redirected
        self.assertTrue(Project.objects.filter(name="uniqueProject").exists())

        # Create a unique project with a hdf5 file attached
        test_file_path = os.path.join(
            settings.BASE_DIR, "static/testData/TestProject.h5"
        )
        with open(test_file_path, "rb") as hdf5_file:
            form_data_with_file = {
                "name": "uniqueProjectWithFile",
                "description": "This is a unique test project with a file",
                "file": hdf5_file,
            }
            response_with_file = self.client.post(self.editor, data=form_data_with_file)
            self.assertEqual(
                response_with_file.status_code, 302
            )  # tests if the user gets redirected
            self.assertTrue(
                Project.objects.filter(name="uniqueProjectWithFile").exists()
            )

            # Assert that a receiver linked to this project exists
            project_with_file = Project.objects.get(name="uniqueProjectWithFile")
            self.assertIsNotNone(project_with_file.receivers.first())

        # Create a not unique project with a hdf5 file attached
        test_file_path = os.path.join(
            settings.BASE_DIR, "static/testData/TestProject.h5"
        )
        with open(test_file_path, "rb") as hdf5_file:
            form_data_with_file = {
                "name": "uniqueProjectWithFile",
                "description": "This is a unique test project with a file",
                "file": hdf5_file,
            }
            response_with_file = self.client.post(self.editor, data=form_data_with_file)

            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(
                str(messages[0]),
                "A project with this name already exists. Please choose a different name.",
            )


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
        heliostat.aimpoint_x = 42
        heliostat.save()

        # Add a receiver to the project
        receiver = Receiver()
        receiver.name = "testReceiver"
        receiver.project = project
        receiver.normal_x = 42
        receiver.save()

        # Add a light source to the project
        light_source = Lightsource()
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

        test_file_path = os.path.join(
            settings.BASE_DIR, "hdfCreation/scenarios/scenarioFile.h5"
        )
        with h5py.File(test_file_path, "r") as hdf5_file:
            # Check if the datasets contain the expected data
            heliostats = hdf5_file.get("heliostats")
            receivers = hdf5_file.get("target_areas")
            lightsources = hdf5_file.get("lightsources")

            self.assertIsNotNone(heliostats)
            self.assertIsNotNone(lightsources)
            self.assertIsNotNone(lightsources)

            for heliostat in heliostats:
                self.assertEqual(42, heliostats[heliostat]["aim_point"][0])

            for receiver in receivers:
                self.assertEqual(42, receivers[receiver]["normal_vector"][0])

            for lightsource in lightsources:
                self.assertEqual(42, lightsources[lightsource]["number_of_rays"][()])


class RenderViewTest(TestCase):
    def setUp(self):
        self.render = reverse("renderHDF5", kwargs={"project_name": "testProject"})
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        project = Project()
        project.name = "testProject"
        project.description = "This is a test project."
        project.owner = user
        project.save()

    def test_render(self):
        file_path = os.path.join(
            settings.BASE_DIR, "hdfCreation/scenarios/scenarioFile.h5"
        )
        last_modified_time = datetime.datetime.fromtimestamp(
            os.path.getmtime(file_path)
        )

        response = self.client.post(self.render)
        self.assertEqual(response.status_code, 302)

        # check if the file was modified
        new_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        self.assertNotEqual(last_modified_time, new_modified_time)

    def test_wrong_method(self):
        response = self.client.get(self.render)
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
        project = Project.objects.get(name="testProject")

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
        self.assertEqual(response.status_code, 404)
