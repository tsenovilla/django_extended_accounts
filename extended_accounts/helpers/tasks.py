from extended_accounts.models import AccountModel as Account
from celery import shared_task


# This task will be called by the post_save signal of Account when one hour has passed since registration. If the user has not been confirmed, it will be deleted from the database.
@shared_task
def delete_unconfirmed_accounts(username):
    try:
        account = Account.objects.get(username=username)
        if not account.is_active:
            account.delete()
    except Account.DoesNotExist:  # If it doesn't exist, there's nothing to do.
        pass
