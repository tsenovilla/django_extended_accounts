from django.apps import AppConfig


class ExtendedAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "extended_accounts"

    def ready(self):
        # Import the signals
        from .signals import __all__

        return super().ready()
