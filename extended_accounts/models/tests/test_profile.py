from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from extended_accounts.models import AccountModel as Account
from PIL import Image
from io import BytesIO
import tempfile, shutil, re

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
class ProfileModelTestCase(TestCase):
    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass(*args, **kwargs)

    def test_image_uses_uuid_name(
        self,
    ):  ## The ProfileModel is never accessed directly, it always goes with an AccountModel instance, so we do follow that here. Just checks that the image is uploaded with a hex name
        account = Account.objects.create_user(
            username="johndoe",
            phone_number=123456789,
            profile_image=create_test_image(),
        )
        hex_name = re.compile(
            r"^[0-9a-f]+$"
        )  ##post_save signal removes the extension, so the image name should simply be a chunk of hexadecimal characters
        self.assertTrue(hex_name.match(account.profile.profile_image.name))
