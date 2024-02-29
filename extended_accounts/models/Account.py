from django.db import models, transaction
from django.apps import apps
from django.contrib import auth
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _


class AccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given username and password and the profile information in an associated profile model
        """
        from .Profile import ProfileModel as Profile

        if not username:
            raise ValueError("The given username must be set")
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        is_staff = extra_fields.pop("is_staff", False)
        is_superuser = extra_fields.pop("is_superuser", False)
        is_active = extra_fields.pop(
            "is_active", False
        )  # Default for is_active will be False, so users must activate their accounts with an email
        email = self.normalize_email(extra_fields.pop("email", None))
        account = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )
        account.password = make_password(password)
        with transaction.atomic():  ## Atomic transaction, if anything goes wrong everything must be rolled back
            account.save(using=self._db)
            Profile.objects.create(account=account, **extra_fields)
        return account

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class AccountModel(AbstractBaseUser, PermissionsMixin):
    """
    An account class that almost defaults to the standard Django User for simplicity. Here the authentication model for your project may be customized. This design's been chosen because we need to extend the default user behavior to properly link the auth properties (defined by this model) and the profile properties(those that are not related to authentication, defined by ProfileModel). Taking the default Django User model code allows to fully customize the accounts from here, while linking them with their profile data.
    We say it almost defaults to the standard Django User because we remove some fields that are not directly related with autentication in django.contrib.auth.models.User (first_name, last_name, ...) and send them to the profile model, so it's slightly different. This allows us keeping this model just for authentication, it also allows each app to specify its own user data requirements without potentially conflicting or breaking assumptions by other app. As a counterpart, more queries are required to work with the model, so maybe you prefer to store everything in this model, sacrifying the flexibility mentioned above.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = AccountManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        swappable = "AUTH_USER_MODEL"

    def update(self, **kwargs):
        from .Profile import ProfileModel as Profile

        ## Get the fields associated with the profile. We discard _state, id, account_id and date joined as they shouldn't be manually updated
        profile_fields = list(Profile().__dict__.keys())
        profile_fields.remove("_state")
        profile_fields.remove("id")
        profile_fields.remove("account_id")
        profile_fields.remove("date_joined")
        ## Get the fields related to the profile inside the update requested fields
        profile_update_requested_fields = {
            k: kwargs.pop(k) for k in profile_fields if k in kwargs
        }
        ## Update
        self.profile.__dict__.update(**profile_update_requested_fields)
        try:
            username = kwargs.pop("username")
        except (
            KeyError
        ):  ## If username isn't part of the kwargs, it's not being updated, so this is OK
            pass
        else:
            if not username:  ## Check that the username passed is not an empty string
                raise ValueError("username cannot be empty")
            kwargs["username"] = self.normalize_username(username)
        try:
            email = kwargs.pop("email")
        except (
            KeyError
        ):  ## If email isn't part of the kwargs, it's not being updated, so this is OK
            pass
        else:
            if not email:  ## Check that the username passed is not an empty string
                raise ValueError("emailcannot be empty")
            kwargs["email"] = AccountManager().normalize_email(email)
        self.__dict__.update(**kwargs)
        try:
            with transaction.atomic():  ## Atomic transaction, if something goes wrong, everything must be rolled back
                self.save()
                self.profile.save()
        except Exception as e:
            self.refresh_from_db()  ## If something went wrong, re-synchronize self with the ddbb (the __dict__.update operations changed our in_memory object)
            raise e
