from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse_lazy
from django.http import Http404
from django.core.files.uploadedfile import SimpleUploadedFile
from extended_accounts.models import AccountModel as Account
from extended_accounts.views import DeleteAccountView
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
class DeleteAccountViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.account = Account.objects.create_user(
            username="johndoe",
            phone_number=123456789,
            email="johndoe@mail.com",
            profile_image=create_test_image(),
        )
        cls.delete_url = reverse_lazy(
            "extended_accounts:delete_account",
            kwargs={"username": cls.account.username},
        )
        cls.factory = RequestFactory()
        cls.view = DeleteAccountView()

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(
            MEDIA_ROOT, ignore_errors=True
        )  ## At the end of the tests, the temporary directory is removed. ignore_errors = True ensures that this won't cause any issues, we don't care if this directory has errors when being removed
        super().tearDownClass(*args, **kwargs)

    def test_account_deleted(self):
        previous_image_name = self.account.profile.profile_image.name
        self.assertIn(previous_image_name + ".png", os.listdir(MEDIA_ROOT))
        self.assertIn(previous_image_name + ".webp", os.listdir(MEDIA_ROOT))
        request = self.factory.post(self.delete_url)
        request.user = self.account
        response = DeleteAccountView.as_view()(request, username=self.account.username)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse_lazy("extended_accounts:login"))
        with self.assertRaises(Account.DoesNotExist):
            Account.objects.get(username=self.account.username)
        self.assertNotIn(previous_image_name + ".png", os.listdir(MEDIA_ROOT))
        self.assertNotIn(previous_image_name + ".webp", os.listdir(MEDIA_ROOT))

    def test_get_success_url(self):
        self.assertEqual(
            self.view.get_success_url(), reverse_lazy("extended_accounts:login")
        )

    def test_get_object_correct(self):
        self.view.kwargs = {"username": self.account.username}
        self.assertEqual(self.view.get_object(), self.account)

    def test_get_object_404(self):
        self.view.kwargs = {"username": "not_registered_user"}
        with self.assertRaises(Http404):
            self.view.get_object()

    def test_test_func_OK(self):
        request = self.factory.get(self.delete_url)
        request.user = self.account
        self.view.setup(request, username=self.account.username)
        self.assertTrue(self.view.test_func())

    def test_test_func_404(self):
        request = self.factory.get(self.delete_url)
        other_account = Account.objects.create_user(
            username="other", email="other@mail.com", phone_number=987654321
        )
        request.user = other_account
        self.view.setup(request, username=self.account.username)
        with self.assertRaises(Http404):
            self.view.test_func()
