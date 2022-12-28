from django.contrib.auth.models import User
from .models import Product
from .serializers import ProductSerializer, UserSerializer
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from .filters import ProductFilter

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
    filter_class = ProductFilter
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        # Get the currently authenticated user
        user = request.user
        # Create a mutable copy of the request data
        data = request.data.copy()
        # Add the user to the request data
        data['user'] = user.pk
        # Pass the modified data to the parent create method
        return super().create(request, *args, data=data, **kwargs)
