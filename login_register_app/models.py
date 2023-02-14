from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from rest_framework.authtoken.models import Token

# create and save user objects using the UserManager
class UserManager(BaseUserManager):
    # create a new user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # create a new user with superuser privileges
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# user definition - inherits AbstractBaseUser
class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    age = models.IntegerField()
    GENDER_OPTIONS = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    gender = models.CharField(max_length=6, choices=GENDER_OPTIONS, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # field used as unique identifier
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        db_table = 'users'
