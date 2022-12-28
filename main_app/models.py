from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin


product_status_choices = (

    ("idle", "idle"),
    ("sold", "sold"),
    ("bought", "bought"),
    ("auction", "auction"),

)


class User(AbstractUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    firstname = models.TextField(max_length=255)
    middlename = models.TextField(max_length=255, blank=True)
    lastname = models.TextField(max_length=255)
    username = models.TextField(max_length=255, unique=True,)
    email = models.EmailField(max_length=255, unique=True,)
    phone = models.IntegerField(unique=True,)
    address_1 = models.TextField(max_length=255)
    address_2 = models.TextField(max_length=255, blank=True)
    country = models.TextField(max_length=255)
    image = models.ImageField(upload_to='users',)
    password = models.TextField(max_length=255, default='')


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.TextField(max_length=255)
    baseprice = models.TextField(max_length=255)
    finalprice = models.TextField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    saledate = models.DateTimeField()
    description = models.TextField(blank=True)
    age = models.IntegerField()
    thumbnailimage = models.ImageField(
        upload_to='product/thumbnail', default="")

    status = models.CharField(max_length=9,
                              choices=product_status_choices,
                              default="idle")

    user = models.ForeignKey(User, on_delete=models.CASCADE, default='')


class Product_image(models.Model):
    product = models.ForeignKey(
        Product, related_name='product_image', on_delete=models.CASCADE,)
    image = models.ImageField(upload_to='product')
