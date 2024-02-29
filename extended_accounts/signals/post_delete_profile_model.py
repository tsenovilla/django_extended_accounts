from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from extended_accounts.models import ProfileModel as Profile
import os


def delete_profile_image(instance):
    profile_image = instance.profile_image
    if profile_image.name:
        list_of_images = filter(
            lambda image: profile_image.name in image,
            os.listdir(settings.MEDIA_ROOT),
        )
        for image in list_of_images:
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, image))
            except:
                pass


@receiver(post_delete, sender=Profile)
def post_delete_profile_model(sender, **kwargs):
    instance = kwargs["instance"]
    delete_profile_image(instance)
