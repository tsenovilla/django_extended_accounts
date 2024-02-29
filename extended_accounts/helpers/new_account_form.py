from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from extended_accounts.models import AccountModel as Account


class NewAccountForm(UserCreationForm):
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
    profile_image = forms.ImageField(required=False, label="Profile image")

    def __init__(self, *args, **kwargs):  ## We remove the help texts which look ugly
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

    def save(
        self,
    ):  ## This form is used to create a user, so it's to call the create_user function in the Account model's manager when saving
        self.cleaned_data.pop("password1")
        self.cleaned_data["password"] = self.cleaned_data.pop(
            "password2"
        )  ## If cleaned data, password1==password2 contains the password information
        return Account.objects.create_user(**self.cleaned_data)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:  # Check if the email is already associated with an user
            Account.objects.get(email=email)
        except Account.DoesNotExist:
            pass
        else:
            raise ValidationError(
                "The email provided is already registered by another user."
            )
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        try:  # Check if the phone number is already associated with an user
            Account.objects.get(profile__phone_number=phone_number)
        except Account.DoesNotExist:
            pass
        else:
            raise ValidationError(
                "The phone number provided is already registered by another user."
            )
        return phone_number

    class Meta(UserCreationForm.Meta):
        model = Account
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_image",
        )
