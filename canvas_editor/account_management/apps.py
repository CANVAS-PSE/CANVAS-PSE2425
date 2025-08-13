from django.apps import AppConfig


class AccountManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "account_management"

    def ready(self):
        # Import signals to ensure they are registered
        import account_management.signals  # noqa: F401
