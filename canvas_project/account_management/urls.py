from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("update_account/", views.update_account, name="update_account"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path('password_reset/<uidb64>/<token>/', views.password_reset_view, name='password_reset'),
    path('password_reset_failed/', views.password_reset_failed, name='password_reset_failed'),
    path('password_forgotten/', views.password_forgotten_view, name='password_forgotten'),
]
