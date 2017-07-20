# -*- coding: utf-8 -*-
from django.contrib import messages

from django.contrib.admin import TabularInline, site
from django.contrib.admin.views.main import ChangeList
from django.db.models import Q
from django.template.defaultfilters import linebreaks
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from shared.admin import with_link, BaseAdmin, short_descr

from issuetracker.models import *
from profiles.models import UserProfile
from notification import models as notification

# Inlines.
from shared.utils import descr


class PermissiveTabularInline(TabularInline):
    """
    Allows to add/change/delete inlines without corresponding permissions

    (i.e. emulates Django<1.4 behavior)
    """
    def has_add_permission(self, *args, **kwargs):
        return True

    def has_change_permission(self, *args, **kwargse):
        return True

    def has_delete_permission(self, *args, **kwargs):
        return True


class IssueCommentAdmin(PermissiveTabularInline):
    model = IssueComment
    extra = 1
    #TODO: add creation_ts to display here
    readonly_fields = ["user"]
    fields = ("user", "text")


class IssueAttachmentAdmin(PermissiveTabularInline):
    model = IssueAttachment
    extra = 3
    readonly_fields = ["user"]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        obj.save()


class IssueHistoryAdmin(PermissiveTabularInline):
    model = IssueChangeHistory
    extra = 0
    readonly_fields = ["user", "text"]


# Admins.

#TODO: restrict changing of other"s inlines if not enough perms. Show disabled
class IssueAdmin(BaseAdmin):
    date_hierarchy = "creation_ts"
    list_display = [
        "id", "author_with_link", 'user_email', 'user_phone', "title", "text", "assignee_with_link",
        "department", "creation_ts", "status",
    ]
    list_filter = ["creation_ts", "status", "deadline"]
    ordering = ["-creation_ts"]
    search_fields = ["title", "text", "author__email"]
    actions = ["make_closed", "make_rejected"]

    fieldsets = [
        (None, {
            "fields": ("status", "author_with_link", 'user_email', 'user_phone', "assignee",
                       "department", "deadline", "title", "html", "internal_comment",
                       "internal_html")
        })
    ]
    readonly_fields = ["author_with_link", "title", "html", "internal_html", 'user_phone', 'user_email']
    inlines = (IssueAttachmentAdmin,
               IssueCommentAdmin,
               IssueHistoryAdmin)

    def user_email(self, obj):
        try:
            return User.objects.get(username=obj.author).email
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return

    def user_phone(self, obj):
        try:
            return UserProfile.objects.get(user=obj.author).phone_mobile
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return

    def author_with_link(self, obj):
        profile = obj.author.profile
        return u"<span style='{0}'>{1}</span> <b><a href='{2}'>Admin</a></b>".format(
            '',
            obj.author.get_full_name(),
            get_admin_url(profile)
        )
    author_with_link.short_description = _(u"Author")
    author_with_link.allow_tags = True
    author_with_link.admin_order_field = 'author'

    user_email.short_description = _(u"Email")

    user_phone.short_description = _(u"Phone")

    def assignee_with_link(self, obj):
        if obj.assignee:
            return '<a href="%s">%s</a>' % (get_admin_url(obj.assignee.profile), obj.assignee)
        else:
            return ""
    assignee_with_link.allow_tags = True

    # This is to automatically set the user on all the inlines
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, IssueComment)\
            or isinstance(instance, IssueAttachment)\
            or isinstance(instance, IssueChangeHistory):
                if not instance.user_id:
                    instance.user = request.user
                instance.save()

    def get_queryset(self, request):
        qs = super(IssueAdmin, self).get_queryset(request)
        if not request.user.has_perm('issuetracker.can_access_all_issues'):
            qs = qs.filter(
                Q(assignee=request.user) |
                (Q(assignee__isnull=True) & Q(department__in=request.user.groups.all())),
            )
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assignee":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super(IssueAdmin, self).\
            formfield_for_foreignkey(db_field, request, **kwargs)

    @descr(_("Mark select issues as closed"))
    def make_closed(self, request, queryset):
        queryset.update(status="closed")

    @descr(_("Mark select issues as rejected"))
    def make_rejected(self, request, queryset):
        queryset.update(status="rejected")

    @descr(_("Text"))
    def html(self, obj):
        return linebreaks(obj.text)

    @descr(_("Internal description"))
    def internal_html(self, obj):
        return linebreaks(obj.internal_description)


class GenericIssueAdmin(IssueAdmin):

    def get_changelist(self, request, **kwargs):
        class IssueChangeList(ChangeList):
            def url_for_result(self, result):
                return result.get_admin_url()
        return IssueChangeList


class AccountDisabledAdmin(IssueAdmin):
    readonly_fields = IssueAdmin.readonly_fields + ["account"]


class InternalTransferIssueAdmin(IssueAdmin):
    exclude = ("sender", )
    readonly_fields = IssueAdmin.readonly_fields + [
        "sender_with_link", "recipient", "amount"
    ]
    actions = ["make_transfer"]

    sender_with_link = with_link("sender")
    get_queryset = BaseAdmin.get_queryset

    @short_descr(_("Make transaction"))
    def make_transfer(self, request, qs):
        from transfers.forms import InternalTransferForm
        for issue in qs:
            form = InternalTransferForm(request=request, internal=True, data={
                "sender": issue.sender.id,
                "recipient_manual": issue.recipient,
                "amount": issue.amount,
                "currency": issue.currency,
                "mode": "manual",
            })
            if form.is_valid() and form.save():
                issue.status = "closed"
                issue.save()
            else:
                from itertools import chain
                messages.error(
                    request,
                    u"Failed to process request #%s: %s" % (issue.id, "; ".join(map(unicode, chain(*form.errors.values()))))
                )

    @descr(_("Mark select issues as rejected"))
    def make_rejected(self, request, queryset):
        super(self.__class__, self).make_rejected(request, queryset)
        for q in queryset:
            notification.send([q.sender.user], 'internaltransfer_reject')



class CheckOnChargebackIssueAdmin(IssueAdmin):
    inlines = []
    list_display = [
        "id", "author_with_link", "title", "text", "user_requested_check",
        "department", "creation_ts", "status",
    ]
    fieldsets = [
        (None, {
            "fields": ("status", "internal_comment")
        })
    ]


class ApproveOpenECNIssueAdmin(IssueAdmin):
    date_hierarchy = "creation_ts"
    list_display = [
        "id", "user_full_name", "allow_open_invest", "author", "title", "text", "assignee_with_link",
        "department", "creation_ts", "status",
    ]
    list_filter = ["creation_ts", "status", "deadline"]
    ordering = ["-creation_ts"]
    search_fields = ["title", "text", "author__email"]
    fieldsets = [
        (None, {
            "fields": ("status", "author", "user_full_name", "user_email", "user_phone",
                       "assignee", "allow_open_invest", "department", "deadline", "title",
                       "html", "internal_comment", "internal_html")
        })
    ]
    readonly_fields = ["title", "html", "internal_html", "user_full_name", "user_email", "user_phone"]
    inlines = (IssueAttachmentAdmin,
               IssueCommentAdmin,
               IssueHistoryAdmin)

    def user_email(self, obj):
        try:
            return User.objects.get(username=obj.author).email
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return

    def user_phone(self, obj):
        try:
            return UserProfile.objects.get(user=obj.author).phone_mobile
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return

    def user_full_name(self, obj):
        try:
            return ''.join([User.objects.get(username=obj.author).first_name, ' ',
                    User.objects.get(username=obj.author).last_name])
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return

    user_email.short_description = _(u"Email")
    user_full_name.short_description = _('User name')
    user_phone.short_description = _(u"Phone")



site.register(GenericIssue, GenericIssueAdmin)
site.register(UserIssue, IssueAdmin)
site.register(RestoreFromArchiveIssue, AccountDisabledAdmin)
site.register(CheckDocumentIssue, IssueAdmin)
site.register(InternalTransferIssue, InternalTransferIssueAdmin)
site.register(ApproveOpenECNIssue, ApproveOpenECNIssueAdmin)
# site.register(CheckOnChargebackIssue, CheckOnChargebackIssueAdmin)
# Vasya said unnecessory
