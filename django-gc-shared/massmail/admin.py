# coding: utf-8

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
import django.contrib.admin.widgets
from django.db.models.fields.related import ManyToManyRel
from django.forms import SelectMultiple
from django.utils.translation import ugettext_lazy as _

from geobase.models import Country
from shared.russian_names import parse_name
from massmail.models import *


# Template admin
class AttachmentInline(admin.StackedInline):
    model = TemplateAttachment


class TemplateAdmin(admin.ModelAdmin):

    inlines = [AttachmentInline]
    list_display = ('name', 'subject', 'language')
    list_filter = ('language', )


# Mailing list admin
class SubscriberInline(admin.TabularInline):
    model = Subscribed


class MailingListAdminForm(forms.ModelForm):
    """A form, which allows to add subscribers via a text field"""
    subscribers = forms.CharField(label=_('Add subscribers'),
                                  widget=forms.Textarea(),
                                  required=False,
                                  help_text=_('Format: email<space>name'),
                                  )

    class Meta:
        model = MailingList
        fields = ('name', 'query', 'subscribers_count',  'subscribers')


class MailingListAdmin(admin.ModelAdmin):
    inlines = [SubscriberInline]
    form = MailingListAdminForm
    save_as = True

    list_display = ('name', 'subscribers_count', 'creation_ts')
    list_filter = ('creation_ts', )
    ordering = ("-creation_ts", )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ("query",)

    def save_model(self, request, obj, form, change):
        super(MailingListAdmin, self).save_model(request, obj, form, change)
        if form.cleaned_data['subscribers'].strip():
            for line in form.cleaned_data['subscribers'].strip().split('\n'):
                line_splitted = line.strip().split(' ', 1)
                if len(line_splitted) < 2:
                    line_splitted.append('')
                email, name = line_splitted
                if not email_re.match(email):
                    continue
                first_name, middle_name, last_name = parse_name(name)
                Subscribed.objects.create(mailing_list=obj,
                                          email=email,
                                          first_name=first_name,
                                          last_name=last_name
                                          )

        obj.save()

        # Recount email count in background
        import massmail.tasks
        # FIXME: is there a case, when there is no pk?
        if obj.pk:
            massmail.tasks.recount_email_count.delay(obj.pk)


class MessageBlockAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MessageBlockAdminForm, self).__init__(*args, **kwargs)
        self.fields['value_html'].widget = CKEditorWidget(config_name="massmail")

    class Meta:
        model = MessageBlock
        fields = ('value_html', )

class MessageBlockInline(admin.StackedInline):
    extra = 1
    form = MessageBlockAdminForm
    model = MessageBlock


class CampaignTypeAdmin(admin.ModelAdmin):
    model = CampaignType
    list_display = ('title', 'unsubscribed', 'subscribed')


class CampaignAdminForm(forms.ModelForm):
    languages = forms.MultipleChoiceField(choices=Country.LANGUAGES,
                                          widget=admin.widgets.FilteredSelectMultiple(is_stacked=False,
                                                                                      verbose_name="languages"))

    def __init__(self, *args, **kwargs):
        super(CampaignAdminForm, self).__init__(*args, **kwargs)

        rel = ManyToManyRel(Campaign, 'id')

        # FIXME: django docs:
        # The base_fields class attribute is the *class-wide* definition of
        # fields. Because a particular *instance* of the class might want to
        # alter self.fields, we create self.fields here by copying base_fields.
        # Instances should always modify self.fields; they should not modify
        # self.base_fields.
        # Don't think using base_fields here is necessary.
        self.base_fields['mailing_list'].widget = admin.widgets.RelatedFieldWidgetWrapper(
            SelectMultiple(attrs={'size': '6'}), rel, admin.site,)
        self.base_fields['negative_mailing_list'].widget = admin.widgets.RelatedFieldWidgetWrapper(
            SelectMultiple(attrs={'size': '6'}), rel, admin.site,)
        self.base_fields['campaign_type'].widget = admin.widgets.RelatedFieldWidgetWrapper(
            SelectMultiple(attrs={'size': '6'}), rel, admin.site,)
        self.base_fields['previous_campaigns'].widget = admin.widgets.RelatedFieldWidgetWrapper(
            SelectMultiple(attrs={'size': '6'}), rel, admin.site,)

    def clean(self):
        cleaned_data = super(CampaignAdminForm, self).clean()
        send_once = cleaned_data.get('send_once')
        schedule_time = cleaned_data.get('send_once_datetime')

        send_period = cleaned_data.get('send_period')
        cron = cleaned_data.get('cron')

        is_active = cleaned_data.get('is_active')

        if send_once and send_period:
            self._errors["send_once"] = self.error_class(
                [_("Please choose either delayed campaign or periodical")]
            )
            return self.cleaned_data

        if is_active and (send_once or send_period):
            self._errors["is_active"] = self.error_class(
                [_("Campaign can't be active and scheduled at the same time")]
            )
            return self.cleaned_data

        if send_once and not schedule_time:
            self._errors["send_once_datetime"] = self.error_class(
                [_("Please choose time for delayed campaign")]
            )

        if send_period and not cron:
            self._errors["cron"] = self.error_class(
                [_("Please specify schedule for the campaign")]
            )

        if send_once and schedule_time and schedule_time < datetime.now():
            self._errors["send_once_datetime"] = self.error_class([_("This date has already passed")])

        return cleaned_data

    class Meta:
        model = Campaign
        fields = ('mailing_list', 'negative_mailing_list', 'campaign_type', 'previous_campaigns',
                  'send_once', 'send_once_datetime', 'send_period', 'cron', 'is_active', )


class CampaignAdmin(admin.ModelAdmin):
    inlines = [MessageBlockInline]
    save_as = True
    list_display = ('name', 'sent_count', 'po_sent_count', 'creation_ts', 'is_active', 'is_sent', "hours_after_previous_campaign",
                    'open_count', 'click_count', 'unsubscribed')
    list_filter = ('creation_ts', 'is_sent', 'is_active', 'is_auto', 'send_period', 'send_once')
    readonly_fields = ('po_sent_count', '_lock', 'unsubscribed')

    form = CampaignAdminForm

    filter_horizontal = ('mailing_list', 'negative_mailing_list')
    fieldsets = (
        (None, {
            "fields": ("name", "template", "email_subject", "personal", "security_notification",
                       ("custom_email_from", "custom_email_from_name"),
                       "is_auto", "_lock", "is_active", "is_sent", "campaign_type",),
        }),
        (_("Mailing lists"), {
            'fields': ("unsubscribed", "languages", ('mailing_list', 'negative_mailing_list'),
                       ('previous_campaigns', 'previous_campaigns_type'), "hours_after_previous_campaign"),
        }),
        (_("Email and Account page"), {
            "fields": ("send_in_private", "po_sent_count", "send_email")
        }),
        (_("Schedule"), {
            "fields": ("order_weight", "send_once", "send_once_datetime", "send_period", "cron")
        }),
        (u"GA", {
            "fields": ("ga_slug",)
        }),
    )

    def open_count(self, obj):
        return obj.open_count
    open_count.short_description = _("Views")

    def click_count(self, obj):
        return obj.click_count
    click_count.short_description = _("Clicks")

    def sent_count(self, obj):
        return obj.sent_count
    sent_count.short_description = _("Emails sent")


class UnsubscribedAdmin(admin.ModelAdmin):
    list_display = ('email', 'creation_ts')
    list_filter = ('creation_ts',)
    search_fields = ('email',)


class SmsCampaignAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SmsCampaignAdminForm, self).__init__(*args, **kwargs)

        rel = ManyToManyRel(Campaign, 'pk')
        self.base_fields['mailing_list'].widget = admin.widgets.RelatedFieldWidgetWrapper(
            SelectMultiple(attrs={'size': '6'}), rel, admin.site,)
        self.base_fields['negative_mailing_list'].widget = admin.widgets.RelatedFieldWidgetWrapper(
            SelectMultiple(attrs={'size': '6'}), rel, admin.site,)
        self.base_fields['campaign_type'].widget = admin.widgets.RelatedFieldWidgetWrapper(
            SelectMultiple(attrs={'size': '6'}), rel, admin.site,)

    def clean(self):
        cleaned_data = super(SmsCampaignAdminForm, self).clean()
        try:
            cleaned_data['text'].encode('ascii')
        except UnicodeEncodeError:
            max_length = 539
        else:
            max_length = 1231
        if len(cleaned_data['text']) > max_length:
            self.errors['text'] = self.error_class([_("Message length exceeds the maximum length")])
        return cleaned_data

    class Media:
        js = ['sms/js/sms_counter.js',]

    class Meta:
        model = SmsCampaign
        fields = ('mailing_list', 'negative_mailing_list', 'campaign_type', 'text')


class SmsCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'sent_count', 'creation_ts', 'is_active', 'is_sent', 'unsubscribed', 'confirmed_only')
    readonly_fields = ('_lock', )
    save_as = True
    form = SmsCampaignAdminForm

    def sent_count(self, obj):
        return obj.sent_count
    sent_count.short_description = _("Messages sent")


admin.site.register(MessageTemplate, TemplateAdmin)
admin.site.register(MailingList, MailingListAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Unsubscribed, UnsubscribedAdmin)
admin.site.register(CampaignType, CampaignTypeAdmin)
admin.site.register(SmsCampaign, SmsCampaignAdmin)
