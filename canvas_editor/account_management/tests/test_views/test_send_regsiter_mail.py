from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.http import urlsafe_base64_encode

from account_management.tests.test_constants import COMPLETELY_WRONG_PASSWORD
from account_management.views.registration_view import RegistrationView


class SendRegisterMailTest(TestCase):
    """
    Tests for the send_register_email method in RegistrationView.

    This test case covers the following scenario:
    - Sending a registration confirmation email and verifying its contents.
    """

    def test_send_register_email(self):
        """
        Test that a registration confirmation email is sent correctly.

        Asserts that:
        - One email is sent.
        - The email subject and recipient are correct.
        - The confirmation URL containing the UID and token is present in the email body.
        """
        # Test if the registration email is sent correctly
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=COMPLETELY_WRONG_PASSWORD,
            first_name="test_first_name",
            last_name="test_last_name",
        )

        factory = RequestFactory()
        request = factory.get("/")

        RegistrationView.send_register_email(user, request)

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert (
            email.subject == "CANVAS: Registration Confirmation"
        )  # Verify email subject
        assert email.to == ["test@example.com"]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"confirm_deletion/{uid}/{token}/"

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body
