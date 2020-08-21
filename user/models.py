from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
import uuid


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        if kwargs.get('is_superuser'):
            user.is_staff = True

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **kwargs):
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_superuser', True)
        if kwargs.get('is_superuser') is False:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,
                            unique=True, db_index=True)
    email = models.EmailField(max_length=50, unique=True,
                              blank=False)

    username = models.CharField(max_length=50, unique=True)
    username_displayed = models.CharField(max_length=50, unique=False,
                                          blank=True, null=True)

    photo = models.ImageField(upload_to='users/',
                              blank=True, null=True)

    data_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    class Meta:
        db_table = 'user'

    USERNAME_FIELD = 'email'
    objects = UserManager()

