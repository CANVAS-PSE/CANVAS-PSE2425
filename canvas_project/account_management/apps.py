from django.apps import AppConfig


class AccountManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "account_management"

    def ready(self):
        import account_management.signals

