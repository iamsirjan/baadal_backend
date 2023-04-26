from datetime import date, datetime
from distutils.command.upload import upload
from time import time
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone



product_status_choices = (

    ("idle", "idle"),
    ("sold", "sold"),
    ("bought", "bought"),
    ("auction", "auction"),
    ("auction_ended", "auction_ended"),


)


class User(AbstractUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    firstname = models.TextField(max_length=250,blank=True)
    middlename = models.TextField(max_length=255, blank=True)
    lastname = models.TextField(max_length=255,blank=True)
    username = models.TextField(max_length=255, unique=True,)
    email = models.EmailField(max_length=255, unique=True,)
    phone = models.IntegerField(blank=True)
    address_1 = models.TextField(max_length=255,blank=True)
    address_2 = models.TextField(max_length=255, blank=True)
    country = models.TextField(max_length=255,blank=True)
    image = models.ImageField(upload_to='users',blank=True)
    password = models.TextField(max_length=255, default='')


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.TextField(max_length=255)
    baseprice = models.TextField(max_length=255)
    finalprice = models.TextField(max_length=255, blank=True)
    created_at = models.DateField(auto_now_add=True)
    saledate = models.DateField()
    saletime = models.TimeField(default='12:00:00')
    verified = models.BooleanField(default=False)
    police_verified = models.BooleanField(default=False)
    saleend = models.TimeField(default='12:00:00')
    saleenddate = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    auctionday = models.TextField(default='')
    age = models.IntegerField()
    thumbnailimage = models.ImageField(
        upload_to='product/thumbnail', default="")
    image1 = models.ImageField(
        upload_to='product/image1', default="")
    image2 = models.ImageField(
        upload_to='product/image2', default="")

    status = models.CharField(max_length=50,
                              choices=product_status_choices,
                              default="idle")

    user = models.ForeignKey(User, on_delete=models.CASCADE, default='')


    
    def assign_to_highest_bidder(self):
        now = timezone.now()
        if self.status == 'active' and self.saleenddate < now.date() and self.saleend < now.time():
            highest_bid = self.bidding_set.order_by('-price').first()
            if highest_bid is not None:
                self.finalprice = highest_bid.price
                self.user = highest_bid.user
                self.status = 'bought'
                self.save()

class Bidding(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE, default="")
    user = models.ForeignKey(User,on_delete=models.CASCADE, default="")
    price = models.TextField(max_length=255)
    bidded_at = models.DateField(auto_now_add=True)


class Product_image(models.Model):
    product = models.ForeignKey(
        Product, related_name='product_image', on_delete=models.CASCADE,)
    image = models.ImageField(upload_to='product')


kyc_status = (

    ("not verified", "not verified"),
    ("verified", "verified"),

)


class KYC(models.Model):
    kyc_id = models.AutoField(primary_key=True)

    national_id = models.TextField(max_length=255)
    image_1 = models.ImageField(upload_to='kyc',)
    image_2 = models.ImageField(upload_to='kyc',)
    status = models.CharField(max_length=255,
                              choices=kyc_status,
                              default="not verified")
    user = models.OneToOneField(User, on_delete=models.CASCADE,default="" )


