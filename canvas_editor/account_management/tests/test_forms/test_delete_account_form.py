from django.test import TestCase

from account_management.forms.delete_account_form import DeleteAccountForm
from account_management.models import User
from account_management.tests.test_constants import (
    SECURE_PASSWORD,
    WRONG_LOGIN_PASSWORD,
)
from canvas import message_dict


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
            [message_dict.incorrect_password_text],
        )
