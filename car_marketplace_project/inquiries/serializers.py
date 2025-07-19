# D:\car_showroom_project\car_marketplace_project\inquiries\serializers.py

from rest_framework import serializers
from .models import Inquiry
from users.serializers import UserProfileSerializer
from cars.serializers import CarSerializer # Ensure this is CarSerializer (the general one)

class InquirySerializer(serializers.ModelSerializer): # <--- NEW/RE-ADDED GENERIC INQUIRY SERIALIZER
    """
    General purpose Serializer for Inquiry, suitable for detail views and embedding.
    Includes related car, buyer, and seller details.
    """
    car_details = CarSerializer(source='car', read_only=True)
    buyer_details = UserProfileSerializer(source='buyer', read_only=True)
    seller_details = UserProfileSerializer(source='seller', read_only=True)

    class Meta:
        model = Inquiry
        fields = [
            'id', 'car', 'car_details', 'buyer', 'buyer_details',
            'seller', 'seller_details', 'message', 'inquiry_date', 'status'
        ]
        read_only_fields = '__all__' # All fields are read-only for this general view

class InquiryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new inquiry.
    Buyer is automatically set by the view.
    """
    class Meta:
        model = Inquiry
        fields = ['car', 'message']

class InquiryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing inquiries, including related data.
    """
    car_details = CarSerializer(source='car', read_only=True)
    buyer_details = UserProfileSerializer(source='buyer', read_only=True)
    seller_details = UserProfileSerializer(source='seller', read_only=True)

    class Meta:
        model = Inquiry
        fields = [
            'id', 'car', 'car_details', 'buyer', 'buyer_details',
            'seller', 'seller_details', 'message', 'inquiry_date', 'status'
        ]
        read_only_fields = [
            'id', 'buyer', 'seller', 'inquiry_date',
            'car_details', 'buyer_details', 'seller_details'
        ]