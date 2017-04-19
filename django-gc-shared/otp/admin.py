# -*- coding: utf-8 -*-

from django.contrib import admin

from otp.models import OTPDevice, SMSDevice, VoiceDevice
from shared.admin import with_link, ViewLoggingAdmin


class OTPDeviceAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'is_deleted'],
        }),
        ('Configuration', {
            'fields': ['key', 'step', 't0', 'digits', 'tolerance'],
        }),
        ('State', {
            'fields': ['drift'],
        }),
    ]
    raw_id_fields = ("user", )

    radio_fields = {'digits': admin.HORIZONTAL}
    search_fields = ("user__username", "user__accounts__mt4_id", "user__id")
    list_filter = ("is_deleted",)
    list_display = ('id', 'user_link', 'creation_ts', "is_deleted")
    ordering = ('-creation_ts',)

    user_link = with_link("user", u"User")


class SMSDeviceAdmin(ViewLoggingAdmin):

    fieldsets = [
        ('Identity', {
            'fields': ['user', 'phone_number', 'is_deleted'],
        }),
    ]
    raw_id_fields = ("user", )
    readonly_fields = "phone_number",
    search_fields = ("user__username", "user__accounts__mt4_id", "user__id")
    list_filter = ("is_deleted",)
    list_display = ('id', 'user_link', 'creation_ts', "is_deleted")
    ordering = ('-creation_ts',)

    user_link = with_link("user", u"User")


class VoiceDeviceAdmin(ViewLoggingAdmin):

    fieldsets = [
        ('Identity', {
            'fields': ['user', 'phone_number', 'is_deleted'],
        }),
    ]
    raw_id_fields = ("user", )
    readonly_fields = "phone_number",
    search_fields = ("user__username", "user__accounts__mt4_id", "user__id")
    list_filter = ("is_deleted",)
    list_display = ('id', 'user_link', 'creation_ts', "is_deleted")
    ordering = ('-creation_ts',)

    user_link = with_link("user", u"User")


admin.site.register(OTPDevice, OTPDeviceAdmin)
admin.site.register(SMSDevice, SMSDeviceAdmin)
admin.site.register(VoiceDevice, VoiceDeviceAdmin)
