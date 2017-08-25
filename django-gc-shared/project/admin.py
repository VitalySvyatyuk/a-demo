#coding=utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.util import flatten_fieldsets
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


class CustomUserAdmin(UserAdmin):

    list_display = ("id", "email", "phone_mobile", "first_name", "last_name")
    search_fields = ("username", "first_name", "last_name", "email", "accounts__mt4_id")

    _readonly_fields = []  # Default fields that are readonly for everyone.

    date_hierarchy = 'date_joined'
    actions = ["reset_otp"]

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self._readonly_fields)
        if request.user.is_staff and not request.user.is_superuser:
            if obj.is_superuser:
                # Prevent a staff user from editing anything of a superuser.
                readonly.extend(flatten_fieldsets(self.declared_fieldsets))
            else:
                # Prevent a non-superuser from editing sensitive security-related fields.
                readonly.extend(['is_staff', 'is_superuser', 'user_permissions', 'groups'])
        return readonly

    def user_change_password(self, request, id, form_url=''):
        # Disallow a non-superuser from changing the password of a superuser.
        user = get_object_or_404(self.model, pk=id)
        if not request.user.is_superuser and user.is_superuser:
            raise PermissionDenied
        return super(CustomUserAdmin, self).user_change_password(request, id)

    def phone_mobile(self, obj):
        return obj.profile.phone_mobile

    def get_search_results(self, request, queryset, search_term):

        queryset, use_distinct = super(CustomUserAdmin, self).get_search_results(request, queryset, search_term)
        queryset |= self.model.objects.filter(profile__phone_mobile__icontains=search_term)

        return queryset, use_distinct

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)