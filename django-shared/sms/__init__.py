# -*- coding: utf-8 -*-
from collections import OrderedDict

import logging
import random
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import mail_admins
from django.utils.translation import activate

from shared.werkzeug_utils import import_string
from sms.exceptions import BackendCoreError, BackendUserError
from sms.models import SMSMessage

log = logging.getLogger(__name__)


def load_backend(path):
    try:
        return import_string(path)()
    except (ImportError, AttributeError), exc:
        raise ImproperlyConfigured("Error importing SMS backend %s: '%s'" % (path, exc))


def get_backends(to_number=None):
    if to_number is not None and isinstance(to_number, basestring):
        to_number = ''.join(d for d in to_number if d.isdigit())
        for mask in settings.SMS_BACKENDS_MASKS:
            if re.match(mask[0], to_number) is not None:
                return [load_backend(mask[1])]
    backends = map(load_backend, settings.SMS_BACKENDS)
    return backends


def send_with_check_verification(profile, text=None, from_=None, params=None):
    """
    A wrapper, for checking verification of receiver number
    """
    from profiles.models import get_validation

    if get_validation(profile.user, "phone_mobile").is_valid:
        return send(to=profile.phone_mobile, text=text, from_=from_, params=params)


def send(to=None, text=None, from_=None, send_reports=True, params=None):
    """A convenient wrapper function for sending SMS messages."""
    if params is None:
        params = {}

    message = SMSMessage(receiver_number=to, sender_number=from_, text=unicode(text), params=params)
    errors = OrderedDict()
    result = None

    for backend in get_backends(to):
        message.backend = backend.short_name
        try:
            result = backend.send(message)
        except (BackendCoreError, BackendUserError) as e:
            errors[backend.short_name] = unicode(e)
        else:
            if errors:
                errors[backend.short_name] = "ok"
            backend.log.debug("SMS was successfully sent.")
            break

    if errors and send_reports and result is None:
        msg = []
        for backend_name, error in errors.items():
            msg.append(u"Через %s: %s\n" % (backend_name, error))

        mail_admins(
            u"Ошибки отправки СМС на номер %s" % to,
            u"Вот что произошло: \n"
            u"%(body)s\n"
            u"Номер телефона: %(phone)s\n"
            u"Сообщение: '%(msg)s'" %
            {
                "phone": to,
                "msg": message.text,
                "body": "".join(msg),
            }
        )

    return result
