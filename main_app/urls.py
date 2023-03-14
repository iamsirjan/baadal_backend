from django.urls import path
from .views import GETKYCAPIViewBYId, KYCUpdateView, KycViewSet, ProductFilterViewSet, RegisterView, RetrieveUserView, ProductViewSet, ProductDeleteView,AssignProductView,BiddingViewSet,CommingAuctionProductView, VerifyKYCView
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
    path('bidding/', BiddingViewSet.as_view(),
         name="bidding"),

     path('assign-product/<int:id>/', AssignProductView.as_view(),
         name="bidding"),
   
    path('kyc/', KycViewSet.as_view(), name="KYC"),
    path('kyc/<int:user_id>/verify/', VerifyKYCView.as_view(), name='verify_kyc'),
    path('kyc/<int:id>', KYCUpdateView.as_view(), name='update kyc'),
     path('kycbyuser/<int:user_id>', GETKYCAPIViewBYId.as_view(), name=' kyc by user id '),


]
