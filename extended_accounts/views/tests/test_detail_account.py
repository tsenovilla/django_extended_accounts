from django.test import TestCase, RequestFactory
from django.urls import reverse_lazy
from django.http import Http404
from extended_accounts.models import AccountModel as Account
from extended_accounts.views import DetailAccountView


class DetailAccountViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.account = Account.objects.create_user(
            username="johndoe", phone_number=123456789, email="johndoe@mail.com"
        )
        cls.detail_url = reverse_lazy(
            "extended_accounts:detail_account",
            kwargs={"username": cls.account.username},
        )
        cls.view = DetailAccountView()
        cls.factory = RequestFactory()

    def test_get_object_correct(self):
        self.view.kwargs = {"username": self.account.username}
        self.assertEqual(self.view.get_object(), self.account)

    def test_get_object_404(self):
        self.view.kwargs = {"username": "not_registered_user"}
        with self.assertRaises(Http404):
            self.view.get_object()
