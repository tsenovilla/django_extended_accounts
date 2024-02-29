from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from extended_accounts.models import AccountModel as Account


class ListAccountView(LoginRequiredMixin, ListView):
    template_name = "extended_accounts/list_account.html"
    model = Account
