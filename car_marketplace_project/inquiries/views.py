from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Inquiry
from .serializers import InquirySerializer, InquiryCreateSerializer, InquiryListSerializer
from .permissions import IsBuyerOfInquiryOrSellerOfCarOrAdmin
from users.permissions import IsSeller 
from rest_framework.routers import DefaultRouter
from rest_framework import serializers


class InquiryViewSet(viewsets.ModelViewSet):
    serializer_class = InquiryListSerializer
    filterset_fields = ['status', 'car', 'buyer', 'seller']
    ordering_fields = ['inquiry_date', 'status'] 

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff: # Admin sees all inquiries
                return Inquiry.objects.all()
            elif hasattr(user, 'is_seller') and user.is_seller: # Seller sees inquiries related to their cars or sent to them
                return Inquiry.objects.filter(Q(seller=user) | Q(car__seller=user)).distinct()
            else: # Regular user (buyer) sees only inquiries they sent
                return Inquiry.objects.filter(buyer=user)
        return Inquiry.objects.none() # Guests/unauthenticated users see no inquiries

    def get_serializer_class(self):
        # Use InquiryCreateSerializer for creation
        if self.action == 'create':
            return InquiryCreateSerializer
        # Use InquirySerializer for detailed retrieve (single object)
        elif self.action == 'retrieve':
            return InquirySerializer
        return InquiryListSerializer

    def get_permissions(self):
        if self.action == 'create':
           self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsBuyerOfInquiryOrSellerOfCarOrAdmin]
        else: 
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        car = serializer.validated_data['car']
        if not car.is_approved:
            raise serializers.ValidationError("Cannot send an inquiry for an unapproved car.")

        # Set the buyer to the requesting user and the seller to the car's seller
        serializer.save(buyer=self.request.user, seller=car.seller)

    def perform_update(self, serializer):
        # Only allow status update for sellers/admins, not message or other fields that a buyer might try to change
        # The custom permission IsBuyerOfInquiryOrSellerOfCarOrAdmin handles who can update.
        # This additional check prevents message updates by unauthorized users even if they bypass the permission.
        if self.request.user.is_seller or self.request.user.is_staff:
            # If the user is a seller or admin, allow status updates.
            # Prevent them from changing the message field directly through update.
            if 'message' in serializer.validated_data and self.request.method in ['PUT', 'PATCH']:
                raise serializers.ValidationError({"message": "Message cannot be updated."})
            serializer.save()
        else:
            # For buyers, the custom permission already restricts updates (they can't update unless they are seller/admin)
            # This line might be redundant if the permission handles it, but good for explicit clarity.
            raise permissions.PermissionDenied("You do not have permission to update this inquiry.")