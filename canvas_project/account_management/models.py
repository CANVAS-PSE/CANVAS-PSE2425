from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    """
    Return the path to the user's profile picture.
    """
    return f"users/{instance.user.id}/{filename}"


class UserProfile(models.Model):
    """
    Model representing a user's profile.
    This model extends the default Django User model by adding a profile picture.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to=user_directory_path, default="profile_pics/default.jpg"
    )

    def __str__(self):
        """
        Return user's email.
        """
        return self.user.email
