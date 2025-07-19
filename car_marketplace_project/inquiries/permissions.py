from rest_framework import permissions

class IsBuyerOfInquiryOrSellerOfCarOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.buyer == request.user or obj.car.seller == request.user or request.user.is_staff

        if request.user.is_authenticated:
            if request.user.is_staff:
                return True
            if obj.buyer == request.user:
                return True
            if obj.car.seller == request.user:
                return True
        
        return False 