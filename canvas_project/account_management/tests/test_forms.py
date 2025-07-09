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
from allauth.socialaccount.models import SocialAccount
from test_constants import (
    TOO_SHORT_PASSWORD,
    SECURE_PASSWORD,
    NO_UPPERCASE_PASSWORD,
    NO_LOWERCASE_PASSWORD,
    UPDATED_PASSWORD,
    NO_NUMERIC_PASSWORD,
    NO_SPECIAL_CHAR_PASSWORD,
    MISMATCHED_BUT_CORRECT_PASSWORD,
    WRONG_LOGIN_PASSWORD,
)


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
            ["This email address is already in use. Please try another."],
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
            ["The passwords you entered do not match. Please try again."],
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
            ["Password must be at least 8 characters long."],
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
            ["Password must contain at least one uppercase letter."],
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
            ["Password must contain at least one lowercase letter."],
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
            ["Password must contain at least one digit."],
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
            ["This email address is not registered."],
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
            ["The password you entered is incorrect."],
        )


class UpdateAccountFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@mail.de",
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password=SECURE_PASSWORD,
        )

    def test_update_account_form_valid_data(self):
        # Test case for valid data submission in UpdateAccountForm
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "new_test@mail.de",
                "old_password": SECURE_PASSWORD,
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": UPDATED_PASSWORD,
            },
        )
        self.assertTrue(form.is_valid())

    def test_update_account_form_no_password(self):
        # Test case for UpdateAccountForm with no password
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
        # Test case for UpdateAccountForm with an already existing email
        User.objects.create_user(
            username="test2@mail.de",
            first_name="test2_first_name",
            last_name="test2_last_name",
            email="test2@mail.de",
            password=SECURE_PASSWORD,
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

    def test_update_account_form_openID_account(self):
        # Test case for UpdateAccountForm with OpenID account
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider="google"
        )
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
            },
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_email(), self.user.email)

    def test_update_account_form_passwords_not_matching(self):
        # Test case for UpdateAccountForm where passwords do not match
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "old_password": SECURE_PASSWORD,
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password_confirmation"],
            ["The passwords you entered do not match. Please try again."],
        )

    def test_update_account_form_password_too_short(self):
        # Test case for UpdateAccountForm where password is too short
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": SECURE_PASSWORD,
                "new_password": TOO_SHORT_PASSWORD,
                "password_confirmation": TOO_SHORT_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must be at least 8 characters long."],
        )

    def test_update_account_form_password_no_uppercase(self):
        # Test case for UpdateAccountForm where password has no uppercase letter
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": SECURE_PASSWORD,
                "new_password": NO_UPPERCASE_PASSWORD,
                "password_confirmation": NO_UPPERCASE_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one uppercase letter."],
        )

    def test_update_account_form_password_no_lowercase(self):
        # Test case for UpdateAccountForm where password has no lowercase letter
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": SECURE_PASSWORD,
                "new_password": NO_LOWERCASE_PASSWORD,
                "password_confirmation": NO_LOWERCASE_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one lowercase letter."],
        )

    def test_update_account_form_password_no_number(self):
        # Test case for UpdateAccountForm where password has no number
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": SECURE_PASSWORD,
                "new_password": NO_NUMERIC_PASSWORD,
                "password_confirmation": NO_NUMERIC_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            ["Password must contain at least one digit."],
        )

    def test_update_account_form_password_no_special_character(self):
        # Test case for UpdateAccountForm where password has no special character
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "old_password": SECURE_PASSWORD,
                "new_password": NO_SPECIAL_CHAR_PASSWORD,
                "password_confirmation": NO_SPECIAL_CHAR_PASSWORD,
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
        # Test case for UpdateAccountForm with wrong password
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "old_password": WRONG_LOGIN_PASSWORD,
                "new_password": UPDATED_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["old_password"],
            ["The password you entered is incorrect."],
        )

    def test_update_account_form_no_old_password(self):
        # Test case for UpdateAccountForm with no old password
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": UPDATED_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["old_password"],
            ["Please enter your current password."],
        )

    def test_update_account_form_no_new_password(self):
        # Test case for UpdateAccountForm with no new password
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "old_password": SECURE_PASSWORD,
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
            password=SECURE_PASSWORD,
        )

    def test_delete_account_form_valid_data(self):
        # Test case for valid data submission in DeleteAccountForm
        form = DeleteAccountForm(
            user=self.user,
            data={
                "password": SECURE_PASSWORD,
            },
        )
        self.assertTrue(form.is_valid())

    def test_delete_account_form_no_data(self):
        # Test case for DeleteAccountForm with no data
        form = DeleteAccountForm(user=self.user, data={})
        self.assertFalse(form.is_valid())

    def test_delete_account_form_wrong_password(self):
        # Test case for DeleteAccountForm with wrong password
        form = DeleteAccountForm(
            user=self.user,
            data={
                "password": WRONG_LOGIN_PASSWORD,
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
            ["This email address is not registered."],
        )
