from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.views.generic import View
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from extended_accounts.models import AccountModel as Account


class AccountConfirmationView(View):
    def get(self, request, **kwargs):
        ## If the account does not exist or it is already validated, we return a 404.
        ## We don't want this URL to be visited more than once per user.
        ## If everything is OK, we activate the account and redirect.
        account = get_object_or_404(Account, username=kwargs["username"])
        if account.is_active:
            raise Http404
        if default_token_generator.check_token(account, kwargs["token"]):
            account.is_active = True
            account.save()
            login(request, account)
            return HttpResponseRedirect(
                reverse_lazy("extended_accounts:redirect_account")
            )
        raise Http404
