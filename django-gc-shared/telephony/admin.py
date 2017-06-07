# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from telephony.models import ExternalAsteriskCDR, CallDetailRecord, VoiceMailCDR, PhoneUser


class ExternalCDRAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in ExternalAsteriskCDR._meta.get_fields()] + ['record']

    date_hierarchy = 'calldate'
    search_fields = ('src', 'dst', 'channel')
    list_display = ('calldate', 'clid', 'channel', 'dst', 'disposition', 'duration', 'userfield', 'file_with_link')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def record(self, obj):
        return format_html(
            '<audio controls>'
            '<source src="{0}" type="audio/wav">'
            '</audio>'
            '<a href="{0}">Download</a>',
            obj.get_record_path() or "")
    record.allow_tags = True

    def file_with_link(self, obj):
        return "<a href='%s'>%s</a>" % (obj.get_record_path(), obj.recordingfile)
    file_with_link.allow_tags = True
    file_with_link.short_description = u"Record"

admin.site.register(ExternalAsteriskCDR, ExternalCDRAdmin)


class CDRAdmin(admin.ModelAdmin):
    search_fields = (
        'user_a__username', 'user_a__email', 'user_b__username', 'user_b__email',
        'number_a', 'number_b', 'name_a', 'name_b', 'external_cdr_id')
    readonly_fields = [f.name for f in CallDetailRecord._meta.fields] + [
        'record', 'source_str', 'dest_str', 'a_with_crm_link', 'b_with_crm_link',
        'safe_number_a', 'safe_number_b', 'external_cdr_link']
    date_hierarchy = 'call_date'
    list_display = ('call_date', 'source_str', 'dest_str', 'price', 'file_with_link')
    fieldsets = (
        (None, {
            'fields': ('external_cdr_link', 'call_date', 'source_str', 'dest_str', 'record')
        }),

        (u'Information', {
            'fields': ('a_with_crm_link', 'b_with_crm_link', 'safe_number_a', 'safe_number_b', 'duration',
'disposition')
        }),
    )

    def external_cdr_link(self, obj):
        return u"<a href='{1}'>{0}</a>".format(
            obj.external_cdr_id,
            reverse('admin:telephony_externalasteriskcdr_change', args=(obj.external_cdr_id,)))
    external_cdr_link.allow_tags = True
    external_cdr_link.short_description = u"External record"

    def source_str(self, obj):
        return obj.source_str()
    source_str.short_description = u"Who"
    source_str.admin_order_field = 'user_a'

    def dest_str(self, obj):
        return obj.dest_str()
    dest_str.short_description = u"To"
    dest_str.admin_order_field = 'user_b'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def a_with_crm_link(self, obj):
        if obj.user_a:
            return u"{0} <a href='{1}' target='_blank'><b>CRM</b></a>".format(
                obj.user_a.get_full_name(),
                obj.user_a.profile.get_amo().get_url())
    a_with_crm_link.allow_tags = True
    a_with_crm_link.short_description = u"User A"

    def b_with_crm_link(self, obj):
        if obj.user_b:
            return u"{0} <a href='{1}' target='_blank'><b>CRM</b></a>".format(
                obj.user_b.get_full_name(),
                obj.user_b.profile.get_amo().get_url())
    b_with_crm_link.allow_tags = True
    b_with_crm_link.short_description = u"User B"

    def safe_number_a(self, obj):
        return obj.safe_number_a
    safe_number_a.short_description = u"Number А"

    def safe_number_b(self, obj):
        return obj.safe_number_b
    safe_number_b.short_description = u"Number B"

    def record(self, obj):
        return format_html(
            '<audio controls>'
            '<source src="{0}" type="audio/wav">'
            '</audio>'
            '<a href="{0}">Download</a>',
            obj.get_record_path() or "")
    record.allow_tags = True
    record.short_description = u"Record"

    def file_with_link(self, obj):
        return "<a href='%s'>%s</a>" % (obj.get_record_path(), obj.recording_file)
    file_with_link.allow_tags = True
    file_with_link.short_description = u"Record"

admin.site.register(CallDetailRecord, CDRAdmin)


class VoiceMailCDRAdmin(admin.ModelAdmin):
    search_fields = (
        'cdr__user_a__username', 'cdr__user_a__email', 'cdr__number_a', 'cdr__name_a')
    readonly_fields = [
        'cdr_link', 'call_date', 'source_str', 'record',
        'a_with_crm_link', 'number_a_sip_link', 'last_commented_by', 'is_manual']
    date_hierarchy = 'call_date'
    list_filter = ('is_manual',)
    list_display = ('call_date', 'source_str', 'is_manual', 'comment')
    fieldsets = (
        (None, {
            'fields': ('cdr_link', 'call_date', 'source_str', 'is_manual', 'record',)
        }),

        (u'Информация', {
            'fields': ('a_with_crm_link', 'number_a_sip_link')
        }),

        (u'Комментарий', {
            'fields': ('comment', 'last_commented_by')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def cdr_link(self, obj):
        return u"<a href='{1}'>{0}</a>".format(
            obj.cdr.external_cdr_id,  # external cdr id is more meaningfull
            reverse('admin:telephony_calldetailrecord_change', args=(obj.cdr_id,)))
    cdr_link.allow_tags = True
    cdr_link.short_description = u"Информация о записи"

    def source_str(self, obj):
        return obj.cdr.source_str()
    source_str.short_description = u"Кто"

    def a_with_crm_link(self, obj):
        if obj.cdr.user_a:
            return u"{0} <a href='{1}' target='_blank'><b>CRM</b></a>".format(
                obj.cdr.user_a.get_full_name(),
                obj.cdr.user_a.profile.get_amo().get_url())
    a_with_crm_link.allow_tags = True
    a_with_crm_link.short_description = u"Пользователь"

    def number_a_sip_link(self, obj):
        return u"{1} <a href='sip:{0}' target='_blank' title='{0}'><b>SIP</b></a>".format(
            obj.cdr.number_a,
            obj.cdr.safe_number_a)
    number_a_sip_link.allow_tags = True
    number_a_sip_link.short_description = u"Номер"

    def record(self, obj):
        return format_html(
            '<audio controls>'
            '<source src="{0}" type="audio/wav">'
            '</audio>'
            '<a href="{0}">Download</a>',
            obj.get_record_path() or "")
    record.allow_tags = True
    record.short_description = u"Запись"

    def save_model(self, request, obj, form, change):
        if 'comment' in obj.changes:
            obj.last_commented_by = request.user
            obj.save()
        super(VoiceMailCDRAdmin, self).save_model(request, obj, form, change)

admin.site.register(VoiceMailCDR, VoiceMailCDRAdmin)


class PhoneUserAdmin(admin.ModelAdmin):
    list_display = ("login", "office", "queue", "enabled", "sync")
    search_fields = ("login", "office")
    list_filter = ("enabled", "queue")

admin.site.register(PhoneUser, PhoneUserAdmin)