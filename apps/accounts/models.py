from django.db import models

class UserRole(models.TextChoices):
    user = 'user',
    admin = 'admin',
    instructor = 'instructor',