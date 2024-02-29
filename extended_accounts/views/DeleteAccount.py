from django.views.generic import DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import Http404
from extended_accounts.models import AccountModel as Account


class DeleteAccountView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Account
    template_name = "extended_accounts/delete_account.html"

    def get_success_url(self):
        return reverse_lazy("extended_accounts:login")

    def get_object(self):
        return get_object_or_404(Account, username=self.kwargs["username"])

    def test_func(self):
        account = self.get_object()
        if account != self.request.user:
            raise Http404
        return True
