from allauth.socialaccount.models import SocialAccount
from django.test import TestCase

from account_management.forms.update_account_form import UpdateAccountForm
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
    WRONG_LOGIN_PASSWORD,
)
from canvas import message_dict


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
            [message_dict.password_match_criterium_text],
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
            [message_dict.password_length_criterium_text],
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
            [message_dict.password_uppercase_criterium_text],
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
            [message_dict.password_lowercase_criterium_text],
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
            [message_dict.password_digit_criterium_text],
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
            [message_dict.password_special_char_criterium_text],
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
            [message_dict.incorrect_password_text],
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
            [message_dict.enter_current_password_text],
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
            [message_dict.enter_new_password_text],
        )
