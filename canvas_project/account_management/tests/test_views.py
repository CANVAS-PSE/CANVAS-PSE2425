from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.test.client import RequestFactory
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from account_management.views import (
    send_register_email,
    send_password_change_email,
    send_password_forgotten_email,
)
from django.contrib.messages import get_messages
from account_management.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from project_management.models import Project
from PIL import Image
import io
import os
import json
from allauth.socialaccount.models import SocialAccount


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
        # Test if the register page is accessible via GET request
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_GET_authenticated(self):
        # Test if an authenticated user is redirected to the projects page when accessing the register page
        self.client.login(username="test@mail.de", password="SecurePass123!")

        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)

    def test_POST_valid_data(self):
        # Test if a new user can successfully register and is redirected to the projects page
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
        )
        user = User.objects.get(email="test2@mail.de")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_POST_invalid_data(self):
        # Test if invalid registration data (mismatched passwords) results in an error message
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
        # Test if the login page is accessible via GET request
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_GET_authenticated(self):
        # Test if an authenticated user is redirected to the projects page when accessing the login page
        self.client.login(username="test@mail.de", password="SecurePass123!")

        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)

    def test_POST_valid_data(self):
        # Test if a valid user can successfully log in and is redirected to the projects page
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
        # Test if an invalid login attempt (wrong email) results in an error message
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
        # Test if a GET request to the logout endpoint returns a 405 (Method Not Allowed) as it should only accept POST requests
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, 405)

    def test_POST(self):
        # Test if a user can successfully log out and is redirected to the login page
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertNotIn("_auth_user_id", self.client.session)


class SendRegisterMailTest(TestCase):
    def test_send_register_email(self):
        # Test if the registration email is sent correctly
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

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert (
            email.subject == "CANVAS: Registration Confirmation"
        )  # Verify email subject
        assert email.to == ["test@example.com"]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"confirm_deletion/{uid}/{token}/"

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


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
        # Test if the confirmation page is accessible via GET request
        response = self.client.get(self.confirm_deletion_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "confirm_deletion.html")

    def test_POST(self):
        # Test if a valid POST request deletes the user and redirects to login page
        response = self.client.post(self.confirm_deletion_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_POST_invalid_token(self):
        # Test if an invalid token results in a redirect to the invalid link page
        response = self.client.post(
            reverse("confirm_deletion", args=[self.uid, "invalid_token"])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invalid_link"))

    def test_POST_invalid_uid(self):
        # Test if an invalid UID results in a redirect to the invalid link page
        response = self.client.post(
            reverse("confirm_deletion", args=["invalid_uid", self.token])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invalid_link"))


class SendPasswordChangeMailTest(TestCase):
    def test_send_password_change_email(self):
        # Test if a password change email is sent correctly
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

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert email.subject == "Password Change Confirmation"  # Verify email subject
        assert email.to == ["test@mail.de"]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"password_reset/{uid}/{token}/"

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


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
        # Test if the password reset page is accessible via GET request
        response = self.client.get(self.password_reset_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_reset.html")

    def test_POST_valid_data(self):
        # Test if a valid password reset request updates the password and logs the user out
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
        # Test if submitting mismatched passwords returns an error message
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
        # Test if an invalid token results in a redirect to the invalid link page
        response = self.client.post(
            reverse("password_reset", args=[self.uid, "invalid_token"])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("invalid_link"))

    def test_POST_invalid_uid(self):
        # Test if an invalid UID results in a redirect to the invalid link page
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
        # Test if the invalid link page is accessible via GET request
        response = self.client.get(self.invalid_link_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invalid_link.html")

    def test_POST(self):
        # Test if the invalid link page is accessible via POST
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
        # Test if a GET request to the delete account endpoint returns a 405 (Method Not Allowed), as it should only accept POST requests
        self.client.login(username="test@mail.de", password="SecurePass123!")
        response = self.client.get(self.delete_account_url)

        self.assertEqual(response.status_code, 405)

    def test_POST_valid_data(self):
        # Test if a valid delete account request removes the user and redirects to login page
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
        # Test if an incorrect password prevents account deletion
        self.client.login(username="test@mail.de", password="SecurePass123!")
        response = self.client.post(
            self.delete_account_url,
            {"password": "SecurePass123"},
        )

        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "The password you entered is incorrect." in str(msg) for msg in messages
            )
        )
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_POST_not_authenticated(self):
        # Test if an unauthenticated user is redirected to the login page
        response = self.client.post(
            self.delete_account_url,
            {"password": "SecurePass123!"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/delete_account/")


class PasswordForgottenViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test@mail.de",
            email="test@mail.de",
            password="SecurePass123!",
            first_name="test_first_name",
            last_name="test_last_name",
        )
        self.password_forgotten_url = reverse("password_forgotten")

    def test_GET(self):
        # Test if the password forgotten page is accessible via GET request
        response = self.client.get(self.password_forgotten_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_forgotten.html")

    def test_POST_valid_data(self):
        # Test if a valid email submission redirects to login page
        response = self.client.post(
            self.password_forgotten_url,
            {"email": "test@mail.de"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_POST_invalid_data(self):
        # Test if submitting an unregistered email returns an error message
        response = self.client.post(
            self.password_forgotten_url,
            {"email": "test2@mail.de"},
        )

        self.assertEqual(response.status_code, 302)
        assert len(mail.outbox) == 0


class SendPasswordForgottenMailTest(TestCase):
    def test_send_password_forgotten_email(self):
        # Test if the password forgotten email is sent correctly
        user = User.objects.create_user(
            username="test@mail.de",
            email="test@mail.de",
            password="SecurePass123!",
            first_name="test_first_name",
            last_name="test_last_name",
        )

        factory = RequestFactory()
        request = factory.get("/")

        send_password_forgotten_email(user, request)

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert email.subject == "Password Reset"  # Verify email subject
        assert email.to == ["test@mail.de"]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"password_reset/{uid}/{token}/"

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


class UpdateAccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test@mail.de",
            email="test@mail.de",
            password="SecurePass123!",
            first_name="test_first_name",
            last_name="test_last_name",
        )
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.update_account_url = reverse("update_account")

    def test_GET(self):
        # Test if a GET request to the delete account endpoint returns a 405 (Method Not Allowed), as it should only accept POST requests
        response = self.client.get(self.update_account_url)

        self.assertEqual(response.status_code, 405)

    def test_POST_not_authenticated(self):
        # Attempting to update an account without authentication should redirect to the login page
        response = self.client.post(
            self.update_account_url,
            {
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "new_test@mail.de",
                "old_password": "SecurePass123!",
                "new_password": "NewSecurePassword123!",
                "password_confirmation": "NewSecurePassword123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/update_account/")

    def test_POST_valid_data_without_profile(self):
        # Test if a user can successfully update their account information
        self.client.login(username="test@mail.de", password="SecurePass123!")

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "new_test@mail.de",
                "old_password": "SecurePass123!",
                "new_password": "NewSecurePassword123!",
                "password_confirmation": "NewSecurePassword123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "new_first_name")
        self.assertEqual(self.user.last_name, "new_last_name")
        self.assertTrue(self.user.check_password("NewSecurePassword123!"))
        self.assertEqual(self.user.email, "new_test@mail.de")
        self.assertEqual(self.user.username, "new_test@mail.de")

    def test_POST_invalid_data(self):
        # Attempting to update with an email that is already in use should fail
        User.objects.create_user(
            username="test2@mail.de",
            email="test2@mail.de",
            password="SecurePass123!",
            first_name="test2_first_name",
            last_name="test2_last_name",
        )
        self.client.login(username="test@mail.de", password="SecurePass123!")

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test2@mail.de",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "test_first_name")
        self.assertEqual(self.user.last_name, "test_last_name")
        self.assertEqual(self.user.email, "test@mail.de")
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "This email address is already in use. Please try another." in str(msg)
                for msg in messages
            )
        )

    def test_POST_From_projects_page(self):
        # Ensuring the user is redirected back to the projects page after updating their account
        self.client.login(username="test@mail.de", password="SecurePass123!")

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
            },
            HTTP_REFERER="/projects/",
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/projects/")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "new_first_name")
        self.assertEqual(self.user.last_name, "new_last_name")
        self.assertEqual(self.user.email, "test@mail.de")
        self.assertTrue(self.user.check_password("SecurePass123!"))

    def test_POST_from_editor_page(self):
        # Ensuring the user is redirected back to the editor page after updating their account
        self.client.login(username="test@mail.de", password="SecurePass123!")

        project = Project.objects.create(
            name="test_project",
            owner=self.user,
        )
        editor_url = reverse("editor", args=[project.name])

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
            },
            HTTP_REFERER=editor_url,
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, editor_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "new_first_name")
        self.assertEqual(self.user.last_name, "new_last_name")
        self.assertEqual(self.user.email, "test@mail.de")

    def test_POST_upload_profile_picture(self):
        # Uploading a profile picture and verifying that it is saved correctly
        self.client.login(username="test@mail.de", password="SecurePass123!")

        # create example picture
        image = Image.new("RGB", (100, 100), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        profile_picture = SimpleUploadedFile(
            "profile_picture.jpg", image_file.read(), content_type="image/jpeg"
        )

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "email": "test@mail.de",
                "old_password": "SecurePass123!",
                "new_password": "NewSecurePassword123!",
                "password_confirmation": "NewSecurePassword123!",
                "profile_picture": profile_picture,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()

        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_picture)
        expected_path = f"users/{self.user.id}/profile_picture"
        self.assertTrue(self.profile.profile_picture.name.startswith(expected_path))

    def test_update_profile_picture_replaces_old_one(self):
        # Test if the old profile picture is deleted when a new one is uploaded
        self.client.login(username="test@mail.de", password="SecurePass123!")

        # First profile picture upload
        image1 = Image.new("RGB", (100, 100), color="blue")
        image_file1 = io.BytesIO()
        image1.save(image_file1, format="JPEG")
        image_file1.seek(0)
        profile_picture1 = SimpleUploadedFile(
            "old_profile_picture.jpg", image_file1.read(), content_type="image/jpeg"
        )

        self.profile.profile_picture = profile_picture1
        self.profile.save()

        first_picture_path = f"users/{self.user.id}/old_profile_picture"
        self.assertTrue(
            self.profile.profile_picture.name.startswith(first_picture_path)
        )

        # Second profile picture upload
        image2 = Image.new("RGB", (100, 100), color="red")
        image_file2 = io.BytesIO()
        image2.save(image_file2, format="JPEG")
        image_file2.seek(0)
        new_profile_picture = SimpleUploadedFile(
            "new_profile_picture.jpg", image_file2.read(), content_type="image/jpeg"
        )

        response2 = self.client.post(
            self.update_account_url,
            {
                "profile_picture": new_profile_picture,
            },
        )

        self.assertEqual(response2.status_code, 302)
        self.profile.refresh_from_db()

        # Verify the new image was saved
        first_picture_path = f"users/{self.user.id}/new_profile_picture"
        self.assertTrue(
            self.profile.profile_picture.name.startswith(first_picture_path)
        )
        # Verify the old image was deleted
        self.assertFalse(os.path.exists(first_picture_path))

    def test_POST_delete_profile_picture(self):
        # Test if a user can delete their profile picture
        self.client.login(username="test@mail.de", password="SecurePass123!")

        image = Image.new("RGB", (100, 100), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        profile_picture = SimpleUploadedFile(
            "profile_picture.jpg", image_file.read(), content_type="image/jpeg"
        )

        self.profile.profile_picture = profile_picture
        self.profile.save()

        expected_path = f"users/{self.user.id}/profile_picture"
        self.assertTrue(self.profile.profile_picture.name.startswith(expected_path))

        response = self.client.post(
            self.update_account_url,
            {
                "delete_picture": "1",  # Setze das Profilbild auf den Standardwert
            },
        )

        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()

        # Verify profile picture is default picture
        self.assertEqual(self.profile.profile_picture.name, "profile_pics/default.jpg")

        # Verify the old image was deleted
        self.assertFalse(os.path.exists(expected_path))


class GetUserInfoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@mail.de", password="SecurePass123!"
        )
        self.get_user_info_url = reverse("get_user_info")

    def test_get_user_info_not_authenticated(self):
        # Unauthenticated users should be redirected to the login page.
        response = self.client.get(self.get_user_info_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/"))

    def test_get_user_info_authenticated_without_socialaccount(self):
        # A regular authenticated user without a SocialAccount should receive `is_openid_user: False`.
        self.client.login(username="testuser", password="SecurePass123!")
        response = self.client.get(self.get_user_info_url)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["is_openid_user"])

    def test_get_user_info_authenticated_with_socialaccount(self):
        # A user with a SocialAccount should receive `is_openid_user: True`.
        self.client.login(username="testuser", password="SecurePass123!")
        SocialAccount.objects.create(user=self.user, provider="google")

        response = self.client.get(self.get_user_info_url)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["is_openid_user"])
