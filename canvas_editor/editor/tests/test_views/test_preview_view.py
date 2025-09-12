import os

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from canvas import view_name_dict
from project_management.models import Project


class PreviewViewTest(TestCase):
    def setUp(self):
        self.upload = reverse(
            view_name_dict.editor_preview_upload_view,
            kwargs={"project_name": "testProject"},
        )
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
