from django.test import TestCase, Client
from project_management.models import Project
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
import os
from django.conf import settings


# TODO: Test the main editor view
class EditorViewTest(TestCase):
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
        self.assertEqual(response_unique.status_code, 302)
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
            self.assertEqual(response_with_file.status_code, 302)
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


# TODO: Test the download view

# TODO: Test the render view

# TODO: Test the preview view
