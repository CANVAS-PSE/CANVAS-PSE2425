from django import forms
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount

PASSWORD_LENGTH_CRITERIUM_TEXT = "Password must be at least 8 characters long."
PASSWORD_DIGIT_CRITERIUM_TEXT = "Password must contain at least one digit."
PASSWORD_UPPERCASE_CRITERIUM_TEXT = (
    "Password must contain at least one uppercase letter."
)
PASSWORD_LOWERCASE_CRITERIUM_TEXT = (
    "Password must contain at least one lowercase letter."
)
PASSWORD_MATCH_CRITERIUM_TEXT = (
    "The passwords you entered do not match. Please try again."
)
PASSWORD_SPECIAL_CHAR_CRITERIUM_TEXT = (
    "Password must contain at least one special character (!@#$%^&*()-_+=<>?/)."
)
PASSWORD_SPECIAL_CHARACTERS = "!@#$%^&*()-_+=<>?/"
INCORRECT_PASSWORD_TEXT = "The password you entered is incorrect."
EMAIL_ALREADY_IN_USE_TEXT = "This email address is already in use. Please try another."


class RegisterForm(forms.Form):
    """
    A form for registering a new user. It includes fields for email, password,
    and password_confirmation. It also validates that the two passwords match.
    """

    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="password", widget=forms.PasswordInput)
    password_confirmation = forms.CharField(
        label="Confirm password", widget=forms.PasswordInput
    )

    def clean_email(self):
        """
        Checks if the email already exists.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            self.add_error(
                "email",
                EMAIL_ALREADY_IN_USE_TEXT,
            )
        return email

    def clean_password(self):
        """
        Validates the password based on security criteria.
        """
        password = str(self.cleaned_data.get("password"))

        if len(password) < 8:
            self.add_error("password", PASSWORD_LENGTH_CRITERIUM_TEXT)
        if not any(char.isdigit() for char in password):
            self.add_error("password", PASSWORD_DIGIT_CRITERIUM_TEXT)
        if not any(char.isupper() for char in password):
            self.add_error("password", PASSWORD_UPPERCASE_CRITERIUM_TEXT)
        if not any(char.islower() for char in password):
            self.add_error("password", PASSWORD_LOWERCASE_CRITERIUM_TEXT)
        if not any(char in PASSWORD_SPECIAL_CHARACTERS for char in password):
            self.add_error(
                "password",
                PASSWORD_SPECIAL_CHAR_CRITERIUM_TEXT,
            )
        return password

    def clean(self):
        """
        Validates that the two passwords match. If they do not, a validation error
        is raised.
        """
        cleaned_data = super().clean()
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data.get("password_confirmation")

        if password != password_confirmation:
            self.add_error("password", PASSWORD_MATCH_CRITERIUM_TEXT)

        return cleaned_data


class LoginForm(forms.Form):
    """
    A form for logging in an existing user. It includes fields for email and
    password. It also validates that the email exists and that the password is
    correct.
    """

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def clean(self):
        """
        Validates that the email exists and that the password is correct. If the
        email does not exist or the password is incorrect, a validation error is
        raised.
        """
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user = User.objects.filter(email=email).first()

        # Check if the user with this email exists and the password is correct.
        if not user:
            self.add_error("email", EMAIL_ALREADY_IN_USE_TEXT)
        elif not user.check_password(password):
            self.add_error("password", INCORRECT_PASSWORD_TEXT)
        else:
            self.user = user

        return self.cleaned_data

    def get_user(self):
        """
        Returns the user object if the form is valid.
        """
        return self.user


class UpdateAccountForm(forms.ModelForm):
    """
    A form for updating the user's account information. It includes fields for
    first_name, last_name, and email. It also includes fields for the old password,
    new password, and password_confirmation. It validates that the old password is
    correct, that the new password passes the security criteria, and that the two
    new passwords match.
    """

    first_name = forms.CharField(label="First name", required=False)
    last_name = forms.CharField(label="Last name", required=False)
    email = forms.EmailField(label="Email", required=False)

    old_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="old_password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="new_password"
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput, required=False, label="password_confirmation"
    )

    profile_picture = forms.ImageField(required=False, label="profile_picture")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "profile_picture"]

    def clean_email(self):
        """
        Validates the email address.
        """
        email = self.cleaned_data.get("email")
        if SocialAccount.objects.filter(user=self.instance).exists():
            return self.instance.email
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            self.add_error("email", EMAIL_ALREADY_IN_USE_TEXT)
        return email

    def clean_old_password(self):
        """
        Validates the old password.
        """
        old_password = self.cleaned_data.get("old_password")
        if old_password and not self.instance.check_password(old_password):
            self.add_error("old_password", INCORRECT_PASSWORD_TEXT)
        return old_password

    def clean_new_password(self):
        """
        Validates that the new password passes the sequrity meassurements.
        """
        new_password = self.cleaned_data.get("new_password")

        if new_password:
            if len(new_password) < 8:
                self.add_error("new_password", PASSWORD_LENGTH_CRITERIUM_TEXT)
            if not any(char.isdigit() for char in new_password):
                self.add_error("new_password", PASSWORD_DIGIT_CRITERIUM_TEXT)
            if not any(char.isupper() for char in new_password):
                self.add_error(
                    "new_password",
                    PASSWORD_UPPERCASE_CRITERIUM_TEXT,
                )
            if not any(char.islower() for char in new_password):
                self.add_error(
                    "new_password",
                    PASSWORD_LOWERCASE_CRITERIUM_TEXT,
                )
            if not any(char in PASSWORD_SPECIAL_CHARACTERS for char in new_password):
                self.add_error(
                    "new_password",
                    PASSWORD_SPECIAL_CHAR_CRITERIUM_TEXT,
                )
        return new_password

    def clean_password_confirmation(self):
        """
        Validates that the two new passwords match. If they do not, a validation error
        is raised.
        """
        new_password = self.cleaned_data.get("new_password")
        password_confirmation = self.cleaned_data.get("password_confirmation")

        if new_password and new_password != password_confirmation:
            self.add_error(
                "password_confirmation",
                PASSWORD_MATCH_CRITERIUM_TEXT,
            )

        return password_confirmation

    def clean(self):
        """
        Validates that the old password is entered when a new password is entered.
        """
        old_password = self.cleaned_data.get("old_password")
        new_password = self.cleaned_data.get("new_password")

        if old_password and not new_password:
            self.add_error("new_password", "Please enter a new password.")
        if new_password and not old_password:
            self.add_error("old_password", "Please enter your current password.")

        return self.cleaned_data


class DeleteAccountForm(forms.Form):
    """
    A form for deleting an account. It includes a field for the password.
    """

    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        """
        Validates the password.
        """
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            self.add_error("password", INCORRECT_PASSWORD_TEXT)
        return password


class PasswordResetForm(forms.Form):
    """
    A form for resetting the password. It includes fields for the new password
    and the password confirmation. It validates that the two passwords match.
    """

    new_password = forms.CharField(label="New password", widget=forms.PasswordInput)
    password_confirmation = forms.CharField(
        label="Confirm new password", widget=forms.PasswordInput
    )

    def clean_new_password(self):
        """
        Validates that the new password passes the security criteria.
        """
        new_password = str(self.cleaned_data.get("new_password"))

        if len(new_password) < 8:
            self.add_error("new_password", PASSWORD_LENGTH_CRITERIUM_TEXT)
        if not any(char.isdigit() for char in new_password):
            self.add_error("new_password", PASSWORD_DIGIT_CRITERIUM_TEXT)
        if not any(char.isupper() for char in new_password):
            self.add_error("new_password", PASSWORD_UPPERCASE_CRITERIUM_TEXT)
        if not any(char.islower() for char in new_password):
            self.add_error("new_password", PASSWORD_LOWERCASE_CRITERIUM_TEXT)
        if not any(char in PASSWORD_SPECIAL_CHARACTERS for char in new_password):
            self.add_error(
                "new_password",
                PASSWORD_SPECIAL_CHAR_CRITERIUM_TEXT,
            )

        return new_password

    def clean(self):
        """
        Validates that the two passwords match. If they do not, a validation error
        is raised.
        """
        cleaned_data = super().clean()
        new_password = self.cleaned_data.get("new_password")
        password_confirmation = self.cleaned_data.get("password_confirmation")

        if new_password != password_confirmation:
            self.add_error(
                "password_confirmation",
                PASSWORD_MATCH_CRITERIUM_TEXT,
            )

        return cleaned_data


class PasswordForgottenForm(forms.Form):
    """
    A form for resetting the password when the user has forgotten it. It includes
    a field for the email address.
    """

    email = forms.EmailField(label="Email")

    def clean_email(self):
        """
        Checks if the email exists.
        """
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            self.add_error("email", "This email address is not registered.")
        return email
