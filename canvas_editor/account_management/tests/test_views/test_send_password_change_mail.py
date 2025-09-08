from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.http import urlsafe_base64_encode

from account_management.views.update_account_view import UpdateAccountView
from canvas.test_constants import SECURE_PASSWORD


class SendPasswordChangeMailTest(TestCase):
    """
    Tests for the send_password_change_email method in UpdateAccountView.

    This test case covers the following scenario:
    - Sending a password change email and verifying its contents.
    """

    def test_send_password_change_email(self):
        """
        Test that a password change email is sent correctly.

        Asserts that:
        - One email is sent.
        - The email subject and recipient are correct.
        - The confirmation URL containing the UID and token is present in the email body.
        """
        user = User.objects.create_user(
            username="testuser",
            email="test@mail.de",
            password=SECURE_PASSWORD,
            first_name="test_first_name",
            last_name="test_last_name",
        )

        factory = RequestFactory()
        request = factory.get("/")

        UpdateAccountView.send_password_change_email(user, request)

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert email.subject == "Password Change Confirmation"  # Verify email subject
        assert email.to == ["test@mail.de"]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"password_reset/{uid}/{token}/"

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body
