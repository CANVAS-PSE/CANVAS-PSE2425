import os

from canvas import path_dict
from django.contrib.auth.models import User
from django.db import models
from django.templatetags.static import static


def user_directory_path(instance, filename: str) -> str:
    """Return the path to the user's profile picture."""
    return f"users/{instance.user.id}/{filename}"


class UserProfile(models.Model):
    """Model representing a user's profile.

    This model extends the default Django User model by adding a profile picture.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True,
    )

    def __str__(self):
        """Return user's email."""
        return self.user.email

    @property
    def image_url(self):
        """Get the url to the profile picture of the user."""
        if self.profile_picture and os.path.isfile(self.profile_picture.path):
            return self.profile_picture.url
        return static(path_dict.default_profil_pic)

    @staticmethod
    def default_picture_url():
        """Get the default profile picture path."""
        return static(path_dict.default_profil_pic)
