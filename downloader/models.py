from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    major = models.CharField('major', max_length=5, blank=True)
