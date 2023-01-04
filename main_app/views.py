from django.contrib.auth.models import User
from .models import Product
from .serializers import ProductSerializer, UserSerializer
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q


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
        # Pass the modified data to the parent create method
        return super().create(request, *args, data=data, **kwargs)


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
        # Get the product id from the URL kwargs
        product_id = self.kwargs['id']

        # Get the product instance
        product = Product.objects.get(product_id=product_id)

        # Return the product instance
        return product


class CommingAuctionProductView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Get the current date and time
        now = timezone.now()

        # Calculate the sale date cutoff
        sale_date_cutoff = now + timezone.timedelta(days=10)

        # Get the products with a sale date within 10 days
        products = Product.objects.filter(
            Q(saledate__gte=now) & Q(saledate__lte=sale_date_cutoff))

        return products
