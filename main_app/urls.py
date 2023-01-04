from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ProductFilterViewSet, RegisterView, RetrieveUserView, ProductViewSet, ProductDeleteView, CommingAuctionProductView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user', RetrieveUserView.as_view(), name="retrieve_user"),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('product/', ProductViewSet.as_view(), name="product"),
    path('filter/product/',
         ProductFilterViewSet.as_view(), name="product"),
    path('product/<int:id>/', ProductDeleteView.as_view(), name='product_delete'),
    path('upcomming-auction/', CommingAuctionProductView.as_view(),
         name="upcomming auction"),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
