# -*- coding: utf-8 -*-

from django.db import models


class LanguageField(models.CharField):
    """
    Language field
    """

    def __init__(self, *args, **kwargs):
        from django.conf import settings
        from django.utils.translation import ugettext_lazy as _

        kwargs['max_length'] = 10
        kwargs['db_index'] = True
        kwargs['verbose_name'] = _('Language')
        kwargs['choices'] = settings.LANGUAGES
        kwargs['default'] = settings.LANGUAGE_CODE

        super(LanguageField, self).__init__(*args, **kwargs)

