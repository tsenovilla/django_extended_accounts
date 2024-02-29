from django.test import TestCase, RequestFactory
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import Http404
from extended_accounts.models import AccountModel as Account
from extended_accounts.views import AccountConfirmationView


class AccountConfirmationViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.account = Account.objects.create_user(
            username="johndoe", email="johndoe@mail.com", phone_number=123456789
        )
        cls.factory = RequestFactory()
        cls.token = default_token_generator.make_token(cls.account)

    def test_ok(self):
        """
        Test that if the user is not active and the followed link is the activation one, then the account gets confirmed and redirected (HTTP response code = 302)
        """
        request = self.factory.get(
            reverse_lazy(
                "extended_accounts:account_confirmation",
                kwargs={
                    "username": self.account.username,
                    "token": self.token,
                },
            )
        )
        ## Since the user has is_active set to False, request.user = self.account doesn't assign a session to the request and the response cannot be processed, hence we need to create a fake session with SessionMiddleware, which creates the session without doing anything else (its get_response function does nothing)
        middleware = SessionMiddleware(lambda get_response: None)
        middleware.process_request(request)
        request.session.save()
        response = AccountConfirmationView.as_view()(
            request, username=self.account.username, token=self.token
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            response.url,
            reverse_lazy("extended_accounts:redirect_account"),
        )
        ## Check the user's now active
        self.account.refresh_from_db()
        self.assertTrue(self.account.is_active)

    def test_user_not_found_404(self):
        """
        Test that if the user passed by URL doesn't exist, then a 404 is rendered
        """
        request = self.factory.get(
            reverse_lazy(
                "extended_accounts:account_confirmation",
                kwargs={"username": "jdoe", "token": "doesntmatter"},
            )
        )
        with self.assertRaises(Http404):
            AccountConfirmationView.as_view()(
                request, username=self.account.username, token="doesntmatter"
            )

    def test_active_user_404(self):
        """
        Test that if the user passed by URL is already active, then a 404 is rendered
        """
        self.account.update(is_active=True)
        request = self.factory.get(
            reverse_lazy(
                "extended_accounts:account_confirmation",
                kwargs={
                    "username": self.account.username,
                    "token": self.token,
                },
            )
        )
        with self.assertRaises(Http404):
            AccountConfirmationView.as_view()(
                request, username=self.account.username, token=self.token
            )

    def test_wrong_token_404(self):
        """
        Test that if the token is incorrect, it responds with 404
        """
        request = self.factory.get(
            reverse_lazy(
                "extended_accounts:account_confirmation",
                kwargs={"username": self.account.username, "token": "wrong_token"},
            )
        )
        with self.assertRaises(Http404):
            AccountConfirmationView.as_view()(
                request, username=self.account.username, token="wrong_token"
            )
