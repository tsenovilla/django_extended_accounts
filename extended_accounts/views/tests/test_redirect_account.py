from django.test import TestCase, RequestFactory
from django.urls import reverse_lazy
from django.contrib.auth.models import AnonymousUser
from extended_accounts.models import AccountModel as Account
from extended_accounts.views import RedirectAccountView


class RedirectAccountTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.account = Account.objects.create_user(
            username="johndoe", email="johndoe@mail.com", phone_number=123456789
        )
        cls.redirect_account_url = reverse_lazy("extended_accounts:redirect_account")
        cls.factory = RequestFactory()

    def test_redirect_if_user_authenticated(self):
        request = self.factory.get(self.redirect_account_url)
        request.user = self.account
        response = RedirectAccountView.as_view()(request)
        self.assertEqual(
            response.url,
            reverse_lazy(
                "extended_accounts:detail_account",
                kwargs={"username": self.account.username},
            ),
        )

    def test_redirect_if_user_not_authenticated(self):
        request = self.factory.get(self.redirect_account_url)
        request.user = AnonymousUser()
        response = RedirectAccountView.as_view()(request)
        self.assertEqual(
            response.url,
            f'/extended_accounts/login/?next={reverse_lazy("extended_accounts:redirect_account")}',
        )
