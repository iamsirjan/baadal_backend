from urllib import request
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import KYC, Product_image, Product, Bidding
# User Serializer
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(
        required=True,

    )
    lastname = serializers.CharField(
        required=True,

    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    phone = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    address_1 = serializers.CharField(
        required=True,
    )

    image = serializers.ImageField(
        required=True,
    )

    country = serializers.CharField(
        required=True,
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('user_id', 'username', 'email', 'phone', 'firstname', 'middlename', 'image', 'address_1', 'address_2', 'country',
                  'lastname', 'password', 're_password', )

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'], password=validated_data['password'], username=validated_data['username'], firstname=validated_data[
                'firstname'], lastname=validated_data['lastname'],
            phone=validated_data['phone'], address_1=validated_data[
                'address_1'],  country=validated_data['country'], image=validated_data['image'], address_2=validated_data[
                'address_2'], middlename=validated_data['middlename']

        )
        return user


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product_image
        fields = ['image']


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    product_image = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'baseprice', 'finalprice', 'created_at', 'saletime', 'auctionday',
                  'saledate', 'saleend','description', 'age', 'status', 'product_image', 'user', 'thumbnailimage']

    def create(self, validated_data):
        # Get the currently authenticated user
        user = self.context['request'].user
        # Add the user to the validated data
        validated_data['user'] = user

        # Create the product instance
        product = Product.objects.create(**validated_data)

        # If there are product images provided in the request, create image instances for them
        if 'product_image' in validated_data:
            product_image_data = validated_data.pop('product_image')
            for image_data in product_image_data:
                Product_image.objects.create(product=product, **image_data)
        return product

    def get_thumbnailimage_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.thumbnailimage.url) if obj.thumbnailimage else ''

    def get_products_by_user(self, user_id):
        products = Product.objects.filter(user=user_id)
       
        return products

class BiddingSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Bidding
        fields = ['id','product','user','price','bidded_at']


class KYCModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = KYC
        fields = ['kyc_id','national_id','image_1','image_2','status','user']
