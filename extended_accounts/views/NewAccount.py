from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.views.generic.edit import CreateView
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from extended_accounts.helpers import NewAccountForm
from extended_accounts.models import AccountModel as Account


class NewAccountView(CreateView):
    template_name = "extended_accounts/new_account.html"
    form_class = NewAccountForm

    def get_success_url(self):
        return reverse_lazy("extended_accounts:login")

    def form_valid(self, form):
        ## Get the response of the super's form_valid
        response = super().form_valid(form)
        account = Account.objects.get(
            username=form.instance.username
        )  ## Get the account directly from the model manager. If we use form.instance directly, it doesn't have the 1to1 related Profile object because it's just a form object
        self.__send_confirmation_email(account)
        return response

    def __send_confirmation_email(self, account):
        subject = "Account Confirmation"
        message = f'Hello!\nWe have received your account creation request, follow the link {self.request.build_absolute_uri(reverse_lazy("extended_accounts:account_confirmation", kwargs = {"username": account.username, "token": default_token_generator.make_token(account)}))} to confirm your account. The link will be valid for 15 minutes, if you do not confirm the account within that time frame you will have to start the process again.'
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[account.email],
        )
