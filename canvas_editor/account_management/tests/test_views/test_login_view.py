from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from account_management.tests.test_views.parameterized_view_test_mixin import (
    ParameterizedViewTestMixin,
)
from canvas.test_constants import SECURE_PASSWORD


class LoginViewTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the login view.

    This test case covers the following scenarios:
    - Accessing the login page via GET request.
    - Redirecting authenticated users from the login page to the projects page.
    - Logging in with valid credentials.
    - Attempting to log in with invalid credentials.
    """

    def setUp(self):
        """
        Set up the test client, user, login URL, and projects URL for each test.

        Creates a test user for login tests.
        """
        self.client = Client()
        self.login_url = reverse("login")
        self.projects_url = reverse("projects")
        self.user = User.objects.create_user(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password=SECURE_PASSWORD,
            username="test@mail.de",
        )

    def test_get(self):
        """
        Test that the login page is accessible via GET request.

        Asserts that the correct template is used for the response.
        """
        self.assert_view_get(self.login_url, "account_management/login.html")

    def test_get_authenticated(self):
        """
        Test that an authenticated user is redirected to the projects page when accessing the login page.

        Asserts that the redirection occurs for authenticated users.
        """
        self.get_authenticated(self.login_url)

    def test_post_valid_data(self):
        """
        Test that a valid user can successfully log in and is redirected to the projects page.

        Asserts that the response is a redirect and the user is authenticated.
        """
        response = self.client.post(
            self.login_url,
            {
                "email": "test@mail.de",
                "password": SECURE_PASSWORD,
            },
        )

        user = User.objects.get(email="test@mail.de")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_post_invalid_data(self):
        """
        Test that an invalid login attempt (wrong email) results in an error message.

        Asserts that the response status code is 200, the login template is used, and an error message is shown.
        """
        response = self.client.post(
            self.login_url,
            {
                "email": "max@mail.de",
                "password": SECURE_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_management/login.html")
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, "This email address is not registered.")
