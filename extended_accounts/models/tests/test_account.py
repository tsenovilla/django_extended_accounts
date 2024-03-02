from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Permission
from django.contrib.auth.backends import BaseBackend
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
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


class UselessBackend(
    BaseBackend
):  ## Use this backend to test that the manager returns manager.none() when calling with_perm if the used backend doesn't have a with_perm attribute
    pass


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AccountModelTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.initial_data = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@mail.com",
            "phone_number": 123456789,
            "profile_image": create_test_image(),
            "password": "test_password",
        }
        cls.account = Account.objects.create_user(**cls.initial_data)
        content_type = ContentType.objects.get_for_model(Account)
        cls.permission = Permission.objects.create(
            codename="can_do_something",
            name="Can Do Something",
            content_type=content_type,
        )
        cls.account.user_permissions.add(
            cls.permission
        )  ## Add the permission to the user

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass(*args, **kwargs)

    def __modify_data(self, to_modify):
        data = self.initial_data.copy()
        data.update(to_modify)
        return data

    ## CREATE_USER TESTS

    def test_create_user_OK(self):
        self.assertEqual(self.account.username, self.initial_data["username"])
        self.assertEqual(self.account.email, self.initial_data["email"])
        self.assertTrue(self.account.check_password(self.initial_data["password"]))
        self.assertFalse(self.account.is_superuser)
        self.assertFalse(self.account.is_staff)
        self.assertFalse(self.account.is_active)
        self.assertEqual(
            self.account.profile.first_name, self.initial_data["first_name"]
        )
        self.assertEqual(self.account.profile.last_name, self.initial_data["last_name"])
        self.assertEqual(
            self.account.profile.phone_number, self.initial_data["phone_number"]
        )
        self.assertIn(
            self.account.profile.profile_image.name + ".png", os.listdir(MEDIA_ROOT)
        )
        self.assertIn(
            self.account.profile.profile_image.name + ".webp", os.listdir(MEDIA_ROOT)
        )

    def test_create_user_rollback_OK_if_wrong_profile_data(self):
        try:
            Account.objects.create_user(username="jdoe", phone_number="NaN")
        except:  ## This exception will be throw as phone_number is not correct
            pass
        with self.assertRaises(Account.DoesNotExist):
            Account.objects.get(username="jdoe")

    def test_create_user_KO_if_username_empty(self):
        data = self.__modify_data(
            {"username": "", "phone_number": 987654321, "email": "jdoe@mail.com"}
        )
        with self.assertRaises(ValueError):
            Account.objects.create_user(**data)

    def test_create_superuser_OK(self):
        data = self.__modify_data(
            {"username": "jdoe", "phone_number": 987654321, "email": "jdoe@mail.com"}
        )  ## Update initial data, otherwise the unique fields will throw an exception
        admin_user = Account.objects.create_superuser(**data)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_create_superuser_KO_if_is_staff_manually_set_to_False_KO(self):
        data = self.__modify_data(
            {"username": "jdoe", "phone_number": 987654321, "email": "jdoe@mail.com"}
        )
        with self.assertRaises(ValueError):
            Account.objects.create_superuser(is_staff=False, **data)

    def test_create_superuser_KO_if_is_superuser_manually_set_to_False_KO(self):
        data = self.__modify_data(
            {"username": "jdoe", "phone_number": 987654321, "email": "jdoe@mail.com"}
        )
        with self.assertRaises(ValueError):
            Account.objects.create_superuser(is_superuser=False, **data)

    def test_create_superuser_KO_if_is_active_manually_set_to_False_KO(self):
        data = self.__modify_data(
            {"username": "jdoe", "phone_number": 987654321, "email": "jdoe@mail.com"}
        )
        with self.assertRaises(ValueError):
            Account.objects.create_superuser(is_active=False, **data)

    ## UPDATE TESTS

    def test_update_account_OK(self):
        self.account.refresh_from_db()  ## Note that the update function updates the in-memory object at the same time it updates the ddbb, so as we are using always the same self.account object, we can have an in-memory object with values corresponding to other tests at this point, so we have to refresh it
        self.account.update(
            username="jdoe",
            first_name="Johnny",
            email="jdoe@mail.com",
            phone_number=987654321,
        )
        ## Updated fields
        self.assertEqual(self.account.username, "jdoe")
        self.assertEqual(self.account.email, "jdoe@mail.com")
        self.assertEqual(self.account.profile.first_name, "Johnny")
        self.assertEqual(self.account.profile.phone_number, 987654321)
        ## The others remain equal, eg, the last_name
        self.assertEqual(self.account.profile.last_name, self.initial_data["last_name"])

    def test_update_without_email_OK(self):
        self.account.refresh_from_db()
        self.account.update(username="jdoe")
        ## Updated fields
        self.assertEqual(self.account.username, "jdoe")

    def test_update_without_username_OK(self):
        self.account.refresh_from_db()
        self.account.update(email="jdoe@mail.com")
        ## Updated fields
        self.assertEqual(self.account.email, "jdoe@mail.com")

    def test_update_rollback_OK_if_wrong_profile_data(self):
        self.account.refresh_from_db()
        try:
            self.account.update(email="jdoe@mail.com", phone_number="onetwothree")
        except:  ## The previous line will throw an exception, it's OK, we want to check that the email and the phone_number doesn't change
            pass
        self.assertEqual(self.account.email, self.initial_data["email"])
        self.assertEqual(
            self.account.profile.phone_number, self.initial_data["phone_number"]
        )

    def test_update_user_KO_if_not_username(self):
        with self.assertRaises(ValueError):
            self.account.update(username="")

    def test_update_user_KO_if_not_email(self):
        with self.assertRaises(ValueError):
            self.account.update(email="")

    def test_update_user_KO_if_wrong_data(self):
        data = self.__modify_data(
            {"username": "jdoe", "phone_number": 987654321, "email": "jdoe@mail.com"}
        )
        Account.objects.create_user(**data)
        with self.assertRaises(IntegrityError):
            self.account.update(username="jdoe")
        self.assertEqual(
            self.account.username, self.initial_data["username"]
        )  ## Test that the in-memory object is neither updated

    ## WITH_PERM TESTS

    def test_manager_with_perm_OK(self):
        self.account.update(is_active=True)  ## We need an active user for this test
        users_with_perm = Account.objects.with_perm(self.permission)
        self.assertIn(self.account, users_with_perm)

        # Test with_perm with invalid permission
        users_without_perm = Account.objects.with_perm("auth.cannot_do_something")
        self.assertNotIn(self.account, users_without_perm)

        # Test get the permission if backend manually supplied
        users_with_perm = Account.objects.with_perm(
            self.permission, backend="django.contrib.auth.backends.ModelBackend"
        )
        self.assertIn(self.account, users_with_perm)

        # Test None if the backend doesn't have with_perm attribute
        users_with_perm = Account.objects.with_perm(
            self.permission,
            backend="extended_accounts.models.tests.test_account.UselessBackend",
        )
        self.assertNotIn(self.account, users_without_perm)

    def test_manager_with_perm_KO_if_multiple_backends(self):
        # Mocking multiple authentication backends
        with self.settings(
            AUTHENTICATION_BACKENDS=[
                "django.contrib.auth.backends.ModelBackend",
                "django.contrib.auth.backends.RemoteUserBackend",
            ]
        ):
            with self.assertRaises(ValueError):
                Account.objects.with_perm(self.permission)

    def test_manager_with_perm_KO_if_backend_not_string_not_None(self):
        with self.assertRaises(TypeError):
            Account.objects.with_perm(self.permission, backend=1)
