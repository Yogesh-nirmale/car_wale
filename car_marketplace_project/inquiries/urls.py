# D:\car_showroom_project\car_marketplace_project\inquiries\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InquiryViewSet

router = DefaultRouter()
# THIS IS THE CRITICAL CHANGE: Added 'inquiries' as the path prefix and 'basename'
router.register(r'inquiries', InquiryViewSet, basename='inquiry')

urlpatterns = [
    path('', include(router.urls)),
]