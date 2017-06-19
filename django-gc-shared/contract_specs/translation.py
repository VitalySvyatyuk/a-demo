# coding=utf-8
from modeltranslation.translator import register, TranslationOptions
from contract_specs.models import SymbolDescription, InstrumentSpecificationCategory, InstrumentSpecification


@register(SymbolDescription)
class SymbolDescriptionTranslation(TranslationOptions):
    fields = ('description', )


@register(InstrumentSpecificationCategory)
class InstrumentSpecificationCategoryTranslation(TranslationOptions):
    fields = ('name', )


@register(InstrumentSpecification)
class InstrumentSpecificationTranslation(TranslationOptions):
    fields = ('description',)
