# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from crm.models import CallInfo, CRMComment, PlannedCall, LinkRequest, ReceptionCall,\
                       PersonalManager, FinancialDepartmentCall, CRMAccess, ManagerReassignRequest, Notification
from geobase.models import Country, Region
from shared.admin import BaseAdmin


class CRMAccessAdmin(BaseAdmin):
    list_display = ('user', 'active', 'reception_access', 'staff_access', 'view_manager',
                    'view_agent_code', 'ib_access', 'regional_access_demo', '_allowed_ips')
    list_filter = ('active', 'reception_access', 'staff_access', 'view_manager',
                   'view_agent_code', 'ib_access', 'regional_access_demo')
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email",
                     "user__accounts__mt4_id")
    raw_id_fields = ('user',)


class CallInfoAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date', 'comment', 'caller')
    date_hierarchy = "date"
    search_fields = ('customer__grand_user__accounts__mt4_id', "customer__grand_user__username",
                     "customer__grand_user__first_name", "customer__grand_user__last_name",)
    readonly_fields = ('customer', 'caller')


class LinkRequestAdmin(admin.ModelAdmin):
    list_display = ('account', 'customer', 'comment',  'author', 'date', 'automatic', 'processed', 'completed')
    date_hierarchy = "date"
    search_fields = ('account__mt4_id', 'author__email', "customer__grand_user__username",
                     "customer__grand_user__first_name", "customer__grand_user__last_name",)
    readonly_fields = ('customer', 'author', 'account')
    actions = ('mark_as_processed', 'mark_as_completed')

    def mark_as_processed(self, request, queryset):
        for item in queryset:  # Using full procedure to trigger save() etc.
            item.processed = True
            item.save()
    mark_as_processed.short_description = u"Отметить как обработанные"

    def mark_as_completed(self, request, queryset):
        queryset.update(completed=True)
    mark_as_completed.short_description = u"Отметить как исполненные"


class PlannedCallInfoAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date')
    date_hierarchy = "date"
    search_fields = ('customer__grand_user__accounts__mt4_id', "customer__grand_user__username",
                     "customer__grand_user__first_name", "customer__grand_user__last_name",)
    readonly_fields = ('customer', 'manager')


class CRMCommentAdmin(admin.ModelAdmin):

    date_hierarchy = "creation_ts"
    list_display = ('customer', 'text', 'creation_ts', 'author')
    search_fields = ('customer__grand_user__accounts__mt4_id', "customer__grand_user__username",
                     "customer__grand_user__first_name", "customer__grand_user__last_name",)
    readonly_fields = ('customer', 'author')


class ReceptionCallAdmin(admin.ModelAdmin):
    list_display = ('switch_to', 'name')
    list_filter = ('switch_to', 'applied')


class FinancialDepartmentCallAdmin(admin.ModelAdmin):
    list_display = ('date', 'name', 'callee')


class PersonalManagerAdmin(admin.ModelAdmin):
    list_display = ('user_str', 'office', 'is_active',
                    'can_request_new_customers', 'can_be_auto_assigned', 'has_document_access',
                    'is_office_supermanager', 'sip_name', 'amo_id',
                    'assignment_params',
                    'allowed_ips', 'daily_limit')
    raw_id_fields = ('user',)
    readonly_fields = ['user_str', 'assignment_params']

    fieldsets = (
        (None, {
            'fields': ('user', 'user_str', 'office', 'amo_id')
        }),
        (_("Permissions"), {
            'fields': ('is_office_supermanager', 'can_see_all_users', 'allowed_ips', 'daily_limit',
                       'has_document_access')
        }),
        (_("Telephony"), {
            'fields': ('sip_name', 'can_see_all_calls')
        }),
        (_("Shift time"), {
            'fields': ('worktime_start', 'worktime_end', 'force_tasks_full_day')
        }),
        (_("Clients assignment"), {
            'fields': ('can_request_new_customers', 'needs_call_check', 'can_be_auto_assigned',
                       'works_with_office_clients', 'ib_account',
                       'reassign_agent_code_to_office', 'languages',
                       'works_with_ib', 'country_state_names',
                       'assignment_params')
        }),
    )

    def user_str(self, obj):
        return obj.user.get_full_name()
    user_str.short_description = u"User"

    def is_active(self, obj):
        return obj.user.is_active
    is_active.admin_order_field = 'user__is_active'
    is_active.short_description = _("Is active")
    is_active.boolean = True

    def assignment_params(self, obj=None):
        if not obj:
            return ""
        if not(obj.user.is_active and obj.can_be_auto_assigned):
            return ""
        s = u""
        if obj.ib_account:
            s += u"Agent code %s. " % obj.ib_account
        if obj.country_state_names:
            # check regions and countries
            country_state_found = []
            for c in Country.objects.all():
                if c.name_ru in obj.country_state_names:
                    country_state_found.append(c.name_ru)
            for r in Region.objects.all():
                if r.name_ru in obj.country_state_names:
                    country_state_found.append(r.name_ru)

            s += u"Countries/regions: " + u",".join(country_state_found) + u". "
        if obj.works_with_office_clients:
            if obj.office and obj.office.is_our:
                s += u"Regional office %s. " % obj.office
            elif obj.office and not obj.office.is_our:
                s += u"Partner's office %s(код %s). " % (obj.office, obj.office.get_agent_codes())

        s += u"Languages: %s" % obj.languages
        if obj.works_with_ib:
            s += u"Partner's clients. "
        return s or u"No clients :("
    assignment_params.short_description = u"Gets assigned to"


class ManagerReassignRequestAdmin(admin.ModelAdmin):
    actions = ['make_accepted']
    list_display = ('status', 'id', 'author_str', 'user_with_crm_link',
                    'previous_manager', 'new_manager', 'comment')
    list_filter = (
        'status',
        ('author', admin.RelatedOnlyFieldListFilter),
        ('previous', admin.RelatedOnlyFieldListFilter),
        ('assign_to', admin.RelatedOnlyFieldListFilter),
    )

    readonly_fields = ('id', 'author_str',
                       'user_with_crm_link', 'user_agent_code',
                       'user_location',
                       'current_manager', 'new_manager', 'previous_manager',
                       'comment', 'created_at', 'updated_at', 'completed_by')

    search_fields = ('user__pk', 'user__username', 'user__email', 'user__accounts__mt4_id')

    fieldsets = (
        (None, {
            'fields': ('id', 'author_str', 'current_manager', 'new_manager', 'comment', 'created_at')
        }),
        (_("Client data"), {
            'fields': ('user_with_crm_link', 'user_agent_code', 'user_location')
        }),
        (_("Decision"), {
            'fields': ('assign_to', 'status', 'reject_reason', 'updated_at', 'completed_by', 'previous_manager')
        }),
    )

    radio_fields = {"status": admin.VERTICAL}

    date_hierarchy = 'created_at'

    def status_bool(self, obj):
        return None if obj.status == 'new' else obj.status == 'accepted'
    status_bool.boolean = True
    status_bool.short_description = _("Status")

    #
    def author_str(self, obj):
        return unicode(obj.author.crm_manager)
    author_str.short_description = _("Author")

    # client info
    def user_with_crm_link(self, obj):
        return mark_safe(
            u"{0} <a href='{1}' target='_blank'><b>CRM</b></a>".format(obj.user.get_full_name(), obj.user_crm_url))
    user_with_crm_link.short_description = _("Client")

    def user_agent_code(self, obj):
        return obj.user.profile.agent_code
    user_agent_code.short_description = _("Agent code")

    def user_location(self, obj):
        profile = obj.user.profile
        addr = map(unicode, filter(lambda x: x, [
            profile.country, profile.state, profile.city
        ]))
        return u', '.join(addr)
    user_location.short_description = _("Address")

    def current_manager(self, obj):
        man = obj.current
        return unicode(man.crm_manager) if man else _("Empty")
    current_manager.short_description = _("Current manager")

    def new_manager(self, obj):
        return unicode(obj.assign_to.crm_manager) if obj.assign_to else _("Empty")
    new_manager.short_description = _("Requested manager")

    def previous_manager(self, obj):
        return unicode(obj.previous.crm_manager) if obj.previous else _("Empty")
    previous_manager.short_description = _("Previous manager")

    def queryset(self, request):
        qs = super(ManagerReassignRequestAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            manager = request.user.crm_manager
        except ObjectDoesNotExist:
            return qs.filter(id=None)  # fuq u

        if not manager.is_office_supermanager:
            return qs.filter(id=None)  # fuq u

        if manager.office:
            return qs.filter(author__in=manager.office.managers.all())

        # supermanagers of main office should be able to view all requests
        else:
            return qs

    def has_add_permission(self, request):
        return False

    def make_accepted(self, request, queryset):
        for i in queryset.filter(assign_to__isnull=False).exclude(status__in=['accepted', 'rejected']):
            i.accept(request.user, notify=True)
            i.save()
    make_accepted.short_description = _("Accept all requests which specify new manager")

    def save_model(self, request, obj, form, change):
        # if model instance was changed and previosly it was new issue
        if 'status' in obj.changes and obj.changes['status'][0] == 'new':
            if form.cleaned_data['status'] == 'accepted':
                obj.accept(request.user, notify=True, completed_by_ip=request.META["REMOTE_ADDR"])
            elif form.cleaned_data['status'] == 'rejected':
                obj.reject(request.user, reason=form.cleaned_data['reject_reason'], notify=True)
            obj.save()

        # save only if we have any changes
        # to preserve updated_at datetime
        if obj.changes:
            super(ManagerReassignRequestAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        # disable edit of possible fields if request is completed
        if obj.is_completed:
            return self.readonly_fields + ('status', 'reject_reason', 'assign_to')
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # fix user choise field to show only managers
        # and use unicode() of crm_manager for labels
        if db_field.name == "assign_to":
            kwargs["queryset"] = User.objects.exclude(crm_manager=None) \
                .filter(is_active=True) \
                .order_by('-crm_manager__office', 'username')
        field = super(ManagerReassignRequestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "assign_to":
            field.label_from_instance = lambda obj: obj.get_full_name()
        return field


class NotificationAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('created_at', 'type', 'user', 'text', 'is_sent', 'sent_at')


admin.site.register(Notification, NotificationAdmin)
admin.site.register(ManagerReassignRequest, ManagerReassignRequestAdmin)
admin.site.register(CallInfo, CallInfoAdmin)
admin.site.register(CRMComment, CRMCommentAdmin)
admin.site.register(PlannedCall, PlannedCallInfoAdmin)
admin.site.register(LinkRequest, LinkRequestAdmin)
admin.site.register(ReceptionCall, ReceptionCallAdmin)
admin.site.register(PersonalManager, PersonalManagerAdmin)
admin.site.register(FinancialDepartmentCall, FinancialDepartmentCallAdmin)
admin.site.register(CRMAccess, CRMAccessAdmin)
