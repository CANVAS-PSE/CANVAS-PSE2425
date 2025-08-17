from django.test import SimpleTestCase
from django.urls import resolve, reverse

from account_management.views import (
    ConfirmDeletionView,
    LoginView,
    PasswordForgottenView,
    PasswordResetView,
    RegistrationView,
    delete_account,
    invalid_link,
    logout_view,
    update_account,
)


class TestUrls(SimpleTestCase):
    """Test if the urls return the correct view."""

    def test_login_url_resolves(self):
        """Test login url."""
        url = reverse("login")
        self.assertEqual(resolve(url).func.view_class, LoginView)

    def test_register_url_resolves(self):
        """Test register url."""
        url = reverse("register")
        self.assertEqual(resolve(url).func.view_class, RegistrationView)

    def test_logout_url_resolves(self):
        """Test logout url."""
        url = reverse("logout")
        self.assertEqual(resolve(url).func, logout_view)

    def test_update_account_url_resolves(self):
        """Test update account url."""
        url = reverse("update_account")
        self.assertEqual(resolve(url).func, update_account)

    def test_delete_account_url_resolves(self):
        """Test delete account url."""
        url = reverse("delete_account")
        self.assertEqual(resolve(url).func, delete_account)

    def test_password_reset_url_resolves(self):
        """Test password reset url."""
        url = reverse("password_reset", args=["uidb64", "token"])
        self.assertEqual(resolve(url).func.view_class, PasswordResetView)

    def test_invalid_link_url_resolves(self):
        """Test the invalid link url."""
        url = reverse("invalid_link")
        self.assertEqual(resolve(url).func, invalid_link)

    def test_confirm_deletion_url_resolves(self):
        """Test the confirm deletion url."""
        url = reverse("confirm_deletion", args=["uidb64", "token"])
        self.assertEqual(resolve(url).func.view_class, ConfirmDeletionView)

    def test_password_forgotten_url_resolves(self):
        """Test the password forgotten url."""
        url = reverse("password_forgotten")
        self.assertEqual(resolve(url).func.view_class, PasswordForgottenView)
