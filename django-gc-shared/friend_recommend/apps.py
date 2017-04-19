# coding=utf-8
from django.apps import AppConfig


class FriendRecommendConfig(AppConfig):
    name = 'friend_recommend'

    def ready(self):
        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('friend_recommendation', u'Friend recomendation')
