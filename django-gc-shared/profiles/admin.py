# -*- coding: utf-8 -*-
import json

from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from jsonfield.utils import default

from platforms.models import TradingAccount
from profiles.models import UserDocument, UserProfile
from shared.admin import BaseAdmin, with_link, ViewLoggingAdmin
from shared.utils import descr


class AccountInline(admin.TabularInline):
    can_delete = False
    model = TradingAccount
    exclude = ("password",)
    readonly_fields = ("mt4_id", "group")


class UserProfileAdmin(ViewLoggingAdmin):

    list_display = ("name", "country", "city", "language", 'middle_name')
    search_fields = ("user__username", "user__first_name", "user__last_name",
                     "user__accounts__mt4_id", "user__requisits__purse", )
    fieldsets = (
        (_("Personal"), {
            "fields": ('full_name', "user", ("last_name", "first_name", "middle_name"), "email_verified", "birthday")
        }),
        (_("Contacts"), {
            "fields": (
                # "skype", "icq", "phone_home", "phone_work",
                "phone_mobile", "email"
            )
        }),
        (_("Location"), {
            "fields": ("country", "city", "state", "address")
        }),
        (_("Other"), {
            "fields": ("manager", "agent_code"),
        }),

        (_("ARUM financial information"), {
            'classes': ('wide', 'extrapretty'),
            "fields": ("allow_open_invest", "us_citizen",  "tax_residence", 'net_capital', 'annual_income',
                       "financial_commitments", 'account_turnover', 'purpose', 'tin',
                       )
        }),
        (_("Type of your activity"), {
            'classes': ('wide', 'extrapretty'),
            "fields": ('nature_of_biz', "source_of_funds", "employment_status", 'education_level',)
        }),
        (_("Trading experience"), {
            'classes': ('wide', 'extrapretty'),
            "fields": ('investment_undertaking', 'derivative_instruments',
                       'forex_instruments', 'transferable_securities'
                       )
        }),
    )

    readonly_fields = ("user", "manager", "agent_code",
                       "first_name", "middle_name", "last_name", 'email', 'full_name')

    # Prevent from accidental profile deletion: delete users instead!
    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm("profiles.can_change_agent_code_manager"):
            return "user", "first_name", "middle_name", "last_name", 'email', 'full_name'
        return super(UserProfileAdmin, self).get_readonly_fields(request, obj)

    @descr(_("First name"))
    def first_name(self, object):
        return unicode(object.user.first_name)

    @descr(_("Surname"))
    def last_name(self, object):
        return unicode(object.user.last_name)

    @descr()
    def name(self, obj):
        return unicode(obj)

    @descr(_("Email"))
    def email(self, object):
        return unicode(object.user.email)

    def save_model(self, request, obj, form, change):

        if 'manager' in obj.changes:
            obj.manager_auto_assigned = False

        return super(UserProfileAdmin, self).save_model(request, obj, form, change)


class UnicodeJSONWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ""
        if not isinstance(value, basestring):
            value = json.dumps(value, indent=4, default=default, ensure_ascii=False)
        return super(UnicodeJSONWidget, self).render(name, value, attrs)


class UserDocumentAdminForm(forms.ModelForm):
    class Meta:
        model = UserDocument
        exclude = ()
        widgets = {
            'fields': UnicodeJSONWidget
        }


class UserDocumentAdmin(BaseAdmin):
    form = UserDocumentAdminForm
    list_display = ('id', 'user_with_link', 'file_with_link', 'description', 'creation_ts')
    fields = ('user', 'name', 'file', 'description', 'fields', 'is_deleted', 'is_rejected')
    search_fields = ('user__username', 'user__email', 'description')
    raw_id_fields = ('user',)
    list_filter = ('name',)
    user_with_link = with_link("user", u"User")

    def file_with_link(self, obj):
        return "<a href='/uploads/%s'>%s</a>" % (obj.file, obj.get_name_display())
    file_with_link.allow_tags = True
    file_with_link.short_description = u"File"


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserDocument, UserDocumentAdmin)
