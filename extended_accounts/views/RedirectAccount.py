from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect


class RedirectAccountView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponseRedirect(
            reverse_lazy(
                "extended_accounts:detail_account",
                kwargs={"username": request.user.username},
            )
        )
