from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse_lazy
from django.http import Http404
from django.core.files.uploadedfile import SimpleUploadedFile
from extended_accounts.models import AccountModel as Account
from extended_accounts.views import UpdateAccountView
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
class UpdateAccountViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.account = Account.objects.create_user(
            username="johndoe",
            email="johndoe@mail.com",
            first_name="John",
            last_name="Doe",
            phone_number=123456789,
            profile_image=create_test_image(),
        )
        cls.view = UpdateAccountView()
        cls.update_url = reverse_lazy(
            "extended_accounts:update_account",
            kwargs={"username": cls.account.username},
        )
        cls.factory = RequestFactory()

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(
            MEDIA_ROOT, ignore_errors=True
        )  ## At the end of the tests, the temporary directory is removed. ignore_errors = True ensures that this won't cause any issues, we don't care if this directory has errors when being removed
        super().tearDownClass(*args, **kwargs)

    def test_get_success_url(self):
        self.assertEqual(
            self.view.get_success_url(),
            reverse_lazy("extended_accounts:redirect_account"),
        )

    def test_get_object_correct(self):
        self.view.kwargs = {"username": self.account.username}
        self.assertEqual(self.view.get_object(), self.account)

    def test_get_object_404(self):
        self.view.kwargs = {"username": "not_registered_user"}
        with self.assertRaises(Http404):
            self.view.get_object()

    def test_get_form_kwargs(self):
        request = self.factory.get(self.update_url)
        self.view.setup(request)
        self.view.object = self.account
        kwargs = self.view.get_form_kwargs()
        self.assertEqual(kwargs["instance"], self.account)
        self.assertEqual(
            kwargs["initial"]["first_name"], self.account.profile.first_name
        )
        self.assertEqual(kwargs["initial"]["last_name"], self.account.profile.last_name)
        self.assertEqual(
            kwargs["initial"]["phone_number"], self.account.profile.phone_number
        )
        self.assertEqual(
            kwargs["initial"]["profile_image"], self.account.profile.profile_image
        )

    def test_test_func_OK(self):
        request = self.factory.get(self.update_url)
        request.user = self.account
        self.view.setup(request, username=self.account.username)
        self.assertTrue(self.view.test_func())

    def test_test_func_404(self):
        request = self.factory.get(self.update_url)
        other_account = Account.objects.create_user(
            username="other", email="other@mail.com", phone_number=987654321
        )
        request.user = other_account
        self.view.setup(request, username=self.account.username)
        with self.assertRaises(Http404):
            self.view.test_func()

    def test_update_user(self):
        request = self.factory.get(self.update_url)
        request.user = self.account
        response = UpdateAccountView.as_view()(request, username=self.account.username)

        initial_data = response.context_data["form"].initial
        self.assertEqual(initial_data["username"], self.account.username)
        self.assertEqual(initial_data["first_name"], self.account.profile.first_name)
        self.assertEqual(initial_data["last_name"], self.account.profile.last_name)
        self.assertEqual(initial_data["email"], self.account.email)
        self.assertEqual(
            initial_data["phone_number"], self.account.profile.phone_number
        )
        self.assertIn(
            initial_data["profile_image"].name + ".png", os.listdir(MEDIA_ROOT)
        )
        self.assertIn(
            initial_data["profile_image"].name + ".webp", os.listdir(MEDIA_ROOT)
        )

        new_data = {
            "username": self.account.username,
            "first_name": "Johnny",
            "last_name": "Doey",
            "email": "johhnydoey@mail.com",
            "phone_number": 987654321,
            "profile_image": create_test_image(),
        }

        request = self.factory.post(self.update_url, new_data)
        request.user = self.account
        response = UpdateAccountView.as_view()(request, username=self.account.username)
        self.assertEqual(302, response.status_code)  ## Correct update -> Redirection
        self.assertEqual(
            response.url, reverse_lazy("extended_accounts:redirect_account")
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.profile.first_name, new_data["first_name"])
        self.assertEqual(self.account.profile.last_name, new_data["last_name"])
        self.assertEqual(self.account.email, new_data["email"])
        self.assertEqual(self.account.profile.phone_number, new_data["phone_number"])
        ## The image has been properly uploaded to the server with its different extensions, similarly, the old image is no longer present
        self.assertIn(MEDIA_ROOT, self.account.profile.profile_image.path)
        self.assertIn(
            self.account.profile.profile_image.name + ".png", os.listdir(MEDIA_ROOT)
        )
        self.assertIn(
            self.account.profile.profile_image.name + ".webp", os.listdir(MEDIA_ROOT)
        )
        self.assertNotIn(
            initial_data["profile_image"].name + ".png", os.listdir(MEDIA_ROOT)
        )
        self.assertNotIn(
            initial_data["profile_image"].name + ".webp", os.listdir(MEDIA_ROOT)
        )
