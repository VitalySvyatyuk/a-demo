# -*- coding: utf-8 -*-

from django.contrib import admin
from education.models import *
from shared.admin import urlize, BaseAdmin, with_link


class TutorialAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)


class WebinarAdmin(TutorialAdmin):
    list_display = ('id', 'category', 'name', 'speaker', 'description', 'language')
    list_filter = ('category', 'language')
    fields = ('slug', 'name', 'language', 'speaker', 'description', 'category', 'password')


class WebinarEventAdmin(BaseAdmin):
    list_display = ('id', 'webinar_with_link', 'starts_at', 'link_to_record', 'link_room')
    list_filter = ('webinar__category', 'webinar__name')
    fields = ('slug', 'webinar', 'starts_at', 'youtube_video_url', 'link_to_room')
    readonly_fields = ('slug', )

    webinar_with_link = with_link('webinar', u"Вебинар")

    def link_to_record(self, obj):
        if obj.youtube_video_url:
            return u"<a href='%s'>Запись</a>" % obj.youtube_video_url
        else:
            return "&mdash;"
    link_to_record.allow_tags = True
    link_to_record.short_description = u"Ссылка на запись"

    def link_room(self, obj):
        return u"<a href='%s'>Комната</a>" % obj.link_to_room
    link_room.allow_tags = True
    link_room.short_description = u"Ссылка на комнату"

    webinar_with_link = with_link("webinar", u"Вебинар")


class BaseRegistrationAdmin(admin.ModelAdmin):
    list_filter = ['creation_ts', 'is_paid']
    list_display = ['id', 'user_with_link', 'user_city', 'creation_ts', 'is_paid', 'tutorial']
    raw_id_fields = ('user', )

    def user_with_link(self, obj):
        return urlize(obj.user, text="%s %s" % (obj.user.first_name, obj.user.last_name))
    user_with_link.short_description = u"Профиль пользователя"
    user_with_link.allow_tags = True

    def user_city(self, obj):
        return obj.user.profile.city

    user_city.short_description = u"Город"


class WebinarRegistrationAdmin(BaseRegistrationAdmin):
    list_display = ['id', "webinar", 'user_with_link', 'user_city', 'webinar_date', 'creation_ts']

    fields = ("user", "tutorial", )
    ordering = ('-creation_ts',)

    def webinar(self, obj):
        return urlize(obj.tutorial, text=obj.tutorial.webinar.name)

    webinar.short_description = u"Вебинар"
    webinar.allow_tags = True

    def webinar_date(self, obj):
        return obj.tutorial.starts_at

    webinar_date.short_description = u"Дата проведения вебинара"
    webinar_date.admin_order_field = "tutorial__starts_at"


admin.site.register(Webinar, WebinarAdmin)
admin.site.register(WebinarEvent, WebinarEventAdmin)
admin.site.register(WebinarRegistration, WebinarRegistrationAdmin)
