from django.test import SimpleTestCase
from django.urls import resolve, reverse

from account_management.views import (
    ConfirmDeletionView,
    LoginView,
    PasswordForgottenView,
    PasswordResetView,
    RegistrationView,
    DeleteAccountView,
    InvalidLinkView,
    LogoutView,
    UpdateAccountView,
)

URLS_TO_VIEWS = [
    ("login", (), LoginView),
    ("register", (), RegistrationView),
    ("logout", (), LogoutView),
    ("update_account", (), UpdateAccountView),
    ("delete_account", (), DeleteAccountView),
    ("password_reset", ("uidb64", "token"), PasswordResetView),
    ("invalid_link", (), InvalidLinkView),
    ("confirm_deletion", ("uidb64", "token"), ConfirmDeletionView),
    ("password_forgotten", (), PasswordForgottenView),
]


class TestUrls(SimpleTestCase):
    """Test if the urls return the correct view."""

    def test_urls_resolve_to_correct_views(self):
        for name, args, view in URLS_TO_VIEWS:
            url = reverse(name, args=args)
            self.assertEqual(resolve(url).func.view_class, view)
