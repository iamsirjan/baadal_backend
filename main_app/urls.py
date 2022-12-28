from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterView, RetrieveUserView, ProductViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user', RetrieveUserView.as_view(), name="retrieve_user"),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('product/', ProductViewSet.as_view(), name="product")

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
