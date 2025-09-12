from django.test import TestCase

from account_management.forms.password_forgotten_form import PasswordForgottenForm
from account_management.models import User
from account_management.tests.test_constants import SECURE_PASSWORD
from canvas import message_dict


class PasswordForgottenFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password=SECURE_PASSWORD,
        )

    def test_password_forgotten_form_valid_data(self):
        # Test case for valid data submission in PasswordForgottenForm
        form = PasswordForgottenForm(
            data={
                "email": "test@mail.de",
            }
        )
        self.assertTrue(form.is_valid())

    def test_password_forgotten_form_no_data(self):
        # Test case for PasswordForgottenForm with no data
        form = PasswordForgottenForm(data={})
        self.assertFalse(form.is_valid())

    def test_password_forgotten_form_wrong_email(self):
        # Test case for PasswordForgottenForm with not existing email
        form = PasswordForgottenForm(
            data={
                "email": "test2@mail.de",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            [message_dict.email_not_registered_text],
        )
