from django.urls import path

from canvas import view_name_dict

from . import views

urlpatterns = [
    path("", views.LoginView.as_view(), name=view_name_dict.login_view),
    path(
        "register/", views.RegistrationView.as_view(), name=view_name_dict.register_view
    ),
    path("logout/", views.logout_view, name=view_name_dict.logout_view),
    path(
        "update_account/", views.update_account, name=view_name_dict.updata_account_view
    ),
    path(
        "delete_account/", views.delete_account, name=view_name_dict.delete_account_view
    ),
    path(
        "password_reset/<uidb64>/<token>/",
        views.PasswordResetView.as_view(),
        name=view_name_dict.password_reset_view,
    ),
    path("invalid_link/", views.invalid_link, name=view_name_dict.invalid_link_view),
    path(
        "confirm_deletion/<uidb64>/<token>/",
        views.ConfirmDeletionView.as_view(),
        name=view_name_dict.confirm_deletion_view,
    ),
    path(
        "password_forgotten_view/",
        views.PasswordForgottenView.as_view(),
        name=view_name_dict.password_forgotten_view,
    ),
    path("get_user_info/", views.get_user_info, name=view_name_dict.get_user_info_view),
]
