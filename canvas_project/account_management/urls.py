from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("update_account/", views.update_account, name="update_account"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path('password_reset/<uidb64>/<token>/', views.password_reset_view, name='password_reset'),
    path('invalid_link/', views.invalid_link, name='invalid_link'),
    path('confirm_deletion/<uidb64>/<token>/', views.confirm_deletion, name='confirm_deletion'),
]
