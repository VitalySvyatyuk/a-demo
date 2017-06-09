# -*- coding: utf-8 -*-
from django.contrib import admin

from geobase.models import (City, Region, Country)
from shared.admin import BaseAdmin


class CityAdmin(BaseAdmin):
    list_display = ('name', 'name_en', 'country', 'region')
    list_filter = ('country',)
    search_fields = ('name','name_en',)


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)


class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'name_en')
    list_display = ('name', 'language', 'phone_code')
    list_filter = ('language', )


admin.site.register(City, CityAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Country, CountryAdmin)

