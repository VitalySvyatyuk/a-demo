# coding=utf-8

from rest_framework.permissions import BasePermission


class IsOtpBinded(BasePermission):
    """
    Allows access if OTP is binded
    """
    def has_permission(self, request, view):
        return not request.user.profile.lost_otp