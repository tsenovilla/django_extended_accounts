from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse_lazy
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.response import TemplateResponse
from django.conf import settings
from extended_accounts.models import AccountModel as Account
from extended_accounts.views import NewAccountView
from PIL import Image
from io import BytesIO
import tempfile, shutil, os

MEDIA_ROOT = tempfile.mkdtemp()


def create_test_image():
    image_buffer = BytesIO()
    image_object = Image.new("RGB", (1, 1))
    image_object.save(image_buffer, "png")
    image_buffer.seek(0)
    image = SimpleUploadedFile(
        "test_image.png",
        image_buffer.read(),
    )
    return image


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NewAccountViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.factory = RequestFactory()
        cls.create_url = reverse_lazy("extended_accounts:new_account")
        cls.login_url = reverse_lazy("extended_accounts:login")

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(
            MEDIA_ROOT, ignore_errors=True
        )  ## At the end of the tests, the temporary directory is removed. ignore_errors = True ensures that this won't cause any issues, we don't care if this directory has errors when being removed
        super().tearDownClass(*args, **kwargs)

    def test_render_get(self):
        request = self.factory.get(self.create_url)
        response = NewAccountView.as_view()(request)
        self.assertEqual(200, response.status_code)
        self.assertIsInstance(response, TemplateResponse)
        self.assertIn("extended_accounts/new_account.html", response.template_name)

    def test_get_success_url(self):
        view = NewAccountView()
        self.assertEqual(view.get_success_url(), self.login_url)

    def test_create_user(self):
        data = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@mail.com",
            "phone_number": 123456789,
            "password1": "testpassword",
            "password2": "testpassword",
            "profile_image": create_test_image(),
        }
        request = self.factory.post(self.create_url, data)
        response = NewAccountView.as_view()(request)

        self.assertEqual(302, response.status_code)  ## Correct creation -> Redirect
        self.assertEqual(response.url, self.login_url)

        ## Test that the user has been saved correctly.
        account = Account.objects.get(username=data["username"])
        self.assertEqual(account.username, data["username"])
        self.assertEqual(account.email, data["email"])
        self.assertEqual(account.profile.first_name, data["first_name"])
        self.assertEqual(account.profile.last_name, data["last_name"])
        self.assertFalse(
            account.is_active
        )  ## Upon creation, the user isn't active until they confirm their account
        self.assertEqual(
            account.profile.phone_number, data["phone_number"]
        )  ## The phone has been registered correctly in the profile
        ## The image's been uploaded
        self.assertIn(
            account.profile.profile_image.name + ".png", os.listdir(MEDIA_ROOT)
        )
        self.assertIn(
            account.profile.profile_image.name + ".webp", os.listdir(MEDIA_ROOT)
        )
        ## To check the password, the account must be active
        account.update(is_active=True)
        self.assertTrue(account.check_password("testpassword"))

        ## Check that the email was sent correctly
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, "Account Confirmation")
        self.assertIn(
            "johndoe", sent_mail.body
        )  ## Verify that the email body contains the user's name (the content in the URL). We cannot verify the complete message because the token generated in the function may not be necessarily the same as we could generate here. In any case, this test is sufficient to see that the mail was sent correctly
        self.assertEqual(sent_mail.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertAlmostEqual(sent_mail.to, ["johndoe@mail.com"])
