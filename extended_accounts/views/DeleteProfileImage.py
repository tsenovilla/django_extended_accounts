from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import Http404, HttpResponseRedirect
from extended_accounts.models import AccountModel as Account


class DeleteProfileImageView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get_object(self):
        return get_object_or_404(Account, username=self.kwargs["username"])

    def post(self, *args, **kwargs):
        account = self.get_object()
        account.update(profile_image=None)
        return HttpResponseRedirect(reverse_lazy("extended_accounts:redirect_account"))

    def test_func(self):
        account = self.get_object()
        if account != self.request.user:
            raise Http404
        return True
