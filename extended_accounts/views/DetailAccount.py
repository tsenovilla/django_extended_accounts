from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from extended_accounts.models import AccountModel as Account


class DetailAccountView(LoginRequiredMixin, DetailView):
    template_name = "extended_accounts/detail_account.html"

    def get_object(self):
        account = get_object_or_404(Account, username=self.kwargs["username"])
        return account
