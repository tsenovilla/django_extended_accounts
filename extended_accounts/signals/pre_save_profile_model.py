from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from extended_accounts.models import ProfileModel as Profile
import os


def delete_previous_image_if_needed(instance):
    profile_image = instance.profile_image
    try:
        original_instance = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        pass
    else:
        conditions = [
            profile_image.name
            and profile_image.name
            not in original_instance.profile_image.name,  ## Change image condition: Be careful because the post_save signal makes a save to remove the extension from the image name in the ddbb, if we use != here instead of not in, we delete the newly uploaded image since profile_image.name is the name without the extension and the original one (in this case what was saved initially when calling save) is the name with the extension
            not profile_image.name
            and original_instance.profile_image.name,  ## User's image deletion condition (the original instance has content but not the new one)
        ]
        if any(conditions):
            list_of_images = filter(
                lambda image: original_instance.profile_image.name in image,
                os.listdir(settings.MEDIA_ROOT),
            )
            for image in list_of_images:
                try:
                    os.remove(os.path.join(settings.MEDIA_ROOT, image))
                except:
                    pass


@receiver(pre_save, sender=Profile)
def pre_save_profile_model(sender, **kwargs):
    instance = kwargs["instance"]
    delete_previous_image_if_needed(instance)
