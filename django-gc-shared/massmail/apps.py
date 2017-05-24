# coding=utf-8
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MassmailConfig(AppConfig):
    name = 'massmail'

    def ready(self):
        import massmail.models
        from project.modeltranslate import model_translate
        massmail.models.CampaignType = model_translate("title")(massmail.models.CampaignType)

        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('unsubscribed', _("Unsubscribed from emails"))
