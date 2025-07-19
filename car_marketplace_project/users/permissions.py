from rest_framework import permissions

class IsSeller(permissions.BasePermission):
    """
    Custom permission to only allow sellers to perform actions.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_seller

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or an admin to edit/delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet or admin.
        return obj.seller == request.user or request.user.is_staff