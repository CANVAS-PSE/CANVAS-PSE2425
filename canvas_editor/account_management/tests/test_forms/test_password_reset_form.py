from account_management.forms.password_reset_form import PasswordResetForm
from account_management.models import User
from account_management.tests.test_constants import (
    MISMATCHED_BUT_CORRECT_PASSWORD,
    NO_LOWERCASE_PASSWORD,
    NO_NUMERIC_PASSWORD,
    NO_SPECIAL_CHAR_PASSWORD,
    NO_UPPERCASE_PASSWORD,
    SECURE_PASSWORD,
    TOO_SHORT_PASSWORD,
    UPDATED_PASSWORD,
)


from django.test import TestCase


class PasswordResetFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password=SECURE_PASSWORD,
        )

    def test_password_reset_form_valid_data(self):
        # Test case for valid data submission in PasswordResetForm
        form = PasswordResetForm(
            data={
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": UPDATED_PASSWORD,
            }
        )
        self.assertTrue(form.is_valid())

    def test_password_reset_form_no_data(self):
        # Test case for PasswordResetForm with no data
        form = PasswordResetForm(data={})
        self.assertFalse(form.is_valid())

    def test_password_reset_form_passwords_not_matching(self):
        # Test case for PasswordResetForm where passwords do not match
        form = PasswordResetForm(
            data={
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password_confirmation"],
            ["The passwords you entered do not match. Please try again."],
        )

    def test_password_reset_form_password_too_short(self):
        # Test case for PasswordResetForm where password is too short
        form = PasswordResetForm(
            data={
                "new_password": TOO_SHORT_PASSWORD,
                "password_confirmation": TOO_SHORT_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must be at least 8 characters long."],
        )

    def test_password_reset_form_password_no_uppercase(self):
        # Test case for PasswordResetForm where password has no uppercase letter
        form = PasswordResetForm(
            data={
                "new_password": NO_UPPERCASE_PASSWORD,
                "password_confirmation": NO_UPPERCASE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one uppercase letter."],
        )

    def test_password_reset_form_password_no_lowercase(self):
        # Test case for PasswordResetForm where password has no lowercase letter
        form = PasswordResetForm(
            data={
                "new_password": NO_LOWERCASE_PASSWORD,
                "password_confirmation": NO_LOWERCASE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one lowercase letter."],
        )

    def test_password_reset_form_password_no_number(self):
        # Test case for PasswordResetForm where password has no number
        form = PasswordResetForm(
            data={
                "new_password": NO_NUMERIC_PASSWORD,
                "password_confirmation": NO_NUMERIC_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one digit."],
        )

    def test_password_reset_form_password_no_special_character(self):
        # Test case for PasswordResetForm where password has no special character
        form = PasswordResetForm(
            data={
                "new_password": NO_SPECIAL_CHAR_PASSWORD,
                "password_confirmation": NO_SPECIAL_CHAR_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [
                "Password must contain at least one special character (!@#$%^&*()-_+=<>?/)."
            ],
        )
