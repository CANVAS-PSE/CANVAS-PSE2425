from django.urls import path

from . import views

urlpatterns = [
    path("", views.LoginView.as_view(), name="login"),
    path("register/", views.RegistrationView.as_view(), name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("update_account/", views.update_account, name="update_account"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path(
        "password_reset/<uidb64>/<token>/",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path("invalid_link/", views.invalid_link, name="invalid_link"),
    path(
        "confirm_deletion/<uidb64>/<token>/",
        views.ConfirmDeletionView.as_view(),
        name="confirm_deletion",
    ),
    path(
        "password_forgotten_view/",
        views.PasswordForgottenView.as_view(),
        name="password_forgotten",
    ),
    path("get_user_info/", views.get_user_info, name="get_user_info"),
]
