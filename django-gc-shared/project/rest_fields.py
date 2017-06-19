# -*- coding: utf-8 -*-

from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication as DRFSessionAuthentication
from rest_framework.metadata import SimpleMetadata


class ChoiceWithHelpTextField(serializers.ChoiceField):
    def __init__(self, *args, **kwargs):
        self.choices_help_texts = kwargs.pop('choices_help_texts')
        if not isinstance(self.choices_help_texts, dict):
            raise TypeError("choices_help_texts should be dict type")
        super(ChoiceWithHelpTextField, self).__init__(*args, **kwargs)

    def metadata(self, *args, **kwargs):
        return {
            'choices_help_texts': self.choices_help_texts
        }


class ExtraMetadata(SimpleMetadata):
    def get_field_info(self, field):
        meta = super(ExtraMetadata, self).get_field_info(field)
        if getattr(field, 'extra_metadata', None):
            meta.update(field.extra_metadata)

        if hasattr(field, 'metadata'):
            meta.update(field.metadata())
        return meta


class ExtraMetadataMixin(serializers.Field):
    def __init__(self, *args, **kwargs):
        self.extra_metadata = kwargs.pop("extra_metadata", {})
        super(ExtraMetadataMixin, self).__init__(*args, **kwargs)


class ExtraMetadataChoiceField(ExtraMetadataMixin, serializers.ChoiceField):
    pass


class ExtraMetadataSlugRelatedField(ExtraMetadataMixin, serializers.SlugRelatedField):
    pass


class SessionAuthentication(DRFSessionAuthentication):
    def enforce_csrf(self, request):
        if getattr(request, 'header_session', False):
            return  # If the request session was set via X-Session-Id header, we do not need CSRF checks
        # TODO: Uncomment the following line when the Android app is ready
        # return super(SessionAuthentication, self).enforce_csrf(request)


class JSONSerializerField(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


def exception_handler(exc, context=None):
    """
    Replace request.POST with drf_request.DATA so Sentry
    can log request properly.
    """
    from rest_framework.views import exception_handler as orig
    response = orig(exc, context)
    if response is None and context is not None:
        context['request']._request.POST = context['request'].data
    return response