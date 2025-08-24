import io
import json
import os

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from PIL import Image

from account_management.models import UserProfile
from canvas.test_constants import (
    CHECKBOX_TRUE,
    COMPLETELY_WRONG_PASSWORD,
    DELETE_PICTURE_FIELD,
    MISMATCHED_BUT_CORRECT_PASSWORD,
    NEW_PROFILE_PICTURE_JPG,
    NEW_PROFILE_PICTURE_SURFIX,
    NO_SPECIAL_CHAR_PASSWORD,
    OLD_PROFILE_PICTURE_JPG,
    OLD_PROFILE_PICTURE_SURFIX,
    PROFILE_PIC_FIELD,
    PROFILE_PIC_PREFIX,
    PROFILE_PIC_SURFIX,
    RESET_PASSWORD,
    SECURE_PASSWORD,
    TEST_PROJECT_NAME,
    UPDATED_PASSWORD,
    TEST_EMAIL_2,
    TEST_USERNAME,
    TEST_FIRST_NAME,
    TEST_LAST_NAME,
    TEST_FIRST_NAME_2,
    TEST_LAST_NAME_2,
    TEST_EMAIL_3,
    NEW_FIRST_NAME,
    NEW_LAST_NAME,
    NEW_EMAIL,
    TEST_PROFILE_PICTURE,
)
from account_management.views import (
    send_password_change_email,
    send_password_forgotten_email,
    send_register_email,
)
from canvas import path_dict, view_name_dict, message_dict, template_dict
from project_management.models import Project


class ParameterizedViewTestMixin:
    """
    Mixin class to provide parameterized testing capabilities for views.
    """

    def assert_view_get(self, url_name, template, expected_status=200):
        response = self.client.get(url_name)
        self.assertEqual(response.status_code, expected_status)
        self.assertTemplateUsed(response, template)

    # Test if an authenticated user is redirected to the projects page when accessing the register/login page
    def GET_authenticated(self, url_namee):
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)
        response = self.client.get(url_namee)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)


class RegisterViewTests(ParameterizedViewTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse(view_name_dict.register_view)
        self.projects_url = reverse(view_name_dict.projects_view)
        self.user = User.objects.create_user(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            username=TEST_EMAIL_2,
        )
        self.valid_user_data = {
            "first_name": TEST_FIRST_NAME_2,
            "last_name": TEST_LAST_NAME_2,
            "email": TEST_EMAIL_3,
            "password": SECURE_PASSWORD,
            "password_confirmation": SECURE_PASSWORD,
        }

    def test_GET(self):
        self.assert_view_get(self.register_url, template_dict.register_template)

    def test_GET_authenticated(self):
        # Test if an authenticated user is redirected to the projects page when accessing the register page
        self.GET_authenticated(self.register_url)

    def test_POST_valid_data(self):
        # Test if a new user can successfully register and is redirected to the projects page
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
        )
        user = User.objects.get(email=TEST_EMAIL_3)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_POST_invalid_data(self):
        # Test if invalid registration data (mismatched passwords) results in an error message
        response = self.client.post(
            self.register_url,
            {
                "first_name": TEST_FIRST_NAME,
                "last_name": TEST_LAST_NAME,
                "email": TEST_EMAIL_2,
                "password": SECURE_PASSWORD,
                "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_dict.register_template)
        self.assertContains(response, message_dict.password_match_criterium_text)
        self.assertTrue(response.context["form"].errors)


class LoginViewTest(ParameterizedViewTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse(view_name_dict.login_view)
        self.projects_url = reverse(view_name_dict.projects_view)
        self.user = User.objects.create_user(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            username=TEST_EMAIL_2,
        )

    def test_GET(self):
        # Test if the login page is accessible via GET request
        self.assert_view_get(self.login_url, template_dict.login_template)

    def test_GET_authenticated(self):
        # Test if an authenticated user is redirected to the projects page when accessing the login page
        self.GET_authenticated(self.login_url)

    def test_POST_valid_data(self):
        # Test if a valid user can successfully log in and is redirected to the projects page
        response = self.client.post(
            self.login_url,
            {
                "email": TEST_EMAIL_2,
                "password": SECURE_PASSWORD,
            },
        )

        user = User.objects.get(email=TEST_EMAIL_2)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_url)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_POST_invalid_data(self):
        # Test if an invalid login attempt (wrong email) results in an error message
        response = self.client.post(
            self.login_url,
            {
                "email": TEST_EMAIL_3,
                "password": SECURE_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_dict.login_template)
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, message_dict.email_not_registered_text)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse(view_name_dict.logout_view)
        self.login_url = reverse(view_name_dict.login_view)
        self.user = User.objects.create_user(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            username=TEST_EMAIL_2,
        )
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)

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
            username=TEST_USERNAME,
            email=TEST_EMAIL_2,
            password=COMPLETELY_WRONG_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )

        factory = RequestFactory()
        request = factory.get("/")

        send_register_email(user, request)

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert (
            email.subject == message_dict.registration_confirmation_subject
        )  # Verify email subject
        assert email.to == [TEST_EMAIL_2]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = reverse(
            view_name_dict.confirm_deletion_view, args=[uid, token]
        )

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


class ConfirmDeletionTest(ParameterizedViewTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.uid = urlsafe_base64_encode(str(self.user.id).encode())
        self.token = default_token_generator.make_token(self.user)
        self.confirm_deletion_url = reverse(
            view_name_dict.confirm_deletion_view, args=[self.uid, self.token]
        )

    def test_GET(self):
        # Test if the confirm deletion page is accessible via GET request
        self.assert_view_get(
            self.confirm_deletion_url, template_dict.confirm_deletion_template
        )

    def test_POST(self):
        # Test if a valid POST request deletes the user and redirects to login page
        response = self.client.post(self.confirm_deletion_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(view_name_dict.login_view))
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_POST_invalid_token(self):
        # Test if an invalid token results in a redirect to the invalid link page
        response = self.client.post(
            reverse(
                view_name_dict.confirm_deletion_view,
                args=[self.uid, view_name_dict.invalid_token_view],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(view_name_dict.invalid_link_view))

    def test_POST_invalid_uid(self):
        # Test if an invalid UID results in a redirect to the invalid link page
        response = self.client.post(
            reverse(
                view_name_dict.confirm_deletion_view,
                args=[view_name_dict.invalid_uid_view, self.token],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(view_name_dict.invalid_link_view))


class SendPasswordChangeMailTest(TestCase):
    def test_send_password_change_email(self):
        # Test if a password change email is sent correctly
        user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )

        factory = RequestFactory()
        request = factory.get("/")

        send_password_change_email(user, request)

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert (
            email.subject == message_dict.password_change_confirmation_subject
        )  # Verify email subject
        assert email.to == [TEST_EMAIL_2]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = reverse(
            view_name_dict.password_reset_view, args=[uid, token]
        )

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


class PasswordResetViewTest(ParameterizedViewTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.uid = urlsafe_base64_encode(str(self.user.id).encode())
        self.token = default_token_generator.make_token(self.user)
        self.password_reset_url = reverse(
            view_name_dict.password_reset_view, args=[self.uid, self.token]
        )

    def test_GET(self):
        # Test if the password reset page is accessible via GET request
        self.assert_view_get(
            self.password_reset_url, template_dict.password_reset_template
        )

    def test_POST_valid_data(self):
        # Test if a valid password reset request updates the password and logs the user out
        response = self.client.post(
            self.password_reset_url,
            {
                "new_password": RESET_PASSWORD,
                "password_confirmation": RESET_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(view_name_dict.login_view))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(RESET_PASSWORD))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_POST_invalid_data(self):
        # Test if submitting mismatched passwords returns an error message
        response = self.client.post(
            self.password_reset_url,
            {
                "new_password": RESET_PASSWORD,
                "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_dict.password_reset_template)
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, message_dict.password_match_criterium_text)

    def test_POST_invalid_token(self):
        # Test if an invalid token results in a redirect to the invalid link page
        response = self.client.post(
            reverse(
                view_name_dict.password_reset_view,
                args=[self.uid, view_name_dict.invalid_token_view],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(view_name_dict.invalid_link_view))

    def test_POST_invalid_uid(self):
        # Test if an invalid UID results in a redirect to the invalid link page
        response = self.client.post(
            reverse(
                view_name_dict.password_reset_view,
                args=[view_name_dict.invalid_uid_view, self.token],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(view_name_dict.invalid_link_view))


class InvalidLinkTest(ParameterizedViewTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.invalid_link_url = reverse(view_name_dict.invalid_link_view)

    def test_GET(self):
        # Test if the invalid link page is accessible via GET request
        self.assert_view_get(self.invalid_link_url, template_dict.invalid_link_template)

    def test_POST(self):
        # Test if the invalid link page is accessible via POST
        response = self.client.post(self.invalid_link_url)

        self.assertEqual(response.status_code, 405)


class DeleteAccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.delete_account_url = reverse(view_name_dict.delete_account_view)

    def test_GET(self):
        # Test if a GET request to the delete account endpoint returns a 405 (Method Not Allowed), as it should only accept POST requests
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)
        response = self.client.get(self.delete_account_url)

        self.assertEqual(response.status_code, 405)

    def test_POST_valid_data(self):
        # Test if a valid delete account request removes the user and redirects to login page
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)
        response = self.client.post(
            self.delete_account_url,
            {"password": SECURE_PASSWORD},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(view_name_dict.login_view))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_POST_invalid_data(self):
        # Test if an incorrect password prevents account deletion
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)
        response = self.client.post(
            self.delete_account_url,
            {"password": NO_SPECIAL_CHAR_PASSWORD},
        )

        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(message_dict.incorrect_password_text in str(msg) for msg in messages)
        )
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_POST_not_authenticated(self):
        # Test if an unauthenticated user is redirected to the login page
        response = self.client.post(
            self.delete_account_url,
            {"password": SECURE_PASSWORD},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/delete_account/")


class PasswordForgottenViewTest(ParameterizedViewTestMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.password_forgotten_url = reverse(view_name_dict.password_forgotten_view)

    def test_GET(self):
        # Test if the password forgotten page is accessible via GET request
        self.assert_view_get(
            self.password_forgotten_url,
            template_dict.password_forgotten_template,
        )

    def test_POST_valid_data(self):
        # Test if a valid email submission redirects to login page
        response = self.client.post(
            self.password_forgotten_url,
            {"email": TEST_EMAIL_2},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(view_name_dict.login_view))

    def test_POST_invalid_data(self):
        # Test if submitting an unregistered email returns an error message
        response = self.client.post(
            self.password_forgotten_url,
            {"email": TEST_EMAIL_3},
        )

        self.assertEqual(response.status_code, 302)
        assert len(mail.outbox) == 0


class SendPasswordForgottenMailTest(TestCase):
    def test_send_password_forgotten_email(self):
        # Test if the password forgotten email is sent correctly
        user = User.objects.create_user(
            username=TEST_EMAIL_2,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )

        factory = RequestFactory()
        request = factory.get("/")

        send_password_forgotten_email(user, request)

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert (
            email.subject == message_dict.password_reset_confirmation_subject
        )  # Verify email subject
        assert email.to == [TEST_EMAIL_2]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = reverse(
            view_name_dict.password_reset_view, args=[uid, token]
        )

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


class UpdateAccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            email=TEST_EMAIL_2,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.update_account_url = reverse(view_name_dict.update_account_view)

    def test_GET(self):
        # Test if a GET request to the delete account endpoint returns a 405 (Method Not Allowed), as it should only accept POST requests
        response = self.client.get(self.update_account_url)

        self.assertEqual(response.status_code, 405)

    def test_POST_not_authenticated(self):
        # Attempting to update an account without authentication should redirect to the login page
        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": NEW_EMAIL,
                "old_password": SECURE_PASSWORD,
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": UPDATED_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/update_account/")

    def test_POST_valid_data_without_profile(self):
        # Test if a user can successfully update their account information
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": NEW_EMAIL,
                "old_password": SECURE_PASSWORD,
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": UPDATED_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, NEW_FIRST_NAME)
        self.assertEqual(self.user.last_name, NEW_LAST_NAME)
        self.assertTrue(self.user.check_password(UPDATED_PASSWORD))
        self.assertEqual(self.user.email, NEW_EMAIL)
        self.assertEqual(self.user.username, NEW_EMAIL)

    def test_POST_invalid_data(self):
        # Attempting to update with an email that is already in use should fail
        User.objects.create_user(
            username=TEST_EMAIL_3,
            email=TEST_EMAIL_3,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME_2,
            last_name=TEST_LAST_NAME_2,
        )
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_3,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, TEST_FIRST_NAME)
        self.assertEqual(self.user.last_name, TEST_LAST_NAME)
        self.assertEqual(self.user.email, TEST_EMAIL_2)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(message_dict.email_already_in_use_text in str(msg) for msg in messages)
        )

    def test_POST_From_projects_page(self):
        # Ensuring the user is redirected back to the projects page after updating their account
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_2,
            },
            HTTP_REFERER="/projects/",
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/projects/")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, NEW_FIRST_NAME)
        self.assertEqual(self.user.last_name, NEW_LAST_NAME)
        self.assertEqual(self.user.email, TEST_EMAIL_2)
        self.assertTrue(self.user.check_password(SECURE_PASSWORD))

    def test_POST_from_editor_page(self):
        # Ensuring the user is redirected back to the editor page after updating their account
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)

        project = Project.objects.create(
            name=TEST_PROJECT_NAME,
            owner=self.user,
        )
        editor_url = reverse(view_name_dict.editor_view, args=[project.name])

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_2,
            },
            HTTP_REFERER=editor_url,
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, editor_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, NEW_FIRST_NAME)
        self.assertEqual(self.user.last_name, NEW_LAST_NAME)
        self.assertEqual(self.user.email, TEST_EMAIL_2)

    def test_POST_upload_profile_picture(self):
        # Uploading a profile picture and verifying that it is saved correctly
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)

        # create example picture
        image = Image.new("RGB", (100, 100), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        profile_picture = SimpleUploadedFile(
            TEST_PROFILE_PICTURE, image_file.read(), content_type="image/jpeg"
        )

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_FIRST_NAME,
                "last_name": NEW_LAST_NAME,
                "email": TEST_EMAIL_2,
                "old_password": SECURE_PASSWORD,
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": UPDATED_PASSWORD,
                "profile_picture": profile_picture,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()

        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_picture)
        expected_path = f"{PROFILE_PIC_PREFIX}/{self.user.id}/{PROFILE_PIC_SURFIX}"
        self.assertTrue(self.profile.profile_picture.name.startswith(expected_path))

    def test_update_profile_picture_replaces_old_one(self):
        # Test if the old profile picture is deleted when a new one is uploaded
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)

        # First profile picture upload
        image1 = Image.new("RGB", (100, 100), color="blue")
        image_file1 = io.BytesIO()
        image1.save(image_file1, format="JPEG")
        image_file1.seek(0)
        profile_picture1 = SimpleUploadedFile(
            OLD_PROFILE_PICTURE_JPG, image_file1.read(), content_type="image/jpeg"
        )

        self.profile.profile_picture = profile_picture1
        self.profile.save()

        first_picture_path = (
            f"{PROFILE_PIC_PREFIX}/{self.user.id}/{OLD_PROFILE_PICTURE_SURFIX}"
        )
        self.assertTrue(
            self.profile.profile_picture.name.startswith(first_picture_path)
        )

        # Second profile picture upload
        image2 = Image.new("RGB", (100, 100), color="red")
        image_file2 = io.BytesIO()
        image2.save(image_file2, format="JPEG")
        image_file2.seek(0)
        new_profile_picture = SimpleUploadedFile(
            NEW_PROFILE_PICTURE_JPG, image_file2.read(), content_type="image/jpeg"
        )

        response2 = self.client.post(
            self.update_account_url,
            {
                PROFILE_PIC_FIELD: new_profile_picture,
            },
        )

        self.assertEqual(response2.status_code, 302)
        self.profile.refresh_from_db()

        # Verify the new image was saved
        first_picture_path = (
            f"{PROFILE_PIC_PREFIX}/{self.user.id}/{NEW_PROFILE_PICTURE_SURFIX}"
        )
        self.assertTrue(
            self.profile.profile_picture.name.startswith(first_picture_path)
        )
        # Verify the old image was deleted
        self.assertFalse(os.path.exists(first_picture_path))

    def test_POST_delete_profile_picture(self):
        # Test if a user can delete their profile picture
        self.client.login(username=TEST_EMAIL_2, password=SECURE_PASSWORD)

        image = Image.new("RGB", (100, 100), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        profile_picture = SimpleUploadedFile(
            TEST_PROFILE_PICTURE, image_file.read(), content_type="image/jpeg"
        )

        self.profile.profile_picture = profile_picture
        self.profile.save()

        expected_path = f"{PROFILE_PIC_PREFIX}/{self.user.id}/{PROFILE_PIC_SURFIX}"
        self.assertTrue(self.profile.profile_picture.name.startswith(expected_path))

        response = self.client.post(
            self.update_account_url,
            {
                DELETE_PICTURE_FIELD: CHECKBOX_TRUE,  # Setze das Profilbild auf den Standardwert
            },
        )

        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()

        # Verify profile picture is default picture
        self.assertEqual(
            self.profile.profile_picture.name, path_dict.default_profil_pic
        )

        # Verify the old image was deleted
        self.assertFalse(os.path.exists(expected_path))


class GetUserInfoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_USERNAME, email=TEST_EMAIL_2, password=SECURE_PASSWORD
        )
        self.get_user_info_url = reverse(view_name_dict.get_user_info_view)

    def test_get_user_info_not_authenticated(self):
        # Unauthenticated users should be redirected to the login page.
        response = self.client.get(self.get_user_info_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/"))

    def test_get_user_info_authenticated_without_socialaccount(self):
        # A regular authenticated user without a SocialAccount should receive `is_openid_user: False`.
        self.client.login(username=TEST_USERNAME, password=SECURE_PASSWORD)
        response = self.client.get(self.get_user_info_url)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["is_openid_user"])

    def test_get_user_info_authenticated_with_socialaccount(self):
        # A user with a SocialAccount should receive `is_openid_user: True`.
        self.client.login(username=TEST_USERNAME, password=SECURE_PASSWORD)
        SocialAccount.objects.create(user=self.user, provider="google")

        response = self.client.get(self.get_user_info_url)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["is_openid_user"])
