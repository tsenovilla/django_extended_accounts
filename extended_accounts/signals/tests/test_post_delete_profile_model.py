from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from extended_accounts.models import AccountModel as Account
from PIL import Image
from io import BytesIO
from unittest.mock import patch
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
class PostDeleteProfileModelTestCase(
    TestCase
):  ## Profile is a model completely linked to Account, so we can test its features through an account instance
    def setUp(self):
        self.account = Account.objects.create_user(
            username="johndoe",
            email="johndoe@mail.com",
            phone_number=123456789,
            profile_image=create_test_image(),
        )

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass(*args, **kwargs)

    def test_post_delete_model_profile(self):
        previous_image_name = self.account.profile.profile_image.name
        self.assertIn(previous_image_name + ".png", os.listdir(MEDIA_ROOT))
        self.assertIn(previous_image_name + ".webp", os.listdir(MEDIA_ROOT))
        self.account.delete()
        self.assertNotIn(previous_image_name + ".png", os.listdir(MEDIA_ROOT))
        self.assertNotIn(previous_image_name + ".webp", os.listdir(MEDIA_ROOT))

    @patch("os.remove")
    def test_non_blocking_execution_if_remove_nonexistent_image(self, mock_os_remove):
        mock_os_remove.side_effect = Exception("Simulated exception")
        self.account.delete()
