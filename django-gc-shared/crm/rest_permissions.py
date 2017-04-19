# -*- coding: utf-8 -*-

from rest_framework import permissions


class CanGetNewCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.crm_manager.can_request_new_customers
