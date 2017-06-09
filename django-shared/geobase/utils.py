# -*- coding: utf-8 -*-
from django.db.models import Q
from django.conf import settings

from geobase.models import Country, City


def get_country(country_id):

    if isinstance(country_id, Country):
        return country_id
    try:
        # раньше country записывалось в базу как название страны на транслите,
        # сейчас записывается id объекта страны в базе. обрабатывать нужно оба случая
        c = Country.objects.filter(id=int(country_id))
    except ValueError:
        c = Country.objects.filter(Q(name_en=country_id) | Q(name=country_id))

    return c[0] if c else country_id


def get_city(city_id):

    if isinstance(city_id, City):
        return city_id
    try:
        c = City.objects.filter(id=int(city_id))
    except ValueError:
        c = City.objects.filter(Q(name_en=city_id) | Q(name=city_id))

    return c[0] if c else city_id


# It's stupid, but some important IPs (for example, Moscow office) are not detected by GeoIP
HARDCODED_GEODATA = {
    "195.146.72.162": {  # Moscow office
        'country_code': 'RU',
        'region': 48,
    },
}


def get_geo_data(request):
    from geobase.models import Region, Country
    from django.contrib.gis.geoip import GeoIP

    if settings.DEBUG and request.META['REMOTE_ADDR'] == "127.0.0.1":
        country = Country.objects.all().order_by('?')[0]
        region = Region.objects.filter(country=country).order_by('?')[0]
        print u"regions.utils.get_geo_data: running in DEBUG mode, randomising result: country {} region {}".\
            format(country.name_en, region.name_en)
        return {
            'country': country,
            'region': region,
        }

    geo_data = HARDCODED_GEODATA.get(request.META['REMOTE_ADDR'])

    if geo_data is None:
        g = GeoIP()
        geo_data = g.record_by_addr(request.META['REMOTE_ADDR'])

    region = None
    country = None
    if geo_data:
        if geo_data.get('country_code') is not None:
            try:
                country = Country.objects.get(code=geo_data['country_code'])
            except Country.DoesNotExist:
                pass

        if country and geo_data.get('region') is not None:
            try:
                region = Region.objects.get(country=country, code=geo_data['region'])
            except (Region.DoesNotExist, Region.MultipleObjectsReturned):
                pass
    return {
        'country': country,
        'region': region,
    }
