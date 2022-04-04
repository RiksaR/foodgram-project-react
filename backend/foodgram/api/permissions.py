from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS
                    or request.user.is_staff)


class RecipePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS
                    or request.user.is_authenticated or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        return bool(request.method in permissions.SAFE_METHODS
                    or obj.author == request.user or request.user.is_staff)


class SubscriptionListPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS and
                    (request.user.is_authenticated or request.user.is_staff))

    def has_object_permission(self, request, view, obj):
        return bool(request.method in permissions.SAFE_METHODS
                    and obj == request.user)
