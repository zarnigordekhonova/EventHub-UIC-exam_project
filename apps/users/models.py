from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from apps.users.managers import CustomUserManager


class CustomUser(AbstractUser):
    TYPE = (
        ('organizer', 'Organizer'),
        ('participant', 'Participant'),
    )

    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("First name"), max_length=128)
    last_name = models.CharField(_("Last name"), max_length=128)
    role = models.CharField(max_length=20, choices=TYPE, default="participant")

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)
    is_organizer_pending = models.BooleanField(default=False)
    is_organizer_confirmed = models.BooleanField(default=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
