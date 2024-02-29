from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from extended_accounts.models import AccountModel as Account
from extended_accounts.helpers import UpdateAccountForm
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
class UpdateAccountFormTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.initial_data = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@mail.com",
            "phone_number": 123456789,
        }
        cls.account = Account.objects.create_user(**cls.initial_data)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass(*args, **kwargs)

    def __modify_data(self, to_modify):
        data = self.initial_data.copy()
        data.update(to_modify)
        return data

    def test_init_form(self):
        form = UpdateAccountForm(data=self.initial_data, instance=self.account)
        self.assertEqual(form.account, self.account)
        self.assertNotIn("last_login", form.fields.keys())
        self.assertNotIn("is_superuser", form.fields.keys())
        self.assertNotIn("groups", form.fields.keys())
        self.assertNotIn("user_permissions", form.fields.keys())
        self.assertNotIn("is_staff", form.fields.keys())
        self.assertNotIn("is_active", form.fields.keys())
        self.assertNotIn("date_joined", form.fields.keys())
        self.assertNotIn("password", form.fields.keys())

    def test_save_form_updates_account_OK(self):
        data = self.__modify_data(
            {"username": "jdoe", "phone_number": 987654321, "first_name": "Johnny"}
        )
        form = UpdateAccountForm(
            data=data,
            instance=self.account,
            files={"profile_image": create_test_image()},
        )
        self.assertTrue(form.is_valid())
        account = form.save()
        self.assertEqual(account.username, data["username"])
        self.assertEqual(account.email, self.initial_data["email"])
        self.assertEqual(account.profile.first_name, data["first_name"])
        self.assertEqual(account.profile.last_name, self.initial_data["last_name"])
        self.assertEqual(account.profile.phone_number, data["phone_number"])
        self.assertIn(
            account.profile.profile_image.name + ".png", os.listdir(MEDIA_ROOT)
        )
        self.assertIn(
            account.profile.profile_image.name + ".webp", os.listdir(MEDIA_ROOT)
        )

    ## VALIDATORS TESTS

    def test_validator_OK(self):
        self.account.refresh_from_db()  # Note that the update function called by the form updates the in-memory object at the same time it updates the ddbb, so as we are using always the same self.account object, we can have an in-memory object with values corresponding to the test that effectively updated the object, so we hace to refresh it.
        form = UpdateAccountForm(data=self.initial_data, instance=self.account)
        self.assertTrue(form.is_valid())

    def test_validator_OK_if_email_not_duplicate(self):
        self.account.refresh_from_db()
        data = self.__modify_data({"email": "other@mail.com"})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertTrue(form.is_valid())

    def test_validator_OK_if_phone_number_not_duplicate(self):
        self.account.refresh_from_db()
        data = self.__modify_data({"phone_number": 987654321})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertTrue(form.is_valid())

    def test_validator_no_first_name_KO(self):
        self.account.refresh_from_db()
        data = self.__modify_data({"first_name": ""})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())

    def test_validator_no_last_name_KO(self):
        self.account.refresh_from_db()
        data = self.__modify_data({"last_name": ""})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())

    def test_validator_no_email_KO(self):
        self.account.refresh_from_db()
        data = self.__modify_data({"email": ""})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())

    def test_validator_duplicate_email_KO(self):
        self.account.refresh_from_db()
        Account.objects.create_user(
            username="other", email="other@mail.com", phone_number=987654321
        )
        data = self.__modify_data({"email": "other@mail.com"})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())

    def test_validator_no_phone_number_KO(self):
        self.account.refresh_from_db()
        data = self.__modify_data({"phone_number": ""})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())

    def test_validator_duplicate_phone_number_KO(self):
        self.account.refresh_from_db()
        Account.objects.create_user(
            username="other", email="other@mail.com", phone_number=987654321
        )
        data = self.__modify_data({"phone_number": 987654321})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())

    def test_validator_malformed_phone_number_KO(self):
        self.account.refresh_from_db()
        ## Malformed phone number (incorrect length)
        data = self.__modify_data({"phone_number": "123"})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())

        ## Malformed phone number (not even numbers)
        data = self.__modify_data({"phone_number": "123frc789"})
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())

    def test_validator_all_incorrect_KO(self):
        self.account.refresh_from_db()
        data = self.__modify_data(
            {"first_name": "", "last_name": "", "email": "", "phone_number": 123}
        )
        form = UpdateAccountForm(data=data, instance=self.account)
        self.assertFalse(form.is_valid())
