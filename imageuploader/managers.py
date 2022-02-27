from django.contrib.auth.base_user import BaseUserManager

from plans.models import Plan


class ImageUploaderManager(BaseUserManager):
    def create_user(self, email, plan_id, password=None):
        """Creates and saves a User with the given email, account tier and password."""
        if not email:
            raise ValueError('Users must have an email address')

        plan = Plan.objects.get(id=plan_id)

        user = self.model(
            email=self.normalize_email(email),
            plan=plan,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, plan, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            plan_id=plan,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
