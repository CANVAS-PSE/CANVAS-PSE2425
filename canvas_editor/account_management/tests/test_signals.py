from django.contrib.auth.models import User
from django.test import TestCase

from account_management.models import UserProfile
from canvas.test_constants import (
    TEST_PASSWORD,
    TEST_EMAIL_2,
    FIRST_NAME_TEST_ENVIRONMENT,
    LAST_NAME_TEST_ENVIRONMENT,
    PROFILE_PIC_PATH_TEST,
)


class TestSignals(TestCase):
    """
    Contains test for the signals of the user profile model.
    """

    def setUp(self) -> None:
        """
        Configure the testing environment for the tests.
        """
        self.user = User.objects.create_user(
            username=TEST_EMAIL_2,
            first_name=FIRST_NAME_TEST_ENVIRONMENT,
            last_name=LAST_NAME_TEST_ENVIRONMENT,
            email=TEST_EMAIL_2,
            password=TEST_PASSWORD,
        )

    def test_create_user_profile(self):
        """
        Test the automatic generation of the user profile.
        """
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        user_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(user_profile.user, self.user)

    def test_save_user_profile(self):
        """
        Test the automatic saving of the profile when saving the user.
        """
        user_profile = self.user.userprofile
        user_profile.profile_picture = PROFILE_PIC_PATH_TEST
        self.user.save()
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.profile_picture, PROFILE_PIC_PATH_TEST)
