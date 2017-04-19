# -*- coding: utf-8 -*-

from django.db import models
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin

from modeltranslation.admin import TranslationAdmin
from contract_specs.models import (
    SymbolDescription, InstrumentSpecificationCategory, InstrumentSpecification)


class SymbolDescriptionAdmin(TranslationAdmin):
    list_display = ("symbol",)


class InstrumentSpecificationCategoryAdmin(TranslationAdmin):
    list_display = ("name",)
    prepopulated_fields = {'slug': ('name',)}


class InstrumentSpecificationAdmin(TranslationAdmin):
    list_display = ("instrument",)
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }


admin.site.register(SymbolDescription, SymbolDescriptionAdmin)
admin.site.register(InstrumentSpecificationCategory, InstrumentSpecificationCategoryAdmin)
admin.site.register(InstrumentSpecification, InstrumentSpecificationAdmin)
