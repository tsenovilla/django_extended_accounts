from django.test import TestCase
from django.conf import settings
from extended_accounts.models import AccountModel as Account
from unittest.mock import patch


## Integration test to ensure that the Celery task is correctly called asynchronously.
## A mock of the real task is made to verify that it has been called with the established input and the correct time counter.
class IntegrationCeleryTest(TestCase):
    @patch("extended_accounts.helpers.tasks.delete_unconfirmed_accounts.apply_async")
    def test_integration_signal_post_save_user(self, mock_celery_call):
        settings.INTEGRATION_TEST_CELERY = (
            True  ## Activate this flag so that the post-save user signal is run
        )
        Account.objects.create_user(username="user_1", phone_number=123456789)
        mock_celery_call.assert_called_with(args=["user_1"], countdown=900)
        settings.INTEGRATION_TEST_CELERY = False
