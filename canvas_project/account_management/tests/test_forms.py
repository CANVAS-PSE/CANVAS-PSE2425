from django.test import TestCase
from account_management.forms import (
    LoginForm,
    RegisterForm,
    UpdateAccountForm,
    DeleteAccountForm,
    PasswordForgottenForm,
    PasswordResetForm,
)
from account_management.models import User


class RegisterFormTest(TestCase):

    def test_register_form_valid_data(self):
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "SecurePassword123!",
                "password_confirmation": "SecurePassword123!",
            }
        )
        self.assertTrue(form.is_valid())

    def test_register_form_no_data(self):
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())

    def test_register_form_existing_mail(self):
        User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password="SecurePassword123!",
        )
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "SecurePassword123!",
                "password_confirmation": "SecurePassword123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            ["This email address is already in use. Please try another."],
        )

    def test_register_form_passwords_not_matching(self):
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "SecurePassword123!",
                "password_confirmation": "SecurePassword123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["The passwords you entered do not match. Please try again."],
        )

    def test_register_form_password_too_short(self):
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "Save-1",
                "password_confirmation": "Save-1",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["Password must be at least 8 characters long."],
        )

    def test_register_form_password_no_uppercase(self):
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "securepassword123!",
                "password_confirmation": "securepassword123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["Password must contain at least one uppercase letter."],
        )

    def test_register_form_password_no_lowercase(self):
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "SECUREPASSWORD123!",
                "password_confirmation": "SECUREPASSWORD123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["Password must contain at least one lowercase letter."],
        )

    def test_register_form_password_no_number(self):
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "SecurePassword!",
                "password_confirmation": "SecurePassword!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["Password must contain at least one digit."],
        )

    def test_register_form_password_no_special_character(self):
        form = RegisterForm(
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "SecurePassword123",
                "password_confirmation": "SecurePassword123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [
                "Password must contain at least one special character (!@#$%^&*()-_+=<>?/)."
            ],
        )
