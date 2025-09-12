from django.test import TestCase

from account_management.forms.login_form import LoginForm
from account_management.models import User
from account_management.tests.test_constants import (
    NO_SPECIAL_CHAR_PASSWORD,
    SECURE_PASSWORD,
)
from canvas import message_dict


class LoginFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password=SECURE_PASSWORD,
        )

    def test_login_form_valid_data(self):
        # Test case for valid data submission in LoginForm
        form = LoginForm(
            data={
                "email": "test@mail.de",
                "password": SECURE_PASSWORD,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_login_form_no_data(self):
        # Test case for LoginForm with no data
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())

    def test_login_form_wrong_email(self):
        # Test case for LoginForm with not existing email
        form = LoginForm(
            data={
                "email": "test2@mail.de",
                "password": SECURE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            [message_dict.email_not_registered_text],
        )

    def test_login_form_wrong_password(self):
        # Test case for LoginForm with wrong password
        form = LoginForm(
            data={
                "email": "test@mail.de",
                "password": NO_SPECIAL_CHAR_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.incorrect_password_text],
        )
