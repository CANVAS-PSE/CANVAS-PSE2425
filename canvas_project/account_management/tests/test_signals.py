from django.test import TestCase
from django.contrib.auth.models import User
from account_management.models import UserProfile


class TestSignals(TestCase):
    def test_create_user_profile(self):
        user = User.objects.create_user(
            username="test@mail.de",
            first_name="first_name",
            last_name="last_name",
            email="test@mail.de",
            password="test",
        )
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        user_profile = UserProfile.objects.get(user=user)
        self.assertEqual(user_profile.user, user)

    def test_save_user_profile(self):
        user = User.objects.create_user(
            username="test@mail.de",
            first_name="first_name",
            last_name="last_name",
            email="test@mail.de",
            password="test",
        )
        user_profile = user.userprofile
        user_profile.profile_picture = "users/1/custom.jpg"
        user_profile.save()
        user.save()
        updated_profile = UserProfile.objects.get(user=user)
        self.assertEqual(updated_profile.profile_picture, "users/1/custom.jpg")
