from rest_framework import permissions


class Admin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class Guest(permissions.BasePermission):
    def has_permission(self, request, view):
        return True


class AuthUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_blocked

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author and not request.user.is_blocked
