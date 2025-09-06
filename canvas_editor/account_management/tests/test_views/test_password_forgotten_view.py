from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from account_management.tests.test_constants import SECURE_PASSWORD
from account_management.tests.test_views.parameterized_view_test_mixin import (
    ParameterizedViewTestMixin,
)


class PasswordForgottenViewTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the password forgotten view.

    This test case covers the following scenarios:
    - Accessing the password forgotten page via GET request.
    - Submitting a valid email for password reset and verifying redirection.
    - Submitting an invalid email and verifying error handling.
    """

    def setUp(self):
        """
        Set up the test client, user, and password forgotten URL for each test.

        Creates a test user for password reset tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="test@mail.de",
            email="test@mail.de",
            password=SECURE_PASSWORD,
            first_name="test_first_name",
            last_name="test_last_name",
        )
        self.password_forgotten_url = reverse("password_forgotten")

    def test_get(self):
        """
        Test that the password forgotten page is accessible via GET request.

        Asserts that the correct template is used for the response.
        """
        self.assert_view_get(
            self.password_forgotten_url,
            "account_management/password_forgotten.html",
        )

    def test_post_valid_data(self):
        """
        Test that submitting a valid email for password reset redirects to the login page.

        Asserts that the response is a redirect to the login page.
        """
        response = self.client.post(
            self.password_forgotten_url,
            {"email": "test@mail.de"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_post_invalid_data(self):
        """
        Test that submitting an unregistered email returns an error message and does not send email.

        Asserts that the response status code is 200 and no email is sent.
        """
        response = self.client.post(
            self.password_forgotten_url,
            {"email": "test2@mail.de"},
        )

        self.assertEqual(response.status_code, 200)
        assert len(mail.outbox) == 0
