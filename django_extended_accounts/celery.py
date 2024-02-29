import os
from celery import Celery

# Set the default configuration file
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_extended_accounts.settings")

celery_app = Celery(
    "django_extended_accounts"
)  ## Rename the app with your project's name :)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means that all celery-related configuration keys
# should have a prefix `CELERY_`.
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Import celery task modules registered in all Django apps
celery_app.autodiscover_tasks()
