from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q # For OR queries

from .models import Brand, CarModel, Car, CarImage
from .serializers import (
    BrandSerializer, CarModelSerializer,
    CarListSerializer, CarDetailSerializer, CarCreateUpdateSerializer,
    CarImageSerializer
)
from users.permissions import IsSeller, IsOwnerOrAdmin
from .filters import CarFilter

class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name']
    ordering_fields = ['name']

class CarModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CarModel.objects.all()
    serializer_class = CarModelSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['brand'] # Filter models by brand ID
    search_fields = ['name']
    ordering_fields = ['name']

class CarViewSet(viewsets.ModelViewSet):
    filter_class = CarFilter # Using custom filterset
    search_fields = ['title', 'description', 'brand__name', 'model__name']
    ordering_fields = ['price', 'year', 'created_at']

    def get_queryset(self):
        """
        Admins can see all cars.
        Sellers can see their own cars (approved or not).
        Regular users/guests can only see approved cars.
        """
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Car.objects.all()
        elif user.is_authenticated and user.is_seller:
            return Car.objects.filter(Q(is_approved=True) | Q(seller=user)).distinct()
        else:
            return Car.objects.filter(is_approved=True)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CarCreateUpdateSerializer
        elif self.action == 'retrieve':
            return CarDetailSerializer
        return CarListSerializer # Default for list

    def get_permissions(self):
        if self.action in ['create']:
            # Only authenticated sellers can create cars
            self.permission_classes = [permissions.IsAuthenticated, IsSeller]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only owner or admin can update/delete
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else:
            # List and retrieve are open to all (but only approved cars for guests)
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Ensure the creating user is set as the seller
        if not self.request.user.is_seller:
            raise permissions.PermissionDenied("Only sellers can add cars.")
        serializer.save(seller=self.request.user)

    @action(detail=False, methods=['get'])
    def compare(self, request):
        car_ids = request.query_params.get('ids')
        if not car_ids:
            return Response({"detail": "Please provide car IDs for comparison (e.g., ?ids=1,2,3)."}, status=status.HTTP_400_BAD_REQUEST)

        ids = [int(x) for x in car_ids.split(',') if x.strip().isdigit()]
        if not ids:
            return Response({"detail": "Invalid car IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        cars = Car.objects.filter(id__in=ids, is_approved=True)
        serializer = CarDetailSerializer(cars, many=True, context={'request': request})
        return Response(serializer.data)