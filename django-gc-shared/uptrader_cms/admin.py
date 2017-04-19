# -*- coding: utf-8 -*-
from ajax_select import make_ajax_form
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from uptrader_cms.models import *
from node.admin import NodeAdmin, CKEditorAdminForm
from shared.admin import BaseAdmin, with_link


class AnalyticsAdmin(NodeAdmin):
    list_display = ('title', 'content_type', 'url_alias', 'creation_ts', 'author', 'language', 'update_ts')


class CompanyNewsAdmin(NodeAdmin):

    form = CKEditorAdminForm
    list_display = ('title', 'alias', 'creation_ts', 'author', 'language', 'published')
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (None, {
            "fields": ("language", "title", "slug", "published",
                       "event_date", "image", "body")
        }),
    )

    def alias(self, obj):
        return obj.get_absolute_url()

    def get_form(self, request, obj=None, **kwargs):
        form = super(CompanyNewsAdmin, self).get_form(request, **kwargs)
        form.current_user = request.user
        return form


class CompanyNewsCategoryAdmin(admin.ModelAdmin):
    save_as = True
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("id", "title", "slug", "language")
    list_filter = ("language", )


class IndicatorEventAdmin(admin.ModelAdmin):
    form = make_ajax_form(IndicatorEvent, {'indicator': 'indicator'})
    list_display = ('title', 'event_date', 'indicator_with_link')
    list_filter = ('importance',)

    indicator_with_link = with_link('indicator', _("Indicator"))


class IndicatorCountryAdmin(BaseAdmin):

    list_display = ("name", "slug", "code", "rate_name")
    fields = ("name", "slug", "code", "rate_name")
    ordering = ("name", )


class IndicatorAdmin(BaseAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    readonly_fields = ('fxstreet_id',)


class LegalDocumentAdminForm(forms.ModelForm):
    languages = forms.MultipleChoiceField(
        choices=settings.LANGUAGES,
        widget=admin.widgets.FilteredSelectMultiple(
            is_stacked=False, verbose_name="languages"))


class LegalDocumentAdmin(BaseAdmin):
    list_display = ['name']
    form = LegalDocumentAdminForm


admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(IndicatorCountry, IndicatorCountryAdmin)
admin.site.register(IndicatorEvent, IndicatorEventAdmin)
admin.site.register(CompanyNews, CompanyNewsAdmin)
admin.site.register(LegalDocument, LegalDocumentAdmin)
