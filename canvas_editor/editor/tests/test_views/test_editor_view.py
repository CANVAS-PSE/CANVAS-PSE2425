from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from canvas import view_name_dict
from project_management.models import Project


class EditorViewTest(TestCase):
    """Test suite for the EditorView.

    This test suite includes tests for both GET and POST methods of the editor view.
    It ensures that the editor view behaves correctly when accessed and when form data is submitted.

    Methods
    -------
    setUp(self):
        Set up the test environment by creating a user and a project.
    test_get_method(self):
        Test the GET method of the editor view to ensure it returns the correct status code and context data.
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
        self.editor = reverse(
            view_name_dict.editor_view, kwargs={"project_name": "testProject"}
        )
        response = self.client.get(self.editor)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project_name"], "testProject")

    def test_get_method_logged_out(self):
        self.client.logout()
        self.editor = reverse(
            view_name_dict.editor_view, kwargs={"project_name": "testProject"}
        )
        response = self.client.get(self.editor)
        self.assertEqual(response.status_code, 302)
