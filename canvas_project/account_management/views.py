from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import login, update_session_auth_hash, logout
from .forms import (
    RegisterForm,
    LoginForm,
    UpdateAccountForm,
    DeleteAccountForm,
    PasswordResetForm,
    PasswordForgottenForm,
)
from django.views.decorators.http import require_POST, require_http_methods, require_GET
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import get_user_model
from .models import UserProfile
from allauth.socialaccount.models import SocialAccount
from django.http import JsonResponse

REDIRECT_PROJECTS_URL = "projects"
REDIRECT_LOGIN_URL = "login"
DEFAULT_PROFIL_PIC = "profile_pics/default.jpg"


class RegistrationView(View):
    """
    Register a new user and redirect to the login page upon success.
    If the user is already logged in, redirect to the projects page.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(REDIRECT_PROJECTS_URL)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = RegisterForm()
        return render(request, "account_management/register.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
            )
            user.set_password(password)
            user.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            send_register_email(user, request)
            return redirect(REDIRECT_PROJECTS_URL)
        return render(request, "account_management/register.html", {"form": form})


def send_register_email(user, request):
    """
    Send an email to the user to confirm that their account has been created.
    """
    subject = "CANVAS: Registration Confirmation"

    # Create the token for the user
    uid = urlsafe_base64_encode(str(user.id).encode())
    token = default_token_generator.make_token(user)

    base_url = request.build_absolute_uri("/")
    # Create the URL for the password change page
    delete_account_url = f"{base_url}confirm_deletion/{uid}/{token}/"

    message = render_to_string(
        "account_management/accounts/account_creation_confirmation_email.html",
        {
            "user": user,
            "delete_account_url": delete_account_url,
        },
    )

    to_email = user.email
    email = EmailMessage(subject, message, to=[to_email])
    email.send()


@require_http_methods(["GET", "POST"])
def confirm_deletion(request, uidb64, token):
    """
    Confirm the deletion of the user's account.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            logout(request)
            user.delete()
            return redirect("login")
        else:
            return render(request, "account_management/confirm_deletion.html")
    else:
        return redirect("invalid_link")


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Log in the user and redirect to the projects page upon success.
    If the user is already logged in, redirect to the projects page.
    """

    if request.user.is_authenticated:
        return redirect(REDIRECT_PROJECTS_URL)

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            return redirect(REDIRECT_PROJECTS_URL)
    else:
        form = LoginForm()
    return render(request, "account_management/login.html", {"form": form})


@require_POST
def logout_view(request):
    """
    Log out the current user and redirect to the login page.
    """
    logout(request)
    return redirect(REDIRECT_LOGIN_URL)


@require_POST
@login_required
def update_account(request):
    """
    Update the user's account information.
    """
    user = request.user

    form = UpdateAccountForm(instance=user, data=request.POST, files=request.FILES)

    if form.is_valid():
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["email"]
        # Set the username to the email for consistency
        user.username = user.email

        old_password = form.cleaned_data["old_password"]
        new_password = form.cleaned_data["new_password"]

        if old_password and new_password:
            user.set_password(new_password)
            update_session_auth_hash(request, user)
            send_password_change_email(user, request)

        _update_profile_picture(
            user=user,
            delete_picture=request.POST.get("delete_picture") == "1",
            new_profile_picture=form.cleaned_data["profile_picture"],
        )

        messages.success(request, "Your account has been updated successfully.")
    else:
        for field in form:
            for error in field.errors:
                messages.error(request, f"Error in {field.label}: {error}")
    return redirect(request.META.get("HTTP_REFERER", "projects"))


def _update_profile_picture(user: User, delete_picture: bool, new_profile_picture):
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if delete_picture and profile.profile_picture:
        profile.profile_picture.delete()
        profile.profile_picture = DEFAULT_PROFIL_PIC
    elif new_profile_picture:
        profile.profile_picture.delete()
        profile.profile_picture = new_profile_picture

    user.save()
    profile.save()


@login_required
@require_GET
def get_user_info(request):
    user = request.user
    is_openid_user = SocialAccount.objects.filter(user=user).exists()
    return JsonResponse({"is_openid_user": is_openid_user})


def send_password_change_email(user, request):
    """
    Send an email to the user to confirm that their password has been changed.
    """
    subject = "Password Change Confirmation"

    # Create the token for the user
    uid = urlsafe_base64_encode(str(user.id).encode())
    token = default_token_generator.make_token(user)

    base_url = request.build_absolute_uri("/")
    # Create the URL for the password change page
    password_reset_url = f"{base_url}password_reset/{uid}/{token}/"

    message = render_to_string(
        "account_management/accounts/password_change_confirmation_email.html",
        {
            "user": user,
            "password_reset_url": password_reset_url,
        },
    )

    to_email = user.email
    email = EmailMessage(subject, message, to=[to_email])
    email.send()


@require_http_methods(["GET", "POST"])
def password_reset_view(request, uidb64, token):
    """
    View to reset the password and log the user out from all sessions.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data["new_password"])
                user.save()

                # Logout from all sessions
                logout(request)

                # Redirect to login page
                return redirect("login")
        else:
            form = PasswordResetForm()

        return render(request, "account_management/password_reset.html", {"form": form})
    else:
        return redirect("invalid_link")


@require_GET
def invalid_link(request):
    return render(request, "account_management/invalid_link.html")


@require_POST
@login_required
def delete_account(request):
    """
    Delete the user's account.
    """
    if request.method == "POST":
        form = DeleteAccountForm(request.user, request.POST)
        if form.is_valid():
            request.user.delete()
            logout(request)
            return redirect(REDIRECT_LOGIN_URL)
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")

    return redirect(request.META.get("HTTP_REFERER", "projects"))


@require_http_methods(["GET", "POST"])
def password_forgotten_view(request):
    """
    View if a user doesn't remember its password and wants to reset it.
    """
    if request.method == "POST":
        form = PasswordForgottenForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email)
            send_password_forgotten_email(user, request)
        return redirect("login")
    else:
        form = PasswordForgottenForm()

    return render(request, "account_management/password_forgotten.html", {"form": form})


def send_password_forgotten_email(user, request):
    """
    Send an email to the user to reset their password.
    """
    subject = "Password Reset"

    # Create the token for the user
    uid = urlsafe_base64_encode(str(user.id).encode())
    token = default_token_generator.make_token(user)

    base_url = request.build_absolute_uri("/")
    # Create the URL for the password change page
    password_reset_url = f"{base_url}password_reset/{uid}/{token}/"

    message = render_to_string(
        "account_management/accounts/password_forgotten_email.html",
        {
            "user": user,
            "password_reset_url": password_reset_url,
        },
    )

    to_email = user.email
    email = EmailMessage(subject, message, to=[to_email])
    email.send()
