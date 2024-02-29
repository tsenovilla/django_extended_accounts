from django.db.models.signals import post_save
from django.dispatch import receiver
from extended_accounts.models import ProfileModel as Profile
from PIL import Image


def manage_uploaded_image(instance):
    profile_image = instance.profile_image
    if (
        profile_image and "." in profile_image.name
    ):  ## If '.' in profile_image.name, it means the image has been updated since in the database the name is stored without extension
        ## We save the image in webp format on the server.
        path = profile_image.path
        server_image = Image.open(profile_image)
        server_image.save(f'{path.split(".")[0]}.webp', format="WEBP")
        ## We save the name without extension in the database
        profile_image.name = profile_image.name.split(".")[0]
        instance.save()


@receiver(post_save, sender=Profile)
def post_save_profile_model(sender, **kwargs):
    instance = kwargs["instance"]
    manage_uploaded_image(instance)
