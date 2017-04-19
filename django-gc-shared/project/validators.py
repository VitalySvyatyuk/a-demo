# -*- coding: utf-8 -*-
import re
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible


@deconstructible
class allow_file_size(object):
    def __init__(self, bytes):
        self.bytes = bytes

    def __eq__(self, other):
        return self.bytes == other.bytes

    def __call__(self, file):
        if file.size > self.bytes:
            raise ValidationError(_('File is too big.'))
        return True


@deconstructible
class allow_file_extensions(object):
    def __init__(self, allowed_exts):
        self.allowed_exts = allowed_exts

    def __eq__(self, other):
        return self.allowed_exts == other.allowed_exts

    def __call__(self, file):
        if not re.search('\.(%s)' % '|'.join(self.allowed_exts), file.name.lower()):
            raise ValidationError(_('Unsupported file extension'))
        return True


class DomainValidator(validators.RegexValidator):
    regex = re.compile(
        ur'(?:(?:[А-ЯЁA-Z0-9](?:[А-ЯЁA-Z0-9-]{0,61}[А-ЯЁA-Z0-9])?\.)+(?:[А-ЯЁA-Z]{2,6}\.?|[А-ЯЁA-Z0-9-]{2,}\.?)|'  # domain...
        ur'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$',  # ...or ip
        re.IGNORECASE | re.UNICODE)
