from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Brand, CarModel, Car, CarImage
from django.utils.html import format_html

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1 # Number of empty forms to display

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'brand', 'model', 'price', 'year', 'seller',
        'is_approved', 'created_at', 'view_images_link'
    )
    list_filter = ('is_approved', 'brand', 'model', 'fuel_type', 'transmission', 'condition', 'year')
    search_fields = ('title', 'description', 'seller__username', 'brand__name', 'model__name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [CarImageInline]
    actions = ['approve_selected_cars', 'reject_selected_cars']
    raw_id_fields = ('brand', 'model', 'seller') # For easier selection if many brands/models/users

    fieldsets = (
        (None, {
            'fields': ('title', 'description', ('brand', 'model'), ('price', 'year'))
        }),
        ('Specifications', {
            'fields': (('fuel_type', 'transmission'), ('mileage', 'engine_type'), 'condition')
        }),
        ('Seller Information', {
            'fields': ('seller',),
            'description': 'This car is listed by this user.'
        }),
        ('Approval Status', {
            'fields': ('is_approved',),
            'description': 'Admin approval is required for the car to be visible on the public site.'
        }),
    )

    def view_images_link(self, obj):
        if obj.images.exists():
            return format_html('<a href="{}">View Images ({})</a>',
                               obj.get_admin_url(), # Placeholder, you might need a custom URL
                               obj.images.count())
        return "No Images"
    view_images_link.short_description = "Images"


    @admin.action(description="Approve selected cars")
    def approve_selected_cars(self, request, queryset):
        updated_count = queryset.update(is_approved=True)
        self.message_user(request, f"{updated_count} cars successfully approved.")

    @admin.action(description="Reject selected cars")
    def reject_selected_cars(self, request, queryset):
        updated_count = queryset.update(is_approved=False)
        self.message_user(request, f"{updated_count} cars successfully rejected.")

# Custom admin site URL for Car images - needs to be handled in frontend/admin
# This is a conceptual link. For Django admin itself, images are displayed in the inline.
# For a public gallery, it would be a frontend concern.
    def get_admin_url(self, obj):
        # This is a placeholder for a hypothetical view that shows all images for a car.
        # In a real app, you might have a custom admin view for this or rely on the inline.
        # For simplicity, we'll just link to the change form for now.
        return f"/admin/cars/car/{obj.id}/change/"


admin.site.register(Brand)
admin.site.register(CarModel)
# CarImage is managed via Car inline, no need to register separately unless for direct manipulation
# admin.site.register(CarImage)