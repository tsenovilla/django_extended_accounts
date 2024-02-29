from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from extended_accounts.models import AccountModel as Account
from extended_accounts.helpers import delete_unconfirmed_accounts


def trigger_delete_unconfirmed_accounts(instance):
    if (
        settings.TESTING ^ settings.INTEGRATION_TEST_CELERY
    ):  ## If we are running tests, we don't launch the Celery task every time a user is created. We don't want to test Celery (external dependency) but our functionality. We only launch it in case we are testing the Celery integration
        return
    delete_unconfirmed_accounts.apply_async(
        args=[instance.username],
        countdown=900,  ## 900 seconds = 15 minutes
    )


@receiver(post_save, sender=Account)
def post_save_account_model(sender, **kwargs):
    instance = kwargs["instance"]
    if kwargs["created"]:
        trigger_delete_unconfirmed_accounts(instance)
