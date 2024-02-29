from django.test import TestCase
from extended_accounts.models import AccountModel as Account
from extended_accounts.helpers import delete_unconfirmed_accounts


class TasksTestCase(TestCase):
    ## Unit test for the Celery task delete_unconfirmed_accounts. It is tested synchronously and completed with the integration test in tests/integracion/test_integracion_celery which verifies that the task is called when creating a user
    def test_delete_unconfirmed_user(self):
        Account.objects.create_user(
            username="user_1", phone_number=123456789, email="user1@mail.com"
        )  ## This user will not be confirmed and therefore will be deleted
        Account.objects.create_user(
            username="user_2",
            phone_number=987654321,
            email="user2@mail.com",
            is_active=True,
        )
        ## Before the Celery task is executed, the users exist
        self.assertTrue(Account.objects.filter(username="user_1").exists())
        self.assertTrue(Account.objects.filter(username="user_2").exists())
        ## Unit test: we can call the Celery task synchronously.
        delete_unconfirmed_accounts.s(username="user_1").apply()
        delete_unconfirmed_accounts.s(username="user_2").apply()
        ## Check again if the users exist
        self.assertFalse(Account.objects.filter(username="user_1").exists())
        self.assertTrue(Account.objects.filter(username="user_2").exists())

    ## If the task is launched on a non-existent user (for example because the user deletes it before the task completes), no exception is raised
    def test_non_existent_user_non_blocking(self):
        delete_unconfirmed_accounts.s(username="user_1").apply()
