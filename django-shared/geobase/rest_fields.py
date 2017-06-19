# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from geobase.phone_code_widget import split_phone_number


class PhoneField(serializers.Field):
    def to_representation(self, obj):
        code, tail, country = split_phone_number(obj)
        return {
            'country': country.id if country else None,
            'code': code,
            'tail': tail,
            'display': obj
        }

    def to_internal_value(self, data):
        #preparse validation
        from geobase.models import Country
        if not data.get('country', None):
            raise serializers.ValidationError(_('Country code is required'))
        if not data.get('tail', None):
            raise serializers.ValidationError(_('Phone number is required'))

        #get selected country
        country = Country.objects.filter(id=data['country']).exclude(phone_code=None).first()
        if not (data['country'] and country):
            raise serializers.ValidationError(_('Invalid country'))

        #clean tail from trashy things like hyphen
        clean_tail = "".join(c for c in data['tail'] if c in '1234567890+')
        if not clean_tail:
            raise serializers.ValidationError(_('Invalid phone tail'))

        #format result
        return u"+{code}{tail}".format(
            code=country.phone_code,
            tail=clean_tail)

    def metadata(self, *args, **kwargs):
        from geobase.models import Country
        country_choices = Country.objects.exclude(
            phone_code=None
        ).order_by(
            'weight', 'name'
        ).values('id', 'phone_code', 'name', 'phone_code_mask')
        return {
            #separate masks, because we cannot presave selected options in angular
            # it is easiest way -_-
            'phone_masks': {
                country_data['id']: country_data.pop('phone_code_mask') or None
                for country_data in country_choices
            },
            #create list of available countries, sorted by weight and name
            'country_choices': country_choices
        }