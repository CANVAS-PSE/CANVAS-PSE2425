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
    EMPTY_FIELD,
    MISMATCHED_BUT_CORRECT_PASSWORD,
    NEW_PASSWORD_FIELD,
    NO_LOWERCASE_PASSWORD,
    NO_NUMERIC_PASSWORD,
    NO_SPECIAL_CHAR_PASSWORD,
    NO_UPPERCASE_PASSWORD,
    OPENID_PROVIDER_FIELD,
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
    OLD_PASSWORD_FIELD,
    NEW_PASSWORD_FIELD,
)
from canvas import message_dict


class FormTestMixin:
    """
    A mixin class for form tests.
    """

    default_data = {}

    def create_form(self, **overrides):
        """
        Create a form instance with the given overrides.
        """
        data = self.default_data.copy()
        data.update(overrides)
        return self.form_class(data=data)

    def create_form_with_instance(self, **overrides):
        """
        Create a form instance with the given overrides while using the specified instance.
        """
        data = self.default_data.copy()
        data.update(overrides)
        return self.form_class(instance=self.instance, data=data)

    def create_form_with_user(self, **overrides):
        """
        Create a form instance with the given overrides while using the specified user.
        """
        data = self.default_data.copy()
        data.update(overrides)
        return self.form_class(user=self.user, data=data)

    def assertFormErrorMessage(self, form, field, expected_message):
        """
        Assert that the form contains the expected error message for the given field.
        """
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[field], [expected_message])


class RegisterFormTest(FormTestMixin, TestCase):
    """
    Test cases for the RegisterForm.
    """

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
        form = self.create_form(
            **{
                FIRST_NAME_FIELD: EMPTY_FIELD,
                LAST_NAME_FIELD: EMPTY_FIELD,
                EMAIL_FIELD: EMPTY_FIELD,
                PASSWORD_FIELD: EMPTY_FIELD,
                PASSWORD_CONFIRMATION_FIELD: EMPTY_FIELD,
            }
        )
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
        self.assertFormErrorMessage(
            form, EMAIL_FIELD, message_dict.email_already_in_use_text
        )

    def test_register_form_passwords_not_matching(self):
        # Test case for RegisterForm where passwords do not match
        form = self.create_form(
            **{PASSWORD_CONFIRMATION_FIELD: MISMATCHED_BUT_CORRECT_PASSWORD}
        )
        self.assertFormErrorMessage(
            form, PASSWORD_FIELD, message_dict.password_match_criterium_text
        )

    def test_register_form_password_too_short(self):
        # Test case for RegisterForm where password is too short
        form = self.create_form(
            **{
                PASSWORD_FIELD: TOO_SHORT_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: TOO_SHORT_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, PASSWORD_FIELD, message_dict.password_length_criterium_text
        )

    def test_register_form_password_no_uppercase(self):
        # Test case for RegisterForm where password has no uppercase letter
        form = self.create_form(
            **{
                PASSWORD_FIELD: NO_UPPERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_UPPERCASE_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, PASSWORD_FIELD, message_dict.password_uppercase_criterium_text
        )

    def test_register_form_password_no_lowercase(self):
        # Test case for RegisterForm where password has no lowercase letter
        form = self.create_form(
            **{
                PASSWORD_FIELD: NO_LOWERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_LOWERCASE_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, PASSWORD_FIELD, message_dict.password_lowercase_criterium_text
        )

    def test_register_form_password_no_number(self):
        # Test case for RegisterForm where password has no number
        form = self.create_form(
            **{
                PASSWORD_FIELD: NO_NUMERIC_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_NUMERIC_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, PASSWORD_FIELD, message_dict.password_digit_criterium_text
        )

    def test_register_form_password_no_special_character(self):
        # Test case for RegisterForm where password has no special character
        form = self.create_form(
            **{
                PASSWORD_FIELD: NO_SPECIAL_CHAR_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_SPECIAL_CHAR_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, PASSWORD_FIELD, message_dict.password_special_char_criterium_text
        )


class LoginFormTest(FormTestMixin, TestCase):
    """
    Test cases for the LoginForm.
    """

    form_class = LoginForm
    default_data = {
        EMAIL_FIELD: TEST_EMAIL_2,
        PASSWORD_FIELD: SECURE_PASSWORD,
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
        form = self.create_form(
            **{
                EMAIL_FIELD: EMPTY_FIELD,
                PASSWORD_FIELD: EMPTY_FIELD,
            }
        )
        self.assertFalse(form.is_valid())

    def test_login_form_wrong_email(self):
        # Test case for LoginForm with not existing email
        form = self.create_form(
            **{
                EMAIL_FIELD: TEST_EMAIL_3,
            }
        )
        self.assertFormErrorMessage(
            form, EMAIL_FIELD, message_dict.email_not_registered_text
        )

    def test_login_form_wrong_password(self):
        # Test case for LoginForm with wrong password
        form = self.create_form(**{PASSWORD_FIELD: NO_SPECIAL_CHAR_PASSWORD})
        self.assertFormErrorMessage(
            form, PASSWORD_FIELD, message_dict.incorrect_password_text
        )


class UpdateAccountFormTest(FormTestMixin, TestCase):
    """
    Test cases for the UpdateAccountForm.
    """

    form_class = UpdateAccountForm
    default_data = {
        FIRST_NAME_FIELD: NEW_FIRST_NAME,
        LAST_NAME_FIELD: NEW_LAST_NAME,
        EMAIL_FIELD: NEW_EMAIL,
        OLD_PASSWORD_FIELD: SECURE_PASSWORD,
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
        self.instance = self.user

    def test_update_account_form_valid_data(self):
        # Test case for valid data submission in UpdateAccountForm
        form = self.create_form_with_instance()
        self.assertTrue(form.is_valid())

    def test_update_account_form_no_password(self):
        # Test case for UpdateAccountForm with no password
        form = self.create_form_with_instance(
            **{
                NEW_PASSWORD_FIELD: EMPTY_FIELD,
                OLD_PASSWORD_FIELD: EMPTY_FIELD,
                PASSWORD_CONFIRMATION_FIELD: EMPTY_FIELD,
            }
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
        form = self.create_form_with_instance(**{EMAIL_FIELD: TEST_EMAIL_3})
        self.assertFormErrorMessage(
            form, EMAIL_FIELD, message_dict.email_already_in_use_text
        )

    def test_update_account_form_openID_account(self):
        # Test case for UpdateAccountForm with OpenID account
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider=OPENID_PROVIDER_FIELD
        )
        form = self.create_form_with_instance()
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_email(), self.user.email)

    def test_update_account_form_passwords_not_matching(self):
        # Test case for UpdateAccountForm where passwords do not match
        form = self.create_form_with_instance(
            **{
                EMAIL_FIELD: NEW_EMAIL,
                PASSWORD_CONFIRMATION_FIELD: MISMATCHED_BUT_CORRECT_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form,
            PASSWORD_CONFIRMATION_FIELD,
            message_dict.password_match_criterium_text,
        )

    def test_update_account_form_password_too_short(self):
        # Test case for UpdateAccountForm where password is too short
        form = self.create_form_with_instance(
            **{
                FIRST_NAME_FIELD: TEST_FIRST_NAME,
                LAST_NAME_FIELD: TEST_LAST_NAME,
                EMAIL_FIELD: TEST_EMAIL_2,
                NEW_PASSWORD_FIELD: TOO_SHORT_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: TOO_SHORT_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_length_criterium_text
        )

    def test_update_account_form_password_no_uppercase(self):
        # Test case for UpdateAccountForm where password has no uppercase letter
        form = self.create_form_with_instance(
            **{
                NEW_EMAIL: TEST_EMAIL_2,
                NEW_PASSWORD_FIELD: NO_UPPERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_UPPERCASE_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_uppercase_criterium_text
        )

    def test_update_account_form_password_no_lowercase(self):
        # Test case for UpdateAccountForm where password has no lowercase letter
        form = self.create_form_with_instance(
            **{
                FIRST_NAME_FIELD: TEST_FIRST_NAME,
                LAST_NAME_FIELD: TEST_LAST_NAME,
                EMAIL_FIELD: TEST_EMAIL_2,
                NEW_PASSWORD_FIELD: NO_LOWERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_LOWERCASE_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_lowercase_criterium_text
        )

    def test_update_account_form_password_no_number(self):
        # Test case for UpdateAccountForm where password has no number
        form = self.create_form_with_instance(
            **{
                FIRST_NAME_FIELD: TEST_FIRST_NAME,
                LAST_NAME_FIELD: TEST_LAST_NAME,
                EMAIL_FIELD: TEST_EMAIL_2,
                NEW_PASSWORD_FIELD: NO_NUMERIC_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_NUMERIC_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_digit_criterium_text
        )

    def test_update_account_form_password_no_special_character(self):
        # Test case for UpdateAccountForm where password has no special character
        form = self.create_form_with_instance(
            **{
                FIRST_NAME_FIELD: TEST_FIRST_NAME,
                LAST_NAME_FIELD: TEST_LAST_NAME,
                EMAIL_FIELD: TEST_EMAIL_2,
                NEW_PASSWORD_FIELD: NO_SPECIAL_CHAR_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_SPECIAL_CHAR_PASSWORD,
            },
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_special_char_criterium_text
        )

    def test_update_account_form_wrong_password(self):
        # Test case for UpdateAccountForm with wrong password
        form = self.create_form_with_instance(
            **{
                EMAIL_FIELD: TEST_EMAIL_2,
                OLD_PASSWORD_FIELD: WRONG_LOGIN_PASSWORD,
                NEW_PASSWORD_FIELD: UPDATED_PASSWORD,
            },
        )
        self.assertFormErrorMessage(
            form, OLD_PASSWORD_FIELD, message_dict.incorrect_password_text
        )

    def test_update_account_form_no_old_password(self):
        # Test case for UpdateAccountForm with no old password
        form = self.create_form_with_instance(
            **{
                OLD_PASSWORD_FIELD: EMPTY_FIELD,
                EMAIL_FIELD: TEST_EMAIL_2,
            },
        )
        self.assertFormErrorMessage(
            form, OLD_PASSWORD_FIELD, message_dict.current_password_prompt
        )

    def test_update_account_form_no_new_password(self):
        # Test case for UpdateAccountForm with no new password
        form = self.create_form_with_instance(
            **{
                EMAIL_FIELD: TEST_EMAIL_2,
                NEW_PASSWORD_FIELD: EMPTY_FIELD,
            },
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.new_password_prompt
        )


class DeleteAccountFormTest(FormTestMixin, TestCase):
    """
    Test cases for the DeleteAccountForm.
    """

    form_class = DeleteAccountForm
    default_data = {
        PASSWORD_FIELD: SECURE_PASSWORD,
    }

    def setUp(self):
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
        )
        self.user = self.user

    def test_delete_account_form_valid_data(self):
        # Test case for valid data submission in DeleteAccountForm
        form = self.create_form_with_user()
        self.assertTrue(form.is_valid())

    def test_delete_account_form_no_data(self):
        # Test case for DeleteAccountForm with no data
        form = self.create_form_with_user(**{PASSWORD_FIELD: EMPTY_FIELD})
        self.assertFalse(form.is_valid())

    def test_delete_account_form_wrong_password(self):
        # Test case for DeleteAccountForm with wrong password
        form = self.create_form_with_user(
            **{
                PASSWORD_FIELD: WRONG_LOGIN_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, PASSWORD_FIELD, message_dict.incorrect_password_text
        )


class PasswordResetFormTest(FormTestMixin, TestCase):
    """
    Test cases for the PasswordResetForm.
    """

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
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: EMPTY_FIELD,
                PASSWORD_CONFIRMATION_FIELD: EMPTY_FIELD,
            }
        )
        self.assertFalse(form.is_valid())

    def test_password_reset_form_passwords_not_matching(self):
        # Test case for PasswordResetForm where passwords do not match
        form = self.create_form(
            **{PASSWORD_CONFIRMATION_FIELD: MISMATCHED_BUT_CORRECT_PASSWORD}
        )
        self.assertFormErrorMessage(
            form,
            PASSWORD_CONFIRMATION_FIELD,
            message_dict.password_match_criterium_text,
        )

    def test_password_reset_form_password_too_short(self):
        # Test case for PasswordResetForm where password is too short
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: TOO_SHORT_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: TOO_SHORT_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_length_criterium_text
        )

    def test_password_reset_form_password_no_uppercase(self):
        # Test case for PasswordResetForm where password has no uppercase letter
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: NO_UPPERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_UPPERCASE_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_uppercase_criterium_text
        )

    def test_password_reset_form_password_no_lowercase(self):
        # Test case for PasswordResetForm where password has no lowercase letter
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: NO_LOWERCASE_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_LOWERCASE_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_lowercase_criterium_text
        )

    def test_password_reset_form_password_no_number(self):
        # Test case for PasswordResetForm where password has no number
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: NO_NUMERIC_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_NUMERIC_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_digit_criterium_text
        )

    def test_password_reset_form_password_no_special_character(self):
        # Test case for PasswordResetForm where password has no special character
        form = self.create_form(
            **{
                NEW_PASSWORD_FIELD: NO_SPECIAL_CHAR_PASSWORD,
                PASSWORD_CONFIRMATION_FIELD: NO_SPECIAL_CHAR_PASSWORD,
            }
        )
        self.assertFormErrorMessage(
            form, NEW_PASSWORD_FIELD, message_dict.password_special_char_criterium_text
        )


class PasswordForgottenFormTest(FormTestMixin, TestCase):
    """
    Test cases for the PasswordForgottenForm.
    """

    form_class = PasswordForgottenForm
    default_data = {
        EMAIL_FIELD: TEST_EMAIL_2,
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
        form = self.create_form(**{EMAIL_FIELD: EMPTY_FIELD})
        self.assertFalse(form.is_valid())

    def test_password_forgotten_form_wrong_email(self):
        # Test case for PasswordForgottenForm with not existing email
        form = self.create_form(**{EMAIL_FIELD: TEST_EMAIL_3})
        self.assertFormErrorMessage(
            form, EMAIL_FIELD, message_dict.email_not_registered_text
        )
