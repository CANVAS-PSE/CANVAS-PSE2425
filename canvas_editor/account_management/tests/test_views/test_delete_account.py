from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from account_management.tests.test_constants import (
    NO_SPECIAL_CHAR_PASSWORD,
    SECURE_PASSWORD,
)


class DeleteAccountTest(TestCase):
    """
    Tests for the delete account view.

    This test case covers the following scenarios:
    - Sending a GET request to the delete account endpoint.
    - Deleting an account with valid credentials.
    - Attempting to delete an account with invalid credentials.
    - Attempting to delete an account when not authenticated.
    """

    def setUp(self):
        """
        Set up the test client, user, and delete account URL for each test.

        Creates a test user for account deletion tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="test@mail.de",
            email="test@mail.de",
            password=SECURE_PASSWORD,
            first_name="test_first_name",
            last_name="test_last_name",
        )
        self.delete_account_url = reverse("delete_account")

    def test_get(self):
        """
        Test that a GET request to the delete account endpoint returns a 405 status code.

        Asserts that only POST requests are allowed for account deletion.
        """
        self.client.login(username="test@mail.de", password=SECURE_PASSWORD)
        response = self.client.get(self.delete_account_url)

        self.assertEqual(response.status_code, 405)

    def test_post_valid_data(self):
        """
        Test that a valid POST request deletes the user and redirects to the login page.

        Asserts that the user is deleted, session is cleared, and redirection occurs.
        """
        self.client.login(username="test@mail.de", password=SECURE_PASSWORD)
        response = self.client.post(
            self.delete_account_url,
            {"password": SECURE_PASSWORD},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_post_invalid_data(self):
        """
        Test that an incorrect password prevents account deletion.

        Asserts that an error message is shown and the user is not deleted.
        """
        self.client.login(username="test@mail.de", password=SECURE_PASSWORD)
        response = self.client.post(
            self.delete_account_url,
            {"password": NO_SPECIAL_CHAR_PASSWORD},
        )

        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "The password you entered is incorrect." in str(msg) for msg in messages
            )
        )
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_post_not_authenticated(self):
        """
        Test that an unauthenticated user is redirected to the login page when attempting account deletion.

        Asserts that redirection to the login page occurs.
        """
        response = self.client.post(
            self.delete_account_url,
            {"password": SECURE_PASSWORD},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/delete_account/")
