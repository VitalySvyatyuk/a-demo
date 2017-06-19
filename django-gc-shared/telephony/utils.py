# -*- coding: utf-8 -*-


def get_common_phone_tail(phone):
    if not phone or len(unicode(phone)) < 10:
        return None
    return phone[-10:]
