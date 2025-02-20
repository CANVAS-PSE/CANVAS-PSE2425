from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.test.client import RequestFactory
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from account_management.views import send_register_email, send_password_change_email


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")
        self.projects_url = reverse("projects")
        self.user = User.objects.create_user(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password="SecurePass123!",
            username="test@mail.de",
        )
        self.valid_user_data = {
            "first_name": "test2_first_name",
            "last_name": "test2_last_name",
            "email": "test2@mail.de",
            "password": "SecurePass123!",
            "password_confirmation": "SecurePass123!",
        }

    def test_GET(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_GET_authenticated(self):
        self.client.login(username="test@mail.de", password="SecurePass123!")

        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)

    def test_POST_valid_data(self):
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
        )
        user = User.objects.get(email="test2@mail.de")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_POST_invalid_data(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@mail.de",
                "password": "SecurePass123!",
                "password_confirmation": "SecurePass",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(
            response, "The passwords you entered do not match. Please try again."
        )
        self.assertTrue(response.context["form"].errors)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.projects_url = reverse("projects")
        self.user = User.objects.create_user(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password="SecurePass123!",
            username="test@mail.de",
        )

    def test_GET(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_GET_authenticated(self):
        self.client.login(username="test@mail.de", password="SecurePass123!")

        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)

    def test_POST_valid_data(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "test@mail.de",
                "password": "SecurePass123!",
            },
        )

        user = User.objects.get(email="test@mail.de")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_POST_invalid_data(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "max@mail.de",
                "password": "SecurePass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, "This email address is not registered.")


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse("logout")
        self.login_url = reverse("login")
        self.user = User.objects.create_user(
            first_name="test_first_name",
            last_name="test_last_name",
            email="test@mail.de",
            password="SecurePass123!",
            username="test@mail.de",
        )
        self.client.login(username="test@mail.de", password="SecurePass123!")

    def test_GET(self):
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, 405)

    def test_POST(self):
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertNotIn("_auth_user_id", self.client.session)


class SendRegisterMailTest(TestCase):
    def test_send_register_email(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="securepassword",
            first_name="test_first_name",
            last_name="test_last_name",
        )

        factory = RequestFactory()
        request = factory.get("/")

        send_register_email(user, request)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]

        assert email.subject == "CANVAS: Registration Confirmation"
        assert email.to == ["test@example.com"]

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"confirm_deletion/{uid}/{token}/"

        assert expected_url_part in email.body


class ConfirmDeletionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@mail.de",
            password="SecurePass123!",
            first_name="test_first_name",
            last_name="test_last_name",
        )
        self.uid = urlsafe_base64_encode(str(self.user.id).encode())
        self.token = default_token_generator.make_token(self.user)
        self.confirm_deletion_url = reverse(
            "confirm_deletion", args=[self.uid, self.token]
        )

    def test_GET(self):
        response = self.client.get(self.confirm_deletion_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "confirm_deletion.html")

    def test_POST(self):
        response = self.client.post(self.confirm_deletion_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_POST_invalid_token(self):
        response = self.client.post(
            reverse("confirm_deletion", args=[self.uid, "invalid_token"])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invalid_link"))

    def test_POST_invalid_uid(self):
        response = self.client.post(
            reverse("confirm_deletion", args=["invalid_uid", self.token])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invalid_link"))


class SendPasswordChangeMailTest(TestCase):
    def test_send_password_change_email(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@mail.de",
            password="SecurePass123!",
            first_name="test_first_name",
            last_name="test_last_name",
        )

        factory = RequestFactory()
        request = factory.get("/")

        send_password_change_email(user, request)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]

        assert email.subject == "Password Change Confirmation"
        assert email.to == ["test@mail.de"]

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"password_reset/{uid}/{token}/"

        assert expected_url_part in email.body


class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@mail.de",
            password="SecurePass123!",
            first_name="test_first_name",
            last_name="test_last_name",
        )
        self.uid = urlsafe_base64_encode(str(self.user.id).encode())
        self.token = default_token_generator.make_token(self.user)
        self.password_reset_url = reverse("password_reset", args=[self.uid, self.token])

    def test_GET(self):
        response = self.client.get(self.password_reset_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_reset.html")

    def test_POST_valid_data(self):
        response = self.client.post(
            self.password_reset_url,
            {
                "new_password": "SecurePass1234!",
                "password_confirmation": "SecurePass1234!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("SecurePass1234!"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_POST_invalid_data(self):
        response = self.client.post(
            self.password_reset_url,
            {
                "new_password": "SecurePass1234!",
                "password_confirmation": "SecurePass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_reset.html")
        self.assertTrue(response.context["form"].errors)
        self.assertContains(
            response, "The passwords you entered do not match. Please try again."
        )

    def test_POST_invalid_token(self):
        response = self.client.post(
            reverse("password_reset", args=[self.uid, "invalid_token"])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invalid_link"))

    def test_POST_invalid_uid(self):
        response = self.client.post(
            reverse("password_reset", args=["invalid_uid", self.token])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invalid_link"))


class InvalidLinkTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.invalid_link_url = reverse("invalid_link")

    def test_GET(self):
        response = self.client.get(self.invalid_link_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invalid_link.html")

    def test_POST(self):
        response = self.client.post(self.invalid_link_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invalid_link.html")


class DeleteAccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test@mail.de",
            email="test@mail.de",
            password="SecurePass123!",
            first_name="test_first_name",
            last_name="test_last_name",
        )
        self.delete_account_url = reverse("delete_account")

    def test_GET(self):
        self.client.login(username="test@mail.de", password="SecurePass123!")
        response = self.client.get(self.delete_account_url)

        self.assertEqual(response.status_code, 405)

    def test_POST_valid_data(self):
        self.client.login(username="test@mail.de", password="SecurePass123!")
        response = self.client.post(
            self.delete_account_url,
            {"password": "SecurePass123!"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_POST_invalid_data(self):
        self.client.login(username="test@mail.de", password="SecurePass123!")
        response = self.client.post(
            self.delete_account_url,
            {"password": "SecurePass123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete_account.html")
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, "The password you entered is incorrect.")
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_POST_not_authenticated(self):
        response = self.client.post(
            self.delete_account_url,
            {"password": "SecurePass123!"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/delete_account/")
