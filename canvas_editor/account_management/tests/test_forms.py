from allauth.socialaccount.models import SocialAccount
from django.test import TestCase

from account_management.forms import (
    DeleteAccountForm,
    LoginForm,
    PasswordForgottenForm,
    PasswordResetForm,
    RegisterForm,
    UpdateAccountForm,
)
from account_management.models import User
from canvas.test_constants import (
    MISMATCHED_BUT_CORRECT_PASSWORD,
    NEW_PASSWORD_FIELD,
    NO_LOWERCASE_PASSWORD,
    NO_NUMERIC_PASSWORD,
    NO_SPECIAL_CHAR_PASSWORD,
    NO_UPPERCASE_PASSWORD,
    SECURE_PASSWORD,
    TOO_SHORT_PASSWORD,
    UPDATED_PASSWORD,
    WRONG_LOGIN_PASSWORD,
    TEST_FIRST_NAME,
    TEST_EMAIL_2,
    TEST_LAST_NAME,
    NEW_FIRST_NAME,
    NEW_LAST_NAME,
    TEST_EMAIL_3,
    NEW_EMAIL,
    TEST_FIRST_NAME_2,
    TEST_LAST_NAME_2,
    FIRST_NAME_FIELD,
    LAST_NAME_FIELD,
    EMAIL_FIELD,
    PASSWORD_FIELD,
    PASSWORD_CONFIRMATION_FIELD,
)
from canvas import message_dict


class FormTestMixin:
    default_data = {}

    def create_form(self, **overrides):
        data = self.default_data.copy()
        data.update(overrides)
        return self.form_class(data=data)


class RegisterFormTest(FormTestMixin, TestCase):
    form_class = RegisterForm
    default_data = {
        FIRST_NAME_FIELD: TEST_FIRST_NAME,
        LAST_NAME_FIELD: TEST_LAST_NAME,
        EMAIL_FIELD: TEST_EMAIL_2,
        PASSWORD_FIELD: SECURE_PASSWORD,
        PASSWORD_CONFIRMATION_FIELD: SECURE_PASSWORD,
    }

    def test_register_form_valid_data(self):
        # Test case for valid data submission in RegisterForm
        form = self.create_form()
        self.assertTrue(form.is_valid())

    def test_register_form_no_data(self):
        # Test case for RegisterForm with no data
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())

    def test_register_form_existing_mail(self):
        # Test case for RegisterForm with an already existing email
        User.objects.create_user(
            username=TEST_EMAIL_2,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
        )
        form = self.create_form()
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            [message_dict.email_already_in_use_text],
        )

    def test_register_form_passwords_not_matching(self):
        # Test case for RegisterForm where passwords do not match
        form = self.create_form(
            **{PASSWORD_CONFIRMATION_FIELD: MISMATCHED_BUT_CORRECT_PASSWORD}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_match_criterium_text],
        )

    def test_register_form_password_too_short(self):
        # Test case for RegisterForm where password is too short
        form = self.create_form(
            **{
                PASSWORD_FIELD: TOO_SHORT_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: TOO_SHORT_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_length_criterium_text],
        )

    def test_register_form_password_no_uppercase(self):
        # Test case for RegisterForm where password has no uppercase letter
        form = self.create_form(
            **{
                PASSWORD_FIELD: NO_UPPERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_UPPERCASE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_uppercase_criterium_text],
        )

    def test_register_form_password_no_lowercase(self):
        # Test case for RegisterForm where password has no lowercase letter
        form = self.create_form(
            **{
                PASSWORD_FIELD: NO_LOWERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_LOWERCASE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_lowercase_criterium_text],
        )

    def test_register_form_password_no_number(self):
        # Test case for RegisterForm where password has no number
        form = self.create_form(
            **{
                PASSWORD_FIELD: NO_NUMERIC_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_NUMERIC_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_digit_criterium_text],
        )

    def test_register_form_password_no_special_character(self):
        # Test case for RegisterForm where password has no special character
        form = self.create_form(
            **{
                PASSWORD_FIELD: NO_SPECIAL_CHAR_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_SPECIAL_CHAR_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.password_special_char_criterium_text],
        )


class LoginFormTest(FormTestMixin, TestCase):
    form_class = LoginForm
    default_data = {
        "email": TEST_EMAIL_2,
        "password": SECURE_PASSWORD,
    }

    def setUp(self):
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
        )

    def test_login_form_valid_data(self):
        # Test case for valid data submission in LoginForm
        form = self.create_form()
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_login_form_no_data(self):
        # Test case for LoginForm with no data
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())

    def test_login_form_wrong_email(self):
        # Test case for LoginForm with not existing email
        form = self.create_form(
            **{
                EMAIL_FIELD: TEST_EMAIL_3,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            [message_dict.email_not_registered_text],
        )

    def test_login_form_wrong_password(self):
        # Test case for LoginForm with wrong password
        form = self.create_form(**{PASSWORD_FIELD: NO_SPECIAL_CHAR_PASSWORD})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            [message_dict.incorrect_password_text],
        )


class UpdateAccountFormTest(FormTestMixin, TestCase):
    form_class = UpdateAccountForm
    default_data = {
        "first_name": NEW_FIRST_NAME,
        "last_name": NEW_LAST_NAME,
        "email": NEW_EMAIL,
        "old_password": SECURE_PASSWORD,
        "new_password": UPDATED_PASSWORD,
        "password_confirmation": UPDATED_PASSWORD,
    }

    def setUp(self):
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
        )

    def test_update_account_form_valid_data(self):
        # Test case for valid data submission in UpdateAccountForm
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": NEW_EMAIL,
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
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": NEW_EMAIL,
            },
        )
        self.assertTrue(form.is_valid())

    def test_update_account_form_existing_mail(self):
        # Test case for UpdateAccountForm with an already existing email
        User.objects.create_user(
            username=TEST_EMAIL_3,
            first_name=TEST_FIRST_NAME_2,
            last_name=TEST_LAST_NAME_2,
            email=TEST_EMAIL_3,
            password=SECURE_PASSWORD,
        )
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_3,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            [message_dict.email_already_in_use_text],
        )

    def test_update_account_form_openID_account(self):
        # Test case for UpdateAccountForm with OpenID account
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider="google"
        )
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
            },
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_email(), self.user.email)

    def test_update_account_form_passwords_not_matching(self):
        # Test case for UpdateAccountForm where passwords do not match
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": SECURE_PASSWORD,
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password_confirmation"],
            [message_dict.password_match_criterium_text],
        )

    def test_update_account_form_password_too_short(self):
        # Test case for UpdateAccountForm where password is too short
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": TEST_FIRST_NAME,
                "last_name": TEST_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": SECURE_PASSWORD,
                "new_password": TOO_SHORT_PASSWORD,
                "password_confirmation": TOO_SHORT_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_length_criterium_text],
        )

    def test_update_account_form_password_no_uppercase(self):
        # Test case for UpdateAccountForm where password has no uppercase letter
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": TEST_FIRST_NAME,
                "last_name": TEST_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": SECURE_PASSWORD,
                "new_password": NO_UPPERCASE_PASSWORD,
                "password_confirmation": NO_UPPERCASE_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_uppercase_criterium_text],
        )

    def test_update_account_form_password_no_lowercase(self):
        # Test case for UpdateAccountForm where password has no lowercase letter
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": TEST_FIRST_NAME,
                "last_name": TEST_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": SECURE_PASSWORD,
                "new_password": NO_LOWERCASE_PASSWORD,
                "password_confirmation": NO_LOWERCASE_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_lowercase_criterium_text],
        )

    def test_update_account_form_password_no_number(self):
        # Test case for UpdateAccountForm where password has no number
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": TEST_FIRST_NAME,
                "last_name": TEST_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": SECURE_PASSWORD,
                "new_password": NO_NUMERIC_PASSWORD,
                "password_confirmation": NO_NUMERIC_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_digit_criterium_text],
        )

    def test_update_account_form_password_no_special_character(self):
        # Test case for UpdateAccountForm where password has no special character
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": TEST_FIRST_NAME,
                "last_name": TEST_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": SECURE_PASSWORD,
                "new_password": NO_SPECIAL_CHAR_PASSWORD,
                "password_confirmation": NO_SPECIAL_CHAR_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_special_char_criterium_text],
        )

    def test_update_account_form_wrong_password(self):
        # Test case for UpdateAccountForm with wrong password
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": WRONG_LOGIN_PASSWORD,
                "new_password": UPDATED_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["old_password"],
            [message_dict.incorrect_password_text],
        )

    def test_update_account_form_no_old_password(self):
        # Test case for UpdateAccountForm with no old password
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_2,
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": UPDATED_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["old_password"],
            [message_dict.current_password_prompt],
        )

    def test_update_account_form_no_new_password(self):
        # Test case for UpdateAccountForm with no new password
        form = UpdateAccountForm(
            instance=self.user,
            data={
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": SECURE_PASSWORD,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.new_password_prompt],
        )


class DeleteAccountFormTest(FormTestMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
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
            [message_dict.incorrect_password_text],
        )


class PasswordResetFormTest(FormTestMixin, TestCase):
    form_class = PasswordResetForm
    default_data = {
        NEW_PASSWORD_FIELD: UPDATED_PASSWORD,
        PASSWORD_CONFIRMATION_FIELD: UPDATED_PASSWORD,
    }

    def setUp(self):
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
        )

    def test_password_reset_form_valid_data(self):
        # Test case for valid data submission in PasswordResetForm
        form = self.create_form()
        self.assertTrue(form.is_valid())

    def test_password_reset_form_no_data(self):
        # Test case for PasswordResetForm with no data
        form = PasswordResetForm(data={})
        self.assertFalse(form.is_valid())

    def test_password_reset_form_passwords_not_matching(self):
        # Test case for PasswordResetForm where passwords do not match
        form = self.create_form(
            **{PASSWORD_CONFIRMATION_FIELD: MISMATCHED_BUT_CORRECT_PASSWORD}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password_confirmation"],
            [message_dict.password_match_criterium_text],
        )

    def test_password_reset_form_password_too_short(self):
        # Test case for PasswordResetForm where password is too short
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: TOO_SHORT_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: TOO_SHORT_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_length_criterium_text],
        )

    def test_password_reset_form_password_no_uppercase(self):
        # Test case for PasswordResetForm where password has no uppercase letter
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: NO_UPPERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_UPPERCASE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_uppercase_criterium_text],
        )

    def test_password_reset_form_password_no_lowercase(self):
        # Test case for PasswordResetForm where password has no lowercase letter
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: NO_LOWERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_LOWERCASE_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_lowercase_criterium_text],
        )

    def test_password_reset_form_password_no_number(self):
        # Test case for PasswordResetForm where password has no number
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: NO_NUMERIC_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_NUMERIC_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_digit_criterium_text],
        )

    def test_password_reset_form_password_no_special_character(self):
        # Test case for PasswordResetForm where password has no special character
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: NO_SPECIAL_CHAR_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_SPECIAL_CHAR_PASSWORD,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["new_password"],
            [message_dict.password_special_char_criterium_text],
        )


class PasswordForgottenFormTest(FormTestMixin, TestCase):
    form_class = PasswordForgottenForm
    default_data = {
        "email": TEST_EMAIL_2,
    }

    def setUp(self):
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
        )

    def test_password_forgotten_form_valid_data(self):

        # Test case for valid data submission in PasswordForgottenForm
        form = self.create_form()
        self.assertTrue(form.is_valid())

    def test_password_forgotten_form_no_data(self):
        # Test case for PasswordForgottenForm with no data
        form = PasswordForgottenForm(data={})
        self.assertFalse(form.is_valid())

    def test_password_forgotten_form_wrong_email(self):
        # Test case for PasswordForgottenForm with not existing email
        form = self.create_form(**{EMAIL_FIELD: TEST_EMAIL_3})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["email"],
            [message_dict.email_not_registered_text],
        )
