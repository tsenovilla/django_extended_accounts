from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from extended_accounts.models import AccountModel as Account


class UpdateAccountForm(UserChangeForm):
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=True, label="Last Name")
    email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.IntegerField(
        required=True,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{9}$",
                message="Phone number must contain 9 digits",  ## This validation is due to spanish phone numbers are composed by 9 digits, adapt it accordingly with your needs
            )
        ],
        label="Phone Number",
    )
    profile_image = forms.ImageField(required=False, label="Profile Image")

    def __init__(
        self, *args, **kwargs
    ):  ## We delete all the fields from the ChangeForm that shouldn't be updated by the users themselves (password update requires a special view)
        super().__init__(*args, **kwargs)
        del self.fields["last_login"]
        del self.fields["is_superuser"]
        del self.fields["groups"]
        del self.fields["user_permissions"]
        del self.fields["is_staff"]
        del self.fields["is_active"]
        del self.fields["password"]
        ## We define the user and the profile throughout the form since we need it to clean of the email and the phone number. There is no problem with exceptions with the get method called below since if this view is accessed it is because the user is registered and therefore both user and profile exist.
        self.account = Account.objects.get(username=self.initial["username"])

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:  # Check if the email is already associated with another user
            account_using_email = Account.objects.get(email=email)
            if account_using_email != self.account:
                raise ValidationError(
                    "The email provided is already registered by another user."
                )
        except Account.DoesNotExist:
            pass
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        try:  # Check if the phone number is already associated with a user
            account_using_phone = Account.objects.get(
                profile__phone_number=phone_number
            )
            if account_using_phone != self.account:
                raise ValidationError(
                    "The phone number provided is already registered by another user."
                )
        except Account.DoesNotExist:
            pass
        return phone_number

    def save(self):  ## Need to add this in order to
        self.account.update(**self.cleaned_data)
        return self.account

    class Meta(UserChangeForm.Meta):
        model = Account
