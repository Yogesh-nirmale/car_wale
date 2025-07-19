# D:\car_showroom_project\car_marketplace_project\cars\serializers.py

from rest_framework import serializers
from .models import Car, Brand, CarModel, CarImage
from users.serializers import UserProfileSerializer

# Serializers for nested objects (Brand, CarModel, CarImage)
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class CarModelSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), source='brand', write_only=True)

    class Meta:
        model = CarModel
        fields = ['id', 'brand', 'brand_id', 'name']

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['uploaded_at']

# General Purpose Car Serializer (for embedding in other serializers)
class CarSerializer(serializers.ModelSerializer): # <--- RE-ADDED THIS GENERAL PURPOSE SERIALIZER
    """
    General purpose Car Serializer for embedding in other serializers or simple display.
    Includes nested seller details, brand, model, and images for comprehensive read-only view.
    """
    seller_details = UserProfileSerializer(source='seller', read_only=True)
    images = CarImageSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    model = CarModelSerializer(read_only=True)

    class Meta:
        model = Car
        fields = [
            'id', 'seller', 'seller_details', 'title', 'brand', 'model',
            'price', 'fuel_type', 'year', 'transmission', 'condition', 'mileage',
            'engine_type', 'description', 'is_approved', 'created_at', 'updated_at', 'images'
        ]
        read_only_fields = '__all__' # All fields are read-only for this general purpose serializer

# Specific Car Serializers for cars app's own views (List, Detail, Create/Update)
class CarListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing cars, with essential information.
    """
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = [
            'id', 'title', 'brand_name', 'model_name', 'year', 'price',
            'mileage', 'fuel_type', 'transmission', 'condition',
            'seller_username', 'is_approved', 'main_image_url'
        ]

    def get_main_image_url(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return self.context['request'].build_absolute_uri(first_image.image.url)
        return None

class CarDetailSerializer(serializers.ModelSerializer): # <--- REMAINING FOR DETAIL VIEW IN CARS APP
    """
    Detailed Serializer for retrieving a single Car object within the cars app.
    It can be the same as CarSerializer for simplicity, or slightly different.
    """
    seller_details = UserProfileSerializer(source='seller', read_only=True)
    images = CarImageSerializer(many=True, read_only=True) 
    brand = BrandSerializer(read_only=True)
    model = CarModelSerializer(read_only=True)

    class Meta:
        model = Car
        fields = [
            'id', 'seller', 'seller_details', 'title', 'brand', 'model',
            'price', 'fuel_type', 'year', 'transmission', 'condition', 'mileage',
            'engine_type', 'description', 'is_approved', 'created_at', 'updated_at', 'images'
        ]
        read_only_fields = '__all__'


class CarCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Car objects in the cars app.
    Allows specifying related objects by their primary keys (IDs).
    """
    brand_id = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), source='brand', write_only=True)
    model_id = serializers.PrimaryKeyRelatedField(queryset=CarModel.objects.all(), source='model', write_only=True)

    class Meta:
        model = Car
        fields = [
            'id', 'title', 'brand_id', 'model_id',
            'price', 'fuel_type', 'year', 'transmission', 'condition', 'mileage',
            'engine_type', 'description'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        validated_data['is_approved'] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('seller', None)
        validated_data.pop('is_approved', None)
        return super().update(instance, validated_data)