# coding: utf-8
from django import forms
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from models import NotificationSettings, Notification, MessageTemplate


class NotificationSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("language", "default_notification_template",),
        }),
    )

    list_display = ('language', 'default_notification_template')


class NotificationAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NotificationAdminForm, self).__init__(*args, **kwargs)
        self.fields['html'].widget = CKEditorWidget(config_name="default")
    
    class Media:
        js = ('sms/js/sms_counter.js', )


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'app_name', 'language', 'published', 'duplicate_by_sms')
    list_filter = ('notification_type', 'language', 'published', 'duplicate_by_sms')
    form = NotificationAdminForm

    def app_name(self, object):
        from notification.models import NotificationTypesRegister
        return NotificationTypesRegister.app_names[object.notification_type]


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'language')
    list_filter = ('language', )


admin.site.register(MessageTemplate, TemplateAdmin)
admin.site.register(NotificationSettings, NotificationSettingsAdmin)
admin.site.register(Notification, NotificationAdmin)
