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
from account_management.tests.test_constants import (
    COMPLETELY_WRONG_PASSWORD,
    MAX_EMAIL,
    MISMATCHED_BUT_CORRECT_PASSWORD,
    NEW_TEST_EMAIL,
    NEW_TEST_FIRST_NAME,
    NEW_TEST_LAST_NAME,
    NO_SPECIAL_CHAR_PASSWORD,
    RESET_PASSWORD,
    SECURE_PASSWORD,
    TEST3_EMAIL,
    TEST_USERNAME,
    UPDATED_PASSWORD,
    TEST_EMAIL,
    TEST_FIRST_NAME,
    TEST_LAST_NAME,
    TEST2_EMAIL,
    TEST2_FIRST_NAME,
    TEST2_LAST_NAME,
)
from account_management.views import (
    send_password_change_email,
    send_password_forgotten_email,
    send_register_email,
)
from canvas import path_dict, view_name_dict, message_dict
from project_management.models import Project


class ParameterizedViewTestMixin:
    """
    Mixin class to provide parameterized testing capabilities for views.
    """

    def assert_view_get(self, url_name, template, expected_status=200):
        """
        Assert that a GET request to the specified URL returns the expected status code and template.
        """
        response = self.get_and_assert(url_name, expected_status)
        self.assertTemplateUsed(response, template)

    def GET_authenticated(self, url_name):
        """
        Simulate an authenticated user accessing a view.
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)
        response = self.get_and_assert_redirect(url_name, 302, self.projects_url)
        return response

    def POST_valid_data_with_user(self, post_url, post_data, redirect_url):
        """
        Simulate a POST request with valid data and an authenticated user.
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)
        response = self.client.post(post_url, post_data)
        user = User.objects.get(email=TEST_EMAIL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def post_and_assert(self, url_name, post_data=None, expected_status=200):
        """
        Assert that a POST request to the specified URL returns the expected status code.
        """
        response = self.client.post(url_name, data=post_data or {})
        self.assertEqual(response.status_code, expected_status)
        return response

    def get_and_assert(self, url_name, expected_status=200):
        """
        Assert that a GET request to the specified URL returns the expected status code.
        """
        response = self.client.get(url_name)
        self.assertEqual(response.status_code, expected_status)
        return response

    def get_and_assert_redirect(self, url_name, expected_status, redirect_to):
        """
        Assert that a GET request to the specified URL returns a redirect to the expected URL.
        """
        response = self.get_and_assert(url_name, expected_status)
        self.assertRedirects(response, reverse(redirect_to))
        return response

    def post_and_assert_redirect(
        self, url_name, post_data=None, expected_status=302, redirect_to=None
    ):
        """
        Assert that a POST request to the specified URL returns a redirect to the expected URL.
        """
        response = self.post_and_assert(url_name, post_data, expected_status)
        self.assertRedirects(response, reverse(redirect_to))
        return response


class RegisterViewTests(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the registration view.
    This class inherits from ParameterizedViewTestMixin to provide common testing methods.
    """

    def setUp(self):
        """
        Set up the test environment for the registration view tests.
        This includes creating a test client, URLs, and a test user.
        """
        self.client = Client()
        self.register_url = reverse(view_name_dict.register_view)
        self.projects_url = reverse(view_name_dict.projects_view)
        self.user = User.objects.create_user(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            username=TEST_EMAIL,
        )
        self.valid_user_data = {
            "first_name": TEST2_FIRST_NAME,
            "last_name": TEST2_LAST_NAME,
            "email": TEST2_EMAIL,
            "password": SECURE_PASSWORD,
            "password_confirmation": SECURE_PASSWORD,
        }

    def test_GET(self):
        """
        Test if the registration page is accessible via GET request.
        """
        self.assert_view_get(self.register_url, path_dict.register_template)

    def test_GET_authenticated(self):
        """
        Test if an authenticated user is redirected to the projects page when accessing the register page
        """
        self.GET_authenticated(self.register_url)

    def test_POST_valid_data(self):
        """
        Test if a new user can successfully register and is redirected to the projects page
        """
        self.POST_valid_data_with_user(
            self.register_url, self.valid_user_data, self.projects_url
        )

    def test_POST_invalid_data(self):
        """
        Test if invalid registration data (e.g., already registered email) results in an error message
        """
        post_data = {
            "first_name": TEST_FIRST_NAME,
            "last_name": TEST_LAST_NAME,
            "email": TEST_EMAIL,
            "password": SECURE_PASSWORD,
            "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
        }
        response = self.post_and_assert(
            self.register_url, post_data, expected_status=200
        )

        self.assertTemplateUsed(response, path_dict.register_template)
        self.assertContains(response, message_dict.password_match_criterium_text)
        self.assertTrue(response.context["form"].errors)


class LoginViewTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the login view.
    This class inherits from ParameterizedViewTestMixin to provide common testing methods.
    """

    def setUp(self):
        """
        Set up the test environment for the login view tests.
        """
        self.client = Client()
        self.login_url = reverse(view_name_dict.login_view)
        self.projects_url = reverse(view_name_dict.projects_view)
        self.user = User.objects.create_user(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            username=TEST_EMAIL,
        )

    def test_GET(self):
        """
        Test if the login page is accessible via GET request
        """
        self.assert_view_get(self.login_url, path_dict.login_template)

    def test_GET_authenticated(self):
        """
        Test if an authenticated user is redirected to the projects page when accessing the login page
        """
        self.GET_authenticated(self.login_url)

    def test_POST_valid_data(self):
        """
        Test if a valid user can successfully log in and is redirected to the projects page
        """
        post_data = {
            "email": TEST_EMAIL,
            "password": SECURE_PASSWORD,
        }
        self.POST_valid_data_with_user(self.login_url, post_data, self.projects_url)

    def test_POST_invalid_data(self):
        """
        Test if an invalid login attempt (wrong email) results in an error message
        """
        post_data = {
            "email": MAX_EMAIL,
            "password": SECURE_PASSWORD,
        }
        response = self.post_and_assert(self.login_url, post_data, expected_status=200)
        self.assertTemplateUsed(response, path_dict.login_template)
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, message_dict.email_not_registered_text)


class LogoutViewTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the logout view.
    This class inherits from ParameterizedViewTestMixin to provide common testing methods.
    """

    def setUp(self):
        """
        Set up the test environment for the logout view tests.
        """
        self.client = Client()
        self.logout_url = reverse(view_name_dict.logout_view)
        self.login_url = reverse(view_name_dict.login_view)
        self.user = User.objects.create_user(
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            username=TEST_EMAIL,
        )
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

    def test_GET(self):
        """
        Test if a GET request to the logout endpoint returns a 405 (Method Not Allowed) as it should only accept POST requests
        """
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, 405)

    def test_POST(self):
        """
        Test if a user can successfully log out and is redirected to the login page
        """
        response = self.post_and_assert(self.logout_url, expected_status=302)

        self.assertRedirects(response, self.login_url)
        self.assertNotIn("_auth_user_id", self.client.session)


class SendRegisterMailTest(TestCase):
    """
    Tests for the send_register_email function.
    """

    def test_send_register_email(self):
        """
        Test if the registration email is sent correctly
        """
        user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST3_EMAIL,
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
            email.subject == "CANVAS: Registration Confirmation"
        )  # Verify email subject
        assert email.to == [TEST3_EMAIL]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"confirm_deletion/{uid}/{token}/"

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


class ConfirmDeletionTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the confirm deletion view.
    This class inherits from ParameterizedViewTestMixin to provide common testing methods.
    """

    def setUp(self):
        """
        Set up the test environment for the confirm deletion view tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.uid = urlsafe_base64_encode(str(self.user.id).encode())
        self.token = default_token_generator.make_token(self.user)
        self.confirm_deletion_url = reverse(
            view_name_dict.confirm_deletion, args=[self.uid, self.token]
        )

    def test_GET(self):
        """
        Test if the confirm deletion page is accessible via GET request
        """
        self.assert_view_get(
            self.confirm_deletion_url, path_dict.confirm_deletion_template
        )

    def test_POST(self):
        """
        Test if a valid POST request deletes the user and redirects to login page
        """
        response = self.post_and_assert(self.confirm_deletion_url, expected_status=302)

        self.assertRedirects(response, reverse(view_name_dict.login_view))
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_POST_invalid_token(self):
        """
        Test if an invalid token results in a redirect to the invalid link page
        """
        self.post_and_assert_redirect(
            view_name_dict.confirm_deletion,
            [self.uid, view_name_dict.invalid_token],
            302,
            view_name_dict.invalid_link,
        )

    def test_POST_invalid_uid(self):
        """
        Test if an invalid UID results in a redirect to the invalid link page
        """
        post_url = reverse(
            view_name_dict.confirm_deletion_view,
            args=[[view_name_dict.invalid_uid_view, self.token], self.token],
        )
        self.post_and_assert_redirect(
            post_url,
            expected_status=302,
            redirect_to=reverse(view_name_dict.invalid_link),
        )


class SendPasswordChangeMailTest(TestCase):
    """
    Tests for sending password change emails.
    """

    def test_send_password_change_email(self):
        """
        Test if a password change email is sent correctly
        """
        user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )

        factory = RequestFactory()
        request = factory.get("/")

        send_password_change_email(user, request)

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert email.subject == "Password Change Confirmation"  # Verify email subject
        assert email.to == [TEST_EMAIL]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"password_reset/{uid}/{token}/"

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


class PasswordResetViewTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the password reset view.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
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
        """
        Test if the password reset page is accessible via GET request
        """
        self.assert_view_get(self.password_reset_url, path_dict.password_reset_template)

    def test_POST_valid_data(self):
        """
        Test if a valid password reset request updates the password and logs the user out
        """
        post_data = {
            "new_password": RESET_PASSWORD,
            "password_confirmation": RESET_PASSWORD,
        }

        self.post_and_assert_redirect(
            self.password_reset_url, post_data, 302, reverse(view_name_dict.login_view)
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(RESET_PASSWORD))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_POST_invalid_data(self):
        """
        Test if submitting mismatched passwords returns an error message
        """
        post_data = {
            "new_password": RESET_PASSWORD,
            "password_confirmation": MISMATCHED_BUT_CORRECT_PASSWORD,
        }

        response = self.post_and_assert(self.password_reset_url, post_data, 200)
        self.assertTemplateUsed(response, path_dict.password_reset_template)
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, message_dict.password_match_criterium_text)

    def test_POST_invalid_token(self):
        """
        Test if an invalid token results in a redirect to the invalid link page
        """
        self.post_and_assert_redirect(
            view_name_dict.password_reset_view,
            [self.uid, view_name_dict.invalid_token],
            302,
            view_name_dict.invalid_link_view,
        )

    def test_POST_invalid_uid(self):
        """
        Test if an invalid UID results in a redirect to the invalid link page
        """
        post_url = reverse(
            view_name_dict.password_reset_view,
            args=[view_name_dict.invalid_uid_view, self.token],
        )
        self.post_and_assert_redirect(
            post_url,
            expected_status=302,
            redirect_to=reverse(view_name_dict.invalid_link_view),
        )


class InvalidLinkTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the invalid link view.
    This class inherits from ParameterizedViewTestMixin to provide common testing methods.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.client = Client()
        self.invalid_link_url = reverse(view_name_dict.invalid_link_view)

    def test_GET(self):
        """
        Test if the invalid link page is accessible via GET request
        """
        self.assert_view_get(self.invalid_link_url, path_dict.invalid_link_template)

    def test_POST(self):
        """
        Test if the invalid link page is accessible via POST
        """
        self.post_and_assert(self.invalid_link_url, expected_status=405)


class DeleteAccountTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the delete account view.
    This class inherits from ParameterizedViewTestMixin to provide common testing methods.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_EMAIL,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.delete_account_url = reverse(view_name_dict.delete_account_view)

    def test_GET(self):
        """
        Test if a GET request to the delete account endpoint returns a 405 (Method Not Allowed), as it should only accept POST requests
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)
        response = self.client.get(self.delete_account_url)

        self.assertEqual(response.status_code, 405)

    def test_POST_valid_data(self):
        """
        Test if a valid delete account request removes the user and redirects to login page
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

        post_data = {"password": SECURE_PASSWORD}
        self.post_and_assert_redirect(
            self.delete_account_url, post_data, 302, reverse(view_name_dict.login_view)
        )
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_POST_invalid_data(self):
        """
        Test if an incorrect password prevents account deletion
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)
        post_data = {"password": NO_SPECIAL_CHAR_PASSWORD}
        response = self.post_and_assert(self.delete_account_url, post_data, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(message_dict.incorrect_password_text in str(msg) for msg in messages)
        )
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_POST_not_authenticated(self):
        """
        Test if an unauthenticated user is redirected to the login page
        """
        post_data = {"password": SECURE_PASSWORD}
        response = self.POST_not_authenticated(self.delete_account_url, post_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/delete_account/")


class PasswordForgottenViewTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the password forgotten view.
    This class inherits from ParameterizedViewTestMixin to provide common testing methods.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_EMAIL,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.password_forgotten_url = reverse(view_name_dict.password_forgotten_view)

    def test_GET(self):
        """
        Test if the password forgotten page is accessible via GET request
        """
        self.assert_view_get(
            self.password_forgotten_url,
            path_dict.password_forgotten_template,
        )

    def test_POST_valid_data(self):
        """
        Test if a valid email submission redirects to login page
        """
        post_data = {"email": TEST_EMAIL}

        self.post_and_assert_redirect(
            self.password_forgotten_url,
            post_data,
            302,
            reverse(view_name_dict.login_view),
        )

    def test_POST_invalid_data(self):
        """
        Test if submitting an unregistered email returns an error message
        """
        post_data = {"email": TEST2_EMAIL}
        self.post_and_assert(self.password_forgotten_url, post_data, 302)
        assert len(mail.outbox) == 0


class SendPasswordForgottenMailTest(TestCase):
    """
    Tests for sending password forgotten emails.
    """

    def test_send_password_forgotten_email(self):
        """
        Test if the password forgotten email is sent correctly
        """
        user = User.objects.create_user(
            username=TEST_EMAIL,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )

        factory = RequestFactory()
        request = factory.get("/")

        send_password_forgotten_email(user, request)

        assert len(mail.outbox) == 1  # Check if one email was sent
        email = mail.outbox[0]

        assert email.subject == "Password Reset"  # Verify email subject
        assert email.to == [TEST_EMAIL]  # Verify recipient

        uid = urlsafe_base64_encode(str(user.id).encode())
        token = default_token_generator.make_token(user)
        expected_url_part = f"password_reset/{uid}/{token}/"

        assert (
            expected_url_part in email.body
        )  # Ensure the confirmation URL is in the email body


class UpdateAccountTest(ParameterizedViewTestMixin, TestCase):
    """
    Tests for the update account view.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_EMAIL,
            email=TEST_EMAIL,
            password=SECURE_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.update_account_url = reverse(view_name_dict.update_account_view)

    def test_GET(self):
        """
        Test if a GET request to the update account endpoint returns a 200 status code.
        """
        response = self.client.get(self.update_account_url)

        self.assertEqual(response.status_code, 405)

    def test_POST_not_authenticated(self):
        """
        Test if a POST request to the update account endpoint without authentication redirects to the login page.
        """
        post_data = {
            "first_name": NEW_TEST_FIRST_NAME,
            "last_name": NEW_TEST_LAST_NAME,
            "email": NEW_TEST_EMAIL,
            "old_password": SECURE_PASSWORD,
            "new_password": UPDATED_PASSWORD,
            "password_confirmation": UPDATED_PASSWORD,
        }
        response = self.POST_not_authenticated(self.update_account_url, post_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/update_account/")

    def test_POST_valid_data_without_profile(self):
        """
        Test if a user can successfully update their account information without a profile
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_TEST_FIRST_NAME,
                "last_name": NEW_TEST_LAST_NAME,
                "email": NEW_TEST_EMAIL,
                "old_password": SECURE_PASSWORD,
                "new_password": UPDATED_PASSWORD,
                "password_confirmation": UPDATED_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, NEW_TEST_FIRST_NAME)
        self.assertEqual(self.user.last_name, NEW_TEST_LAST_NAME)
        self.assertTrue(self.user.check_password(UPDATED_PASSWORD))
        self.assertEqual(self.user.email, NEW_TEST_EMAIL)
        self.assertEqual(self.user.username, NEW_TEST_EMAIL)

    def test_POST_invalid_data(self):
        """
        Test if a user cannot update their account information with invalid data.
        """
        User.objects.create_user(
            username=TEST2_EMAIL,
            email=TEST2_EMAIL,
            password=SECURE_PASSWORD,
            first_name=TEST2_FIRST_NAME,
            last_name=TEST2_LAST_NAME,
        )
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

        post_data = {
            "first_name": NEW_TEST_FIRST_NAME,
            "last_name": NEW_TEST_LAST_NAME,
            "email": TEST2_EMAIL,
        }
        response = self.post_and_assert(self.update_account_url, post_data, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, NEW_TEST_FIRST_NAME)
        self.assertEqual(self.user.last_name, NEW_TEST_LAST_NAME)
        self.assertEqual(self.user.email, TEST_EMAIL)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(message_dict.email_already_in_use_text in str(msg) for msg in messages)
        )

    def test_POST_From_projects_page(self):
        """
        Test if a user is redirected back to the projects page after updating their account
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_TEST_FIRST_NAME,
                "last_name": NEW_TEST_LAST_NAME,
                "email": TEST_EMAIL,
            },
            HTTP_REFERER="/projects/",
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/projects/")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, NEW_TEST_FIRST_NAME)
        self.assertEqual(self.user.last_name, NEW_TEST_LAST_NAME)
        self.assertEqual(self.user.email, TEST_EMAIL)
        self.assertTrue(self.user.check_password(SECURE_PASSWORD))

    def test_POST_from_editor_page(self):
        """
        Test if a user is redirected back to the editor page after updating their account
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

        project = Project.objects.create(
            name="test_project",
            owner=self.user,
        )
        editor_url = reverse(view_name_dict.editor_view, args=[project.name])

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_TEST_FIRST_NAME,
                "last_name": NEW_TEST_LAST_NAME,
                "email": TEST_EMAIL,
            },
            HTTP_REFERER=editor_url,
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, editor_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, NEW_TEST_FIRST_NAME)
        self.assertEqual(self.user.last_name, NEW_TEST_LAST_NAME)
        self.assertEqual(self.user.email, TEST_EMAIL)

    def test_POST_upload_profile_picture(self):
        """
        Test if a user can upload a profile picture successfully.
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

        # create example picture
        image = Image.new("RGB", (100, 100), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        profile_picture = SimpleUploadedFile(
            path_dict.profile_picture_jpg,
            image_file.read(),
            content_type=path_dict.profile_picture_content_type,
        )

        response = self.client.post(
            self.update_account_url,
            {
                "first_name": NEW_TEST_FIRST_NAME,
                "last_name": NEW_TEST_LAST_NAME,
                "email": TEST_EMAIL,
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
        expected_path = f"users/{self.user.id}/profile_picture"
        self.assertTrue(self.profile.profile_picture.name.startswith(expected_path))

    def test_update_profile_picture_replaces_old_one(self):
        """
        Test if the old profile picture is deleted when a new one is uploaded
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

        # First profile picture upload
        image1 = Image.new("RGB", (100, 100), color="blue")
        image_file1 = io.BytesIO()
        image1.save(image_file1, format="JPEG")
        image_file1.seek(0)
        profile_picture1 = SimpleUploadedFile(
            path_dict.profile_picture_jpg,
            image_file1.read(),
            content_type=path_dict.profile_picture_content_type,
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
            path_dict.new_profile_picture_jpg,
            image_file2.read(),
            content_type=path_dict.profile_picture_content_type,
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
        """
        Test if a user can delete their profile picture
        """
        self.client.login(username=TEST_EMAIL, password=SECURE_PASSWORD)

        image = Image.new("RGB", (100, 100), color="blue")
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        profile_picture = SimpleUploadedFile(
            path_dict.profile_picture_jpg,
            image_file.read(),
            content_type=path_dict.profile_picture_content_type,
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
        self.assertEqual(
            self.profile.profile_picture.name, path_dict.default_profil_pic
        )

        # Verify the old image was deleted
        self.assertFalse(os.path.exists(expected_path))


class GetUserInfoTest(TestCase):
    """
    Tests for the get_user_info view.
    This view returns user information, including whether the user is an OpenID user.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_USERNAME, email=TEST_EMAIL, password=SECURE_PASSWORD
        )
        self.get_user_info_url = reverse("get_user_info")

    def test_get_user_info_not_authenticated(self):
        """
        Test if an unauthenticated user is redirected to the login page.
        """
        response = self.client.get(self.get_user_info_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/"))

    def test_get_user_info_authenticated_without_socialaccount(self):
        """
        Test if a regular authenticated user without a SocialAccount receives `is_openid_user: False`.
        """
        self.client.login(username="testuser", password=SECURE_PASSWORD)
        response = self.client.get(self.get_user_info_url)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["is_openid_user"])

    def test_get_user_info_authenticated_with_socialaccount(self):
        """
        Test if a user with a SocialAccount receives `is_openid_user: True`.
        """
        self.client.login(username="testuser", password=SECURE_PASSWORD)
        SocialAccount.objects.create(user=self.user, provider="google")

        response = self.client.get(self.get_user_info_url)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["is_openid_user"])
