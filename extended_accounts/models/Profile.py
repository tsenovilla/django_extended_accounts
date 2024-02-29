from django.db import models
from django.utils import timezone
from django.conf import settings
from uuid import uuid4


def unique_image_name(instance, filename):
    """
    This function is used by ImageField's upload_to in order to get a unique name for an updated image, obtained via uuid4.
    WARNING: You might be tempted to use a lambda function instead of this one. That works perfectly when the application is running, but it fails when we make Django migrations. This is due to lambda functions cannot be serialized, which is a requirement for Django's migration framework. Therefore, to achieve a more consistent app, it is better to use this one.
    """
    return uuid4().hex + "." + filename.split(".")[-1]


class ProfileModel(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.IntegerField(
        unique=True, null=True
    )  ## We have to allow null here, otherwise it'll throw an error when creating users from the CLI. Otherwise we must pass this field to the Account Model but it's not worthy of that. It's OK with theoretically allowing null but we won't allow it in forms or serializers.
    profile_image = models.ImageField(
        upload_to=unique_image_name, default=None, null=True
    )
    date_joined = models.DateTimeField(default=timezone.now)
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE
    )
