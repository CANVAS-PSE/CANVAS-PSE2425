from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from account_management.tests.test_constants import (
    MISMATCHED_BUT_CORRECT_PASSWORD,
    SECURE_PASSWORD,
)
from account_management.tests.test_views.parameterized_view_test_mixin import (
    ParameterizedViewTestMixin,
)
from canvas import message_dict, view_name_dict


class RegisterViewTests(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the register view.

    This test case covers the following scenarios:
    - Accessing the register page via GET request.
    - Redirecting authenticated users from the register page to the projects page.
    - Registering a new user with valid data.
    - Handling invalid registration data (mismatched passwords).
    """

    def setUp(self):
        """
        Set up the test client, user, register URL, projects URL, and valid user data for each test.

        Creates a test user and prepares valid registration data.
        """
        self.client = Client()
        self.register_url = reverse(view_name_dict.register_view)
        self.projects_url = reverse(view_name_dict.projects_view)
        self.user = User.objects.create_user(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password=SECURE_PASSWORD,
            username="test@mail.de",
        )
        self.valid_user_data = {
            "first_name": "test2_first_name",
            "last_name": "test2_last_name",
            "email": "test2@mail.de",
            "password": SECURE_PASSWORD,
            "password_confirmation": SECURE_PASSWORD,
        }

    def test_get(self):
        """
        Test that the register page is accessible via GET request.

        Asserts that the correct template is used for the response.
        """
        self.assert_view_get(self.register_url, "account_management/register.html")

    def test_get_authenticated(self):
        """
        Test that an authenticated user is redirected to the projects page when accessing the register page.

        Asserts that the redirection occurs for authenticated users.
        """
        self.get_authenticated(self.register_url)

    def test_post_valid_data(self):
        """
        Test that a new user can successfully register and is redirected to the projects page.

        Asserts that the user is created, logged in, and redirected.
        """
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
        )
        user = User.objects.get(email="test2@mail.de")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_post_invalid_data(self):
        """
        Test that invalid registration data (mismatched passwords) results in an error message.

        Asserts that the response status code is 200, the register template is used, and an error message is shown.
        """
        response = self.client.post(
            self.register_url,
            {
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": SECURE_PASSWORD,
                "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account_management/register.html")
        self.assertContains(response, message_dict.password_match_criterium_text)
        self.assertTrue(response.context["form"].errors)
