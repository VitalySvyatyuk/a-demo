# -*- coding: utf-8 -*-
from collections import Counter

from django.conf import settings
from django.contrib.gis.geoip import GeoIP
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from pygeoip import timezone as pygeoip_tz
from pytz import timezone as pytz_tz

from shared.models import RegexpManager, RegexpQuerySet, CustomManagerMixin


class GeobaseQueryset(RegexpQuerySet):

    def russian(self):
        return self.filter(language='ru')

    def non_russian(self):
        return self.exclude(language='ru')


class CountryManager(RegexpManager, CustomManagerMixin):

    def get_queryset(self):
        return GeobaseQueryset(self.model)

    def get_by_ip(self, ip):
        if settings.DEBUG and ip == "127.0.0.1":  # Return a random country for debug purposes
            return self.get_queryset().order_by("?")[0]
        g = GeoIP()
        country_code = g.country_code(ip)
        if country_code is None:
            return
        country = self.get_queryset().filter(code=country_code)
        if country:
            return country[0]


class Country(models.Model):
    LANGUAGES = (  # Not using the one from settings.py because we have more languages here
        ("en", "English"),
        ("ru", "Russian"),
        ('zh-cn', 'Chinese'),
        ('id', 'Indonesian'),
        ("es", "Spanish"),
        ('fr', 'French'),
        ('ar', 'Arabic'),
        ('ms', 'Malaysian'),
        ('pt', 'Portuguese'),
        ('hi', 'Hindi'),
    )

    name = models.CharField(_('Name'), max_length=50)
    # name_en = models.CharField(_('Name Eng'), max_length=50, default="")
    slug = models.SlugField(_('Slug'), help_text=_('Unique string for url generating'))
    code = models.CharField(_("Code"), max_length=5, null=True, blank=True, db_index=True, unique=True)
    weight = models.IntegerField(_('Weight'), default=100)
    phone_code = models.SmallIntegerField(_('Phone code'), default=None, blank=True, null=True)
    is_primary = models.BooleanField(_('This country is primary in this phone code group'), default=False)
    phone_code_mask = models.CharField(u'Маска номера', blank=True, default='', max_length=30,
                                       help_text=u'"9" обозначает любую цифру, например (999) 999-9999')
    language = models.CharField(_('Language'), max_length=10, help_text=u'Основной язык страны', choices=LANGUAGES,
                                blank=True, default='')

    objects = CountryManager()

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        ordering = ['weight', 'name']

    def __unicode__(self):
        # from django.utils.translation import get_language
        # if get_language() == 'ru':
        #     return self.name_ru
        # else:
        #     return self.name_en or self.name
        return self.name

    @property
    def is_russian_language(self):
        return self.language == 'ru'

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.is_primary and self.__class__.objects.filter(phone_code=self.phone_code,
                                                             is_primary=True).exclude(pk=self.pk).exists():
            raise ValidationError('The primary country for this phone code group is already selected')

    @classmethod
    def get_phone_codes(cls, countries_list=None):
        """
            This function returns a list of country codes in exactly that format:
            [('+code1','+code1  (Country1)'),('+code2','+code2  (Country2)')...]

            It takes 1 argument - countries. If countries_list is None, function will return the whole bunch of
            countries in our database. If countries_list is 'russian', function will return list of only
            russian-language speaking countries. If countries_list is a list of country_names, function will
            return a list of phone-codes of that countries.
        """

        countries = cls.objects.exclude(phone_code=None)

        if countries_list:
            if countries_list == 'russian':
                countries = countries.russian()
            else:
                countries = countries.filter(Q(name__in=countries_list) | Q(name_en__in=countries_list))

        # Countries which have a Primary country with the same phone code
        c = Counter(countries.values_list("phone_code", flat=True))
        secondary_countries = [x for x in countries if not x.is_primary and c[x.phone_code] > 1]

        return [("+%d" % c.phone_code, c.pk, c in secondary_countries, c.phone_code_mask) for c in countries]

    def get_time_zone(self):
        if not self.code:
            return
        tz_name = pygeoip_tz.country_dict.get(self.code)
        if tz_name is None:
            return

        if isinstance(tz_name, str):
            return pytz_tz(tz_name)
        elif isinstance(tz_name, dict):
            if self.code in ['AR', 'AU', 'KZ', 'UZ', 'MX']:
                return pytz_tz(tz_name['01'])
            elif self.code == 'UA':
                return pytz_tz(tz_name['02'])
            elif self.code in ['BR', 'ID']:
                return pytz_tz(tz_name['03'])
            elif self.code == 'CA':
                return pytz_tz(tz_name['ON'])
            elif self.code == 'RU':
                return pytz_tz(tz_name['06'])
            elif self.code == 'US':
                return pytz_tz(tz_name['CT'])
            else:
                return pytz_tz(tz_name[tz_name.keys()[0]])


class Region(models.Model):
    country = models.ForeignKey("Country", verbose_name=_('Country'), related_name="regions")
    #see http://download.geonames.org/export/dump/admin1CodesASCII.txt for codes
    code = models.CharField(_("Code"), max_length=5, null=True, blank=True, db_index=True)
    name = models.CharField(_('Name'), max_length=50)
    # name_en = models.CharField(_('Name Eng'), max_length=50, default="")

    objects = RegexpManager()

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')
        ordering = ['country__name', 'name']

    def __unicode__(self):
        return self.name

    def get_time_zone(self):
        if self.code:
            tz_name = pygeoip_tz.time_zone_by_country_and_region(
                self.country.code,
                self.code
            )
            if tz_name is None:
                return
            return pytz_tz(tz_name)
        else:
            return self.country.get_time_zone()


class City(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('Country'))
    region = models.ForeignKey(Region, verbose_name=_('Region'), null=True, blank=True)
    name = models.CharField(_('Name'), max_length=50)
    name_en = models.CharField(_('Name Eng'), max_length=50, default="")

    objects = RegexpManager()

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ['country__name', 'name']

    def __unicode__(self):
        from django.utils.translation import get_language
        if get_language() == 'ru':
            return self.name
        else:
            return self.name_en
