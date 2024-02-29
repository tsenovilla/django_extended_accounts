from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from extended_accounts.helpers import NewAccountForm
from extended_accounts.models import AccountModel as Account
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
class NewAccountFormTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        Account.objects.create_user(
            username="jdoe",
            first_name="John",
            last_name="Doe",
            email="jdoe@mail.com",
            phone_number=987654321,
            password="passwordtest",
        )  ## Register an user to test the form errors
        cls.data = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@mail.com",
            "phone_number": 123456789,
            "password1": "passwordtest",
            "password2": "passwordtest",
        }

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass(*args, **kwargs)

    def __modify_data(self, to_modify):
        data = self.data.copy()
        data.update(to_modify)
        return data

    def test_init_form(self):
        form = NewAccountForm(self.data)
        self.assertIsNone(form.fields["password1"].help_text)
        self.assertIsNone(form.fields["password2"].help_text)

    def test_save_form_creates_account_OK(self):
        form = NewAccountForm(self.data, files={"profile_image": create_test_image()})
        self.assertTrue(form.is_valid())
        account = form.save()
        self.assertEqual(account.username, self.data["username"])
        self.assertEqual(account.email, self.data["email"])
        self.assertTrue(account.check_password(self.data["password1"]))
        self.assertEqual(account.profile.first_name, self.data["first_name"])
        self.assertEqual(account.profile.last_name, self.data["last_name"])
        self.assertEqual(account.profile.phone_number, self.data["phone_number"])
        self.assertIn(
            account.profile.profile_image.name + ".png", os.listdir(MEDIA_ROOT)
        )
        self.assertIn(
            account.profile.profile_image.name + ".webp", os.listdir(MEDIA_ROOT)
        )

    ## VALIDATORS TESTS
    def test_validator_OK(self):
        form = NewAccountForm(self.data)
        self.assertTrue(form.is_valid())

    def test_validator_no_first_name_KO(self):
        data = self.__modify_data({"first_name": ""})
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())

    def test_validator_no_last_name_KO(self):
        data = self.__modify_data({"last_name": ""})
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())

    def test_validator_no_email_KO(self):
        data = self.__modify_data({"email": ""})
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())

    def test_validator_duplicate_email_KO(self):
        data = self.__modify_data({"email": "jdoe@mail.com"})
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())

    def test_validator_no_phone_number_KO(self):
        data = self.__modify_data({"phone_number": ""})
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())

    def test_validator_malformed_phone_number_KO(self):
        ## Malformed phone number (incorrect length)
        data = self.__modify_data({"phone_number": 123})
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())

        ## Malformed phone number (not even numbers)
        data = self.__modify_data({"phone_number": "123frc789"})
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())

    def test_validator_duplicate_phone_number_KO(self):
        data = self.__modify_data({"phone_number": 987654321})
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())

    def test_validator_all_incorrect_KO(self):
        data = self.__modify_data(
            {"first_name": "", "last_name": "", "email": "", "phone_number": 987654321}
        )
        form = NewAccountForm(data)
        self.assertFalse(form.is_valid())
