# coding=utf-8
from rest_framework import permissions


class AccountIsActive(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return not (obj.is_deleted or obj.is_archived)
