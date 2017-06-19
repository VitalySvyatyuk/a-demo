# coding=utf-8
from django.apps import AppConfig


class GeobaseConfig(AppConfig):
    name = 'geobase'

    def ready(self):
        import geobase.models
        from project.modeltranslate import model_translate
        geobase.models.Country = model_translate("name")(geobase.models.Country)
        geobase.models.Region = model_translate("name")(geobase.models.Region)

        from geobase.phone_code_widget import CountryPhoneCodeFormField
        CountryPhoneCodeFormField.delay_init = False
        for field in CountryPhoneCodeFormField.register:
            field.delayed_init()

