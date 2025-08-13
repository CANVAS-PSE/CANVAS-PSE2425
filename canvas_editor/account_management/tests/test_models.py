from django.test import TestCase
from django.contrib.auth.models import User
from account_management.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.templatetags.static import static


class UserProfileModelTest(TestCase):
    def setUp(self):
        """Setup a test user and user profile."""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="SecurePassword123!",
        )
        self.profile = UserProfile.objects.get(user=self.user)

    def test_user_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertFalse(bool(self.profile.profile_picture))
        self.assertEqual(self.profile.image_url, static("img/profile_pics/default.svg"))

    def test_user_profile_str(self):
        self.assertEqual(str(self.profile), self.user.email)

    def test_user_profile_picture_upload_path(self):
        file = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )
        self.profile.profile_picture = file
        self.profile.save()
        expected_prefix = f"users/{self.user.id}/test"

        self.assertTrue(self.profile.profile_picture.name.startswith(expected_prefix))
