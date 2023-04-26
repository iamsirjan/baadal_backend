from math import prod
from django.contrib.auth.models import User
from .models import KYC, Product, Bidding
from .serializers import KYCModelSerializer, ProductSerializer, UserSerializer , BiddingSerializer
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from datetime import date, datetime, timedelta
import cv2
import numpy as np
import pytesseract
import re
from django.core.files.uploadedfile import TemporaryUploadedFile
from tempfile import NamedTemporaryFile
from .yolo import compare_images
from .match import match_images
from django.core.files.storage import default_storage
from django.conf import settings
import glob
from django.http import Http404
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


# Register API

User = get_user_model()
MESSAGE = "Something went wrong."


class RegisterView(generics.CreateAPIView, generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class RetrieveUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        try:
            user = request.user
            user = UserSerializer(user)
            return Response({'user': user.data}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': MESSAGE}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductViewSet(generics.CreateAPIView, generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Product.objects.all()

    serializer_class = ProductSerializer

    # # Get the current date and time
    # now = timezone.now()

    # # Get the products with a sale date equal to today's date
    # products = Product.objects.filter(saledate=now)

    # # Change the status of the products to "sold"
    # products.update(status='auction')


  




    def create(self, request, *args, **kwargs):
        
        # Get the currently authenticated user
        user = request.user
      
       
        # Create a mutable copy of the request data
        data = request.data.copy()
       
        # Add the user to the request data
        data['user'] = user.pk
        # # Get the paths to the images from the request data
        img1 = request.FILES.get('image1')
        img2 = request.FILES.get('image2')

        # # # Save the images to the media directory
        img1_path = default_storage.save('images/' + img1.name, img1)
        img2_path = default_storage.save('images/' + img2.name, img2)

        
        # # # # Get the full paths to the saved images
        img1_full_path = settings.MEDIA_ROOT + '/' + img1_path
        
        img2_full_path = settings.MEDIA_ROOT + '/' + img2_path
        # # # # Compare the images using object detection
        result = compare_images(img1_full_path, img2_full_path)
        print(result)
        for img in glob.glob('/home/sirjan/major project/baadal_backend/main_app/image/*'):
            matchimage = match_images(img1_full_path, img)
            print(matchimage)
            if matchimage == True:
                verification = False
                break
            else:
                verification = True
            
        # Create a new Product object with the modified data
        product_serializer = self.get_serializer(data=data)
        if product_serializer.is_valid():
            print('ok')
            product = product_serializer.save()
            print('ok1')
            product.verified = result
            product.police_verified = verification
            
            product.save()
            return Response({'message': 'Product added successfully', 'product': product_serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': product_serializer.errors,'errors':product_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        


class ProductFilterViewSet(generics.ListAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Product.objects.all()    

    serializer_class = ProductSerializer

    def get_queryset(self):
        # Get the user id from the request
        user_id = self.request.user.user_id

        # Create a serializer instance
        serializer = ProductSerializer()

        # Get the products for the user
        products = serializer.get_products_by_user(user_id)

        return products


class ProductDeleteView(generics.DestroyAPIView, generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return Product.objects.get(product_id=self.kwargs['id'])
        except Product.DoesNotExist:
            raise Http404

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return Response({'message': 'Product deleted successfully'})

    def update(self, request, *args, **kwargs):
        # Get the paths to the images from the request data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        img1 = request.FILES.get('image1')
        img2 = request.FILES.get('image2')
       
        # Save the images to the media directory
        img1_path = default_storage.save('images/' + img1.name, img1  )
        img2_path = default_storage.save('images/' + img2.name, img2)
        # # Get the full paths to the saved images
        img1_full_path = settings.MEDIA_ROOT + '/' + img1_path
        img2_full_path = settings.MEDIA_ROOT + '/' + img2_path
        # # Compare the images using object detection
        result = compare_images(img1_full_path, img2_full_path)
        print(result)
        request.data['verified'] = result
        for img in glob.glob('/home/sirjan/major project/baadal_backend/main_app/image/*'):
            matchimage = match_images(img1_full_path, img)
            print(matchimage)
            if matchimage == True:

                request.data['police_verified'] = False
                
                break
            else:
                request.data['police_verified'] = True
                
        
        # Call the parent update method to perform the update
        self.perform_update(serializer)
        
        return Response({'message': 'Product edited successfully', 'product': serializer.data}, status=status.HTTP_201_CREATED)



class CommingAuctionProductView(generics.ListAPIView):
    



    def get(self, request, format=None):
        today = datetime.now().date()
        four_days_from_now = today + timedelta(days=4)
        upcoming_products = Product.objects.filter(
            saledate__gte=today,
            saledate__lte=four_days_from_now
        ).order_by('saledate')



        products = []
        for product in upcoming_products:
         
            

            time_left = (product.saledate - today).days
            
            if time_left < 1:
                sale_datetime = datetime.combine(product.saledate, product.saletime)
                time_left_seconds = (sale_datetime - datetime.now()).total_seconds()
                now = timezone.localtime(timezone.now())
               
                if time_left_seconds < 0 :
                    if datetime.combine(product.saleenddate, product.saleend) > datetime.now() and product.finalprice == '' :
                        product.status = 'auction'
                    elif product.finalprice != '':
                        product.status = 'sold'
                    elif datetime.combine(product.saleenddate, product.saleend) < datetime.now() and product.finalprice == '':
                        product.status = 'auction_ended'
                    else :
                        product.status = 'idle'
                    product.save()
                    auction_day = "00:00"
                    time_left = 0
                else:
                    hours_left = int(time_left_seconds / 3600)
                    minutes_left = int((time_left_seconds % 3600) / 60)
                    seconds_left = int(time_left_seconds % 60)
                    auction_day = f"{hours_left:02d}:{minutes_left:02d}:{seconds_left:02d}"
            elif time_left == 1:
                time_left = 1
                auction_day = str(time_left)
            else:
                auction_day = str(time_left)
                time_left = time_left - 1  # since we don't count today


            sale_enddatetime = datetime.combine(product.saleenddate, product.saleend)
            if product.status == 'idle':
                auction_end_at = "auction not started yet"
            elif product.status == 'sold' or product.status == 'auction_ended' or product.status == 'bought':
                auction_end_at = 'auction ended'
            elif sale_enddatetime > datetime.now():
                time_left_secondsend = (sale_enddatetime - datetime.now()).total_seconds()
                hours_leftend = int(time_left_secondsend / 3600)
                minutes_leftend = int((time_left_secondsend % 3600) / 60)
                seconds_leftend = int(time_left_secondsend % 60)
                auction_end_at = f"{hours_leftend:02d}:{minutes_leftend:02d}:{seconds_leftend:02d}"
            else :
                auction_end_at = 'soon'

            product_data = {
                'product_id': product.product_id,
                'name': product.name,
                'baseprice': product.baseprice,
                'finalprice': product.finalprice,
                'saledate': product.saledate,
                'auction_day': auction_day,
                'time_left': time_left,
                'status':product.status,
                'verified':product.verified,
                'police_verified':product.police_verified,
                'auction_end_at':auction_end_at,
                'created_at':product.created_at,
                'thumbnailimage': request.build_absolute_uri(product.thumbnailimage.url) if product.thumbnailimage else None
            }
            products.append(product_data)

        return Response(products)



class BiddingViewSet(generics.CreateAPIView, generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Bidding.objects.all()
    serializer_class = BiddingSerializer

    def get_queryset(self):
        queryset = Bidding.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        product_id = self.request.query_params.get('product_id', None)
        if user_id is not None:
            queryset = queryset.filter(user=user_id)
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)
        return queryset
   
    def perform_create(self,serializer):
         user = self.request.user
         product = self.request.data.get('product_id')  
         serializer.save(user=user, product_id=product)




class AssignProductView(APIView):
    def get(self, request,id, format=None):
        
        now = timezone.localtime(timezone.now())
        product = Product.objects.filter(
            product_id=id,
            saleenddate__lte=now.date(),
            saleend__lte=now.time(),
        
        )
        print(product)
        if product:
            
            highest_bid = Bidding.objects.filter(product=id).order_by('-price').first()
            
            if highest_bid:
                product = Product.objects.get(product_id=id)
                product.status = 'bought'
                product.user = highest_bid.user
                product.finalprice = highest_bid.price
                product.save()
        return Response({'message': 'Products assigned successfully.', 'data': {
                        'user_id': highest_bid.user.user_id,
                        'username': highest_bid.user.username,
                        'price': highest_bid.price
                    }})



class KycViewSet(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = KYC.objects.all()
    serializer_class = KYCModelSerializer

    def create(self, request):
             
        request.data['user'] = request.user.user_id
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(self.serializer_class(instance).data, status=status.HTTP_201_CREATED)


class KYCUpdateView(generics.DestroyAPIView, generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = KYC.objects.all()
    serializer_class = KYCModelSerializer
    lookup_field = 'id'

    def get_object(self):
        kyc_id = self.kwargs['id']

        # Get the product instance
        kyc = KYC.objects.get(kyc_id=kyc_id)

        return kyc


class GETKYCAPIViewBYId(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = KYCModelSerializer

    def get(self, request, user_id):
        try:
            kyc = KYC.objects.get(user_id=user_id)
            serializer = self.serializer_class(kyc)
            return Response(serializer.data)
        except KYC.DoesNotExist:
            return Response({'message': 'KYC not found'})

class VerifyKYCView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = KYCModelSerializer

    def get(self, request, user_id):

            try:
                kyc = KYC.objects.get(user=user_id)
               
                image_2_path = kyc.image_2.path
                print(image_2_path)

                img = cv2.imread(image_2_path)
                print(img)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                th, threshed = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)

                result = pytesseract.image_to_string(threshed, lang='ind')


                match = re.search(r'\d{2}-\d{2}-\d{2}-\d{5}', result)
                if match:
                    cc_number = match.group(0) 
                    print(cc_number)
                    if kyc.national_id == cc_number:
                        kyc.status = 'verified'
                        kyc.save()
                        return Response({'message': 'KYC verified','data':
                        self.serializer_class(kyc).data
                        })
                    else:
                        kyc.status = 'not verified'
                        kyc.save()
                        return Response({'message': 'KYC not verified','data':self.serializer_class(kyc).data})
                else:
                    return Response({'message': 'KYC not verified: no national ID found'})           
            
            except KYC.DoesNotExist:
                    return Response({'message': 'KYC not found'})

                

