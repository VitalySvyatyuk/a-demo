# coding=utf-8
from django.apps import AppConfig


class CmsConfig(AppConfig):
    name = 'uptrader_cms'

    def ready(self):
        import uptrader_cms.models
        from project.modeltranslate import model_translate
        uptrader_cms.models.Indicator = model_translate("name")(uptrader_cms.models.Indicator)
        uptrader_cms.models.IndicatorCountry = model_translate("name")(uptrader_cms.models.IndicatorCountry)
        uptrader_cms.models.LegalDocument = model_translate("name")(uptrader_cms.models.LegalDocument)
