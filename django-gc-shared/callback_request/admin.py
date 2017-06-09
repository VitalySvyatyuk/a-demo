from django.contrib import admin
from shared.admin import BaseAdmin
from models import CallbackRequest


class CallbackAdmin(BaseAdmin):
    list_display = ('id', 'phone_number', 'creation_ts', 'request_processed', 'internal_comment')

admin.site.register(CallbackRequest, CallbackAdmin)
