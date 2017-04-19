# coding=utf-8
from rest_framework import permissions


class OnlySelfUserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
