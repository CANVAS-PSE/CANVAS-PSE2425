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


class LoginFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password="SecurePassword123!",
        )

    def test_login_form_valid_data(self):
        form = LoginForm(
            data={
                "email": "test@mail.de",
                "password": "SecurePassword123!",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_login_form_no_data(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())

    def test_login_form_wrong_email(self):
        form = LoginForm(
            data={
                "email": "test2@mail.de",
                "password": "SecurePassword123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            ["This email address is not registered."],
        )

    def test_login_form_wrong_password(self):
        form = LoginForm(
            data={
                "email": "test@mail.de",
                "password": "SecurePassword123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["The password you entered is incorrect."],
        )


class UpdateAccountFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password="SecurePassword123!",
        )

    def test_update_account_form_valid_data(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "new_test@mail.de",
                "old_password": "SecurePassword123!",
                "new_password": "NewSecurePassword123!",
                "password_confirmation": "NewSecurePassword123!",
            },
        )
        self.assertTrue(form.is_valid())

    def test_update_account_form_no_password(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "new_test@mail.de",
            },
        )
        self.assertTrue(form.is_valid())

    def test_update_account_form_existing_mail(self):
        User.objects.create_user(
            username="test2@mail.de",
            first_name="test2_first_name",
            last_name="test2_last_name",
            email="test2@mail.de",
            password="SecurePassword123!",
        )
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test2@mail.de",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            ["This email address is already in use. Please try another."],
        )

    def test_update_account_form_passwords_not_matching(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "old_password": "SecurePassword123!",
                "new_password": "NewSecurePassword123!",
                "password_confirmation": "NewSecurePassword123",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password_confirmation"],
            ["The passwords you entered do not match. Please try again."],
        )

    def test_update_account_form_password_too_short(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": "SecurePassword123!",
                "new_password": "Save-1",
                "password_confirmation": "Save-1",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must be at least 8 characters long."],
        )

    def test_update_account_form_password_no_uppercase(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": "SecurePassword123!",
                "new_password": "securepassword123!",
                "password_confirmation": "securepassword123!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one uppercase letter."],
        )

    def test_update_account_form_password_no_lowercase(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": "SecurePassword123!",
                "new_password": "SECUREPASSWORD123!",
                "password_confirmation": "SECUREPASSWORD123!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one lowercase letter."],
        )

    def test_update_account_form_password_no_number(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": "SecurePassword123!",
                "new_password": "SecurePassword!",
                "password_confirmation": "SecurePassword!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one digit."],
        )

    def test_update_account_form_password_no_special_character(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": "SecurePassword123!",
                "new_password": "SecurePassword123",
                "password_confirmation": "SecurePassword123",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [
                "Password must contain at least one special character (!@#$%^&*()-_+=<>?/)."
            ],
        )

    def test_update_account_form_wrong_password(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "old_password": "WrongPassword123!",
                "new_password": "NewSecurePassword123!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["old_password"],
            ["The password you entered is incorrect."],
        )

    def test_update_account_form_no_old_password(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "new_password": "NewSecurePassword123!",
                "password_confirmation": "NewSecurePassword123!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["old_password"],
            ["Please enter your current password."],
        )

    def test_update_account_form_no_new_password(self):
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "old_password": "SecurePassword123!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Please enter a new password."],
        )


class DeleteAccountFormTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password="SecurePassword123!",
        )

    def test_delete_account_form_valid_data(self):
        form = DeleteAccountForm(
            user=self.user,
            data={
                "password": "SecurePassword123!",
            },
        )
        self.assertTrue(form.is_valid())

    def test_delete_account_form_no_data(self):
        form = DeleteAccountForm(user=self.user, data={})
        self.assertFalse(form.is_valid())

    def test_delete_account_form_wrong_password(self):
        form = DeleteAccountForm(
            user=self.user,
            data={
                "password": "WrongPassword123!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["The password you entered is incorrect."],
        )


class PasswordResetFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password="SecurePassword123!",
        )

    def test_password_reset_form_valid_data(self):
        form = PasswordResetForm(
            data={
                "new_password": "NewSecurePassword123!",
                "password_confirmation": "NewSecurePassword123!",
            }
        )
        self.assertTrue(form.is_valid())

    def test_password_reset_form_no_data(self):
        form = PasswordResetForm(data={})
        self.assertFalse(form.is_valid())

    def test_password_reset_form_passwords_not_matching(self):
        form = PasswordResetForm(
            data={
                "new_password": "NewSecurePassword123!",
                "password_confirmation": "NewSecurePassword123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password_confirmation"],
            ["The passwords you entered do not match. Please try again."],
        )

    def test_password_reset_form_password_too_short(self):
        form = PasswordResetForm(
            data={
                "new_password": "Save-1",
                "password_confirmation": "Save-1",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must be at least 8 characters long."],
        )

    def test_password_reset_form_password_no_uppercase(self):
        form = PasswordResetForm(
            data={
                "new_password": "securepassword123!",
                "password_confirmation": "securepassword123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one uppercase letter."],
        )

    def test_password_reset_form_password_no_lowercase(self):
        form = PasswordResetForm(
            data={
                "new_password": "SECUREPASSWORD123!",
                "password_confirmation": "SECUREPASSWORD123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one lowercase letter."],
        )

    def test_password_reset_form_password_no_number(self):
        form = PasswordResetForm(
            data={
                "new_password": "SecurePassword!",
                "password_confirmation": "SecurePassword!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one digit."],
        )

    def test_password_reset_form_password_no_special_character(self):
        form = PasswordResetForm(
            data={
                "new_password": "SecurePassword123",
                "password_confirmation": "SecurePassword123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [
                "Password must contain at least one special character (!@#$%^&*()-_+=<>?/)."
            ],
        )
