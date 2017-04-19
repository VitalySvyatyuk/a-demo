# coding: utf-8

from friend_recommend.models import Recommendation

from django.contrib import admin
from django.contrib.auth.models import User


class RecommendationAdmin(admin.ModelAdmin):

    list_display = ('id', 'creation_ts', 'user',
                    'name', 'email', 'has_joined')

    readonly_fields = ('user', 'ib_account')

    def has_joined(self, obj):
        user = User.objects.filter(email__iexact=obj.email, profile__registered_from="").first()
        if not user:
            return u'Нет'
        if user.date_joined < obj.creation_ts:
            return u'Уже был'
        return u'Да'
    has_joined.short_description = u'Пришел ли к нам'

    
# admin.site.register(Recommendation, RecommendationAdmin)
# Vasya said unnecessary
