from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from extended_accounts.models import AccountModel as Account
from PIL import Image
from io import BytesIO
import tempfile, shutil, re, os

MEDIA_ROOT = (
    tempfile.mkdtemp()
)  ## During the tests, we will use this directory for image uploads


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
class PostSaveProfileModelTesCase(TestCase):

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        shutil.rmtree(
            MEDIA_ROOT, ignore_errors=True
        )  ## At the end of the tests, the temporary directory is removed. ignore_errors = True ensures that this will not cause any issues; we are indifferent to errors during deletion.
        super().tearDownClass(*args, **kwargs)

    def test_post_save_model_perfil(
        self,
    ):  ## Profile is a model completely linked to Account, so we can test its features through an account instance
        account = Account.objects.create_user(
            username="johndoe",
            email="johndoe@mail.com",
            phone_number=123456789,
            profile_image=create_test_image(),
        )
        unique_name_without_extension = re.compile(r"^[0-9a-f]+$")
        self.assertTrue(
            unique_name_without_extension.match(account.profile.profile_image.name)
        )  ## In the database, we only have the name without extensions
        ## But the image has been successfully uploaded to the server
        self.assertIn(MEDIA_ROOT, account.profile.profile_image.path)
        self.assertIn(
            account.profile.profile_image.name + ".png", os.listdir(MEDIA_ROOT)
        )
        self.assertIn(
            account.profile.profile_image.name + ".webp", os.listdir(MEDIA_ROOT)
        )
