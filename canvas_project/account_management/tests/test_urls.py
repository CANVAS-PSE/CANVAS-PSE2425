from django.test import SimpleTestCase
from django.urls import reverse, resolve
from account_management.views import (
    login_view,
    logout_view,
    register_view,
    update_account,
    delete_account,
    password_reset_view,
    invalid_link,
    confirm_deletion,
    password_forgotten_view,
)


class TestUrls(SimpleTestCase):

    def test_login_url_resolves(self):
        url = reverse("login")
        self.assertEqual(resolve(url).func, login_view)

    def test_register_url_resolves(self):
        url = reverse("register")
        self.assertEqual(resolve(url).func, register_view)

    def test_logout_url_resolves(self):
        url = reverse("logout")
        self.assertEqual(resolve(url).func, logout_view)

    def test_update_account_url_resolves(self):
        url = reverse("update_account")
        self.assertEqual(resolve(url).func, update_account)

    def test_delete_account_url_resolves(self):
        url = reverse("delete_account")
        self.assertEqual(resolve(url).func, delete_account)

    def test_password_reset_url_resolves(self):
        url = reverse("password_reset", args=["uidb64", "token"])
        self.assertEqual(resolve(url).func, password_reset_view)

    def test_invalid_link_url_resolves(self):
        url = reverse("invalid_link")
        self.assertEqual(resolve(url).func, invalid_link)

    def test_confirm_deletion_url_resolves(self):
        url = reverse("confirm_deletion", args=["uidb64", "token"])
        self.assertEqual(resolve(url).func, confirm_deletion)

    def test_password_forgotten_url_resolves(self):
        url = reverse("password_forgotten")
        self.assertEqual(resolve(url).func, password_forgotten_view)
