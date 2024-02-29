from django.db.models.base import Model as Model
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from extended_accounts.models import AccountModel as Account
from extended_accounts.helpers import UpdateAccountForm


class UpdateAccountView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "extended_accounts/update_account.html"
    model = Account
    form_class = UpdateAccountForm

    def get_success_url(self):
        return reverse_lazy("extended_accounts:redirect_account")

    def get_object(self):
        return get_object_or_404(Account, username=self.kwargs["username"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = kwargs["instance"]
        kwargs["initial"] = {
            "first_name": instance.profile.first_name,
            "last_name": instance.profile.last_name,
            "phone_number": instance.profile.phone_number,
            "profile_image": instance.profile.profile_image,
        }
        return kwargs

    def test_func(self):
        user = self.get_object()
        if user != self.request.user:
            raise Http404
        return True
