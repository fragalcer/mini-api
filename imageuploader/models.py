import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from imageuploader.managers import ImageUploaderManager
from plans.models import Plan


class ImageUploaderUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = ImageUploaderManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['plan']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin


class UserImage(models.Model):
    user = models.ForeignKey(ImageUploaderUser, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=False, null=True)
    thumbnail_200 = ImageSpecField(
        source='image', processors=[ResizeToFit(200, 200)], format='JPEG'
    )
    thumbnail_400 = ImageSpecField(
        source='image', processors=[ResizeToFit(400, 400)], format='JPEG'
    )


class TemporaryLink(models.Model):
    key = models.UUIDField(
        default=uuid.uuid1,
        editable=False,
        help_text='Universally-unique Identifier. Uses UUID1 as this improves uniqueness and tracking between links',
        unique=True
    )
    image = models.ForeignKey(UserImage, related_name='temporary_links', on_delete=models.CASCADE)
    expiry_date = models.DateTimeField(
        _('Expiration date'),
        help_text=_("Date on which the Link is no longer effective."),
    )

    @property
    def is_expired(self) -> bool:
        return self.expiry_date < timezone.now()
