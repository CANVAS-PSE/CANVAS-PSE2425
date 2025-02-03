from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    """
    Return the path to the user's profile picture.
    """
    return f"users/{instance.user.id}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to=user_directory_path, default="profile_pics/default.jpg"
    )

    def __str__(self):
        return self.user.email
