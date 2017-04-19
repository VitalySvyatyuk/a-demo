# -*- coding: utf-8 -*-

from django.conf.urls import *


urlpatterns = patterns("otp.views",

    url(r"^security/$", "security",
        name="otp_security"),
    url(r"^refresh_qr_code/$", "refresh_qr_code",
        name="refresh_qr_code"),
    url(r"^check_sync/$", "check_sync",
        name="check_sync"),
    url(r"^check_sms/$", "check_sms",
        name="check_sms"),
    url(r"^send_sms/$", "send_sms",
        name="send_sms"),
    url(r"^make_call/$", "make_call",
        name="make_call"),
    url(r"^confirm/$", "confirm",
        name="confirm_phone"),
)
