from django.contrib import admin
from sms.models import SMSMessage


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'receiver_number', 'backend')
    readonly_fields = ('backend', 'receiver_number', 'timestamp', 'code', 'sender_number',
                       'text')
    search_fields = ('receiver_number', )
