from django.contrib.auth.models import AbstractUser
from django.db import models


# # Create your models here.
# class user_mst(models.Model):
#     email=models.EmailField(unique=True)
#     password=models.CharField(max_length=20)

class CustomUser(AbstractUser):
    ROLES = (
        ('superadmin', 'Superadmin'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    phone_number = models.CharField(max_length=20)
    address=models.CharField(max_length=200)
    area_code=models.CharField(max_length=100)
    zone_name=models.CharField(max_length=50 )
    login_user_name=models.CharField(max_length=200)
    last_logout = models.DateTimeField(null=True, blank=True)
    

     


