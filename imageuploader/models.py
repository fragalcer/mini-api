from django.contrib.auth.models import AbstractBaseUser
from django.core.signing import SignatureExpired, TimestampSigner
from django.db import models
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
    key = models.CharField(_("Key"), max_length=200, primary_key=True)
    image = models.ForeignKey(UserImage, related_name='temporary_links', on_delete=models.CASCADE)

    @property
    def is_expired(self) -> bool:
        signer = TimestampSigner()
        try:
            signer.unsign_object(self.key, max_age=signer.unsign_object(self.key)['max_age'])
        except SignatureExpired:
            return True
        return False
