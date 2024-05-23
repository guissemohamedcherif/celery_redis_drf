import uuid
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
from api.validators import *
from django.contrib.auth.models import PermissionsMixin

SUPERADMIN = 'superadmin'
USER = 'user'

USER_TYPES = (
    (USER, USER),
    (SUPERADMIN, SUPERADMIN),
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('user_type', SUPERADMIN)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    fist_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, validators=[isnumbervalidator])
    is_active = models.BooleanField(('active'), default=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPES)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fist_name', 'last_name', 'phone_number']
    
    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')
        app_label = "api"

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f'<User: {self.pk}, email: {self.email}, user_type: {self.user_type}>'


class Product(models.Model):
    slug = models.SlugField(default=uuid.uuid1,editable=False)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=50, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'<Product: {self.pk}, name: {self.name}>'
