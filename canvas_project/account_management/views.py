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
from django.views.decorators.http import require_POST
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


def register_view(request):
    """
    Register a new user and redirect to the login page upon success.
    If the user is already logged in, redirect to the projects page.
    """

    if request.user.is_authenticated:
        return redirect(REDIRECT_PROJECTS_URL)

    if request.method == "POST":

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
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


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
        "accounts/account_creation_confirmation_email.html",
        {
            "user": user,
            "delete_account_url": delete_account_url,
        },
    )

    to_email = user.email
    email = EmailMessage(subject, message, to=[to_email])
    email.send()


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
            return render(request, "confirm_deletion.html")
    else:
        return redirect("invalid_link")


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
            next_url = request.POST.get("next") or request.GET.get(
                "next", REDIRECT_PROJECTS_URL
            )
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


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
    is_openid_user = SocialAccount.objects.filter(user=user).exists()

    if request.method == "POST":
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

            profile, created = UserProfile.objects.get_or_create(user=user)
            if request.POST.get("delete_picture") == "1":
                if (
                    profile.profile_picture
                    and profile.profile_picture.name != "profile_pics/default.jpg"
                ):
                    profile.profile_picture.delete()  # delete former profile picture
                profile.profile_picture = (
                    "profile_pics/default.jpg"  # set default profile picture
                )
            # Set profile picture only if a new one is uploaded
            elif form.cleaned_data.get("profile_picture"):
                # Check if the current profile picture exists and is not the default picture.
                if (
                    profile.profile_picture
                    and profile.profile_picture.name != "profile_pics/default.jpg"
                ):
                    profile.profile_picture.delete()
                profile.profile_picture = form.cleaned_data["profile_picture"]

            user.save()
            profile.save()

            messages.success(request, "Your account has been updated successfully.")
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Error in {field.label}: {error}")
        return redirect(request.META.get("HTTP_REFERER", "projects"))


@login_required
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
        "accounts/password_change_confirmation_email.html",
        {
            "user": user,
            "password_reset_url": password_reset_url,
        },
    )

    to_email = user.email
    email = EmailMessage(subject, message, to=[to_email])
    email.send()


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

        return render(request, "password_reset.html", {"form": form})
    else:
        return redirect("invalid_link")


def invalid_link(request):
    return render(request, "invalid_link.html")


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

    return render(request, "password_forgotten.html", {"form": form})


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
        "accounts/password_forgotten_email.html",
        {
            "user": user,
            "password_reset_url": password_reset_url,
        },
    )

    to_email = user.email
    email = EmailMessage(subject, message, to=[to_email])
    email.send()
