from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('car', 'buyer', 'seller', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'car__brand', 'car__model', 'seller')
    search_fields = ('message', 'buyer__username', 'seller__username', 'car__title')
    readonly_fields = ('buyer', 'seller', 'car', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('car', 'buyer', 'seller', 'message')
        }),
        ('Status Information', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )