from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


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
