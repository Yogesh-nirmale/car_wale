# D:\car_showroom_project\car_marketplace_project\cars\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, CarModelViewSet, CarViewSet

router = DefaultRouter()
# Adjusted to match frontend's /api/cars/brands/ request
router.register(r'cars/brands', BrandViewSet, basename='brand')
# Adjusted to match frontend's /api/cars/models/ (for consistency if needed later)
router.register(r'cars/models', CarModelViewSet, basename='carmodel')
# CRITICAL FIX: Adjusted to match frontend's /api/cars/cars/ request for the main car list
router.register(r'cars/cars', CarViewSet, basename='car')

urlpatterns = [
    path('', include(router.urls)),
]