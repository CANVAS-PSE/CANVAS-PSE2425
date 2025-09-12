from django.test import TestCase

from account_management.forms.register_form import RegisterForm
from account_management.models import User
from account_management.tests.test_constants import (
    MISMATCHED_BUT_CORRECT_PASSWORD,
    NO_LOWERCASE_PASSWORD,
    NO_NUMERIC_PASSWORD,
    NO_SPECIAL_CHAR_PASSWORD,
    NO_UPPERCASE_PASSWORD,
    SECURE_PASSWORD,
    TOO_SHORT_PASSWORD,
)
from canvas import message_dict


class RegisterFormTest(TestCase):
    def test_register_form_valid_data(self):
        # Test case for valid data submission in RegisterForm
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": SECURE_PASSWORD,
                "password_confirmation": SECURE_PASSWORD,
            }
        )
        self.assertTrue(form.is_valid())

    def test_register_form_no_data(self):
        # Test case for RegisterForm with no data
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())

    def test_register_form_existing_mail(self):
        # Test case for RegisterForm with an already existing email
        User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password=SECURE_PASSWORD,
        )
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": SECURE_PASSWORD,
                "password_confirmation": SECURE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            [message_dict.email_already_in_use_text],
        )

    def test_register_form_passwords_not_matching(self):
        # Test case for RegisterForm where passwords do not match
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": SECURE_PASSWORD,
                "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_match_criterium_text],
        )

    def test_register_form_password_too_short(self):
        # Test case for RegisterForm where password is too short
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": TOO_SHORT_PASSWORD,
                "password_confirmation": TOO_SHORT_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_length_criterium_text],
        )

    def test_register_form_password_no_uppercase(self):
        # Test case for RegisterForm where password has no uppercase letter
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": NO_UPPERCASE_PASSWORD,
                "password_confirmation": NO_UPPERCASE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_uppercase_criterium_text],
        )

    def test_register_form_password_no_lowercase(self):
        # Test case for RegisterForm where password has no lowercase letter
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": NO_LOWERCASE_PASSWORD,
                "password_confirmation": NO_LOWERCASE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_lowercase_criterium_text],
        )

    def test_register_form_password_no_number(self):
        # Test case for RegisterForm where password has no number
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": NO_NUMERIC_PASSWORD,
                "password_confirmation": NO_NUMERIC_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_digit_criterium_text],
        )

    def test_register_form_password_no_special_character(self):
        # Test case for RegisterForm where password has no special character
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": NO_SPECIAL_CHAR_PASSWORD,
                "password_confirmation": NO_SPECIAL_CHAR_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_special_char_criterium_text],
        )
