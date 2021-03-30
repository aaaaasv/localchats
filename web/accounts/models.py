from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField('Email', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_username(self):
        return self.username

    def update_username(self, new_username):
        self.username = new_username
        self.save()
        return self.username


class AnonymousUser(models.Model):
    id = models.AutoField(primary_key=True)

    def get_username(self):
        try:
            return self.username_set.all().last().username
        except AttributeError:
            return f'user#{self.id}'

    def get_username_instance(self):
        try:
            return self.username_set.all().last()
        except AttributeError:
            return None

    def update_username(self, new_username):
        print("OK")
        u = self.username_set.create(
            username=new_username,
            user=self
        )
        print("OK 2")
        u.save()
        self.save()
        return self.get_username()


class Username(models.Model):
    user = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, default="user")
