# -*- coding: utf-8 -*-

from xml.etree.ElementTree import fromstring
import logging
import urllib2

from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from sms.exceptions import BackendCoreError, BackendUserError


class BaseSMSBackend(object):
    """Base SMS backend implementation."""
    short_name = "base"
    user_errors = ()
    core_errors = () # FIXME: remove?
    error_messages = {}

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def send(self, *args, **kwargs):
        """
        Method should perform all the needed I/O operations an raise
        an appropriate exception class (either BackendCoreError or
        BackendUserError) if the backend failed to send the message
        or return and SMSMessage instance if everything went fine.
        """
        raise NotImplementedError

    def error(self, code=None):
        """
        Method should construct an exception for a given status code;
        BackendUserError for codes, listed in Backend.user_codes and
        BackendCoreError for others.
        """
        error_class = BackendUserError if code in self.user_errors else BackendCoreError
        error_message = self.error_messages.get(code, _("Failed to send message"))
        return error_class(error_message)


class SMSRuBackend(BaseSMSBackend):
    """SMS backend, using http://sms.ru API."""
    short_name = "smsru"
    user_errors = ("203", "205")
    error_messages = {
        "100": _("Message is in the queue"),
        "101": _("Message is on the way to the operator"),
        "102": _("Message is on the way to the recipient"),
        "103": _("Message delivered"),
        "104": _("Message failed: out of time"),
        "105": _("Message failed: cancelled by the operator"),
        "106": _("Message failed: phone malfunction"),
        "107": _("Message failed, reason unknown"),
        "108": _("Message declined"),
        "200": _("Wrong API key."),
        "201": _("Not enough funds."),
        "202": _("Invalid receiver number."),
        "203": _("Empty message."),
        "204": _("Sender name not allowed."),
        "205": _("Message too long."),
        "206": _("Message limit exceeded"),
        "207": _("Receiver number not allowed.")
    }

    def send(self, message):

        params = {
            'api_id': settings.SMSRU_API_ID,
            'to': message.receiver_number,
            'from': message.sender_number or settings.SMSRU_SENDER,
            'text': message.text
        }

        try:
            response = urllib2.urlopen('http://sms.ru/sms/send?%s' % urlencode(params)).read()
        except urllib2.URLError as exc:
            raise BackendCoreError("Failed to accesss the API: %s" % force_unicode(exc))

        status = response.split('\n')[0]

        if status != '100':
            self.log.debug('SMSRu Error: %s' % status)
            raise self.error(status)
        message.save()
        return message


class WebSMSBackend(BaseSMSBackend):
    """
    SMS backend, using http://websms.ru API
    """
    short_name = "webru"
    user_errors = ("10", "11", "12")
    error_messages = {
        "0": _("No errors"),
        "1": _("Error login or password"),
        "2": _("Blocked user"),
        "3": _("Insufficient funds"),
        "4": _("Blocked ip"),
        "5": _("Http not enabled"),
        "6": _("This server ip not enabled"),
        "7": _("Email sending not enabled"),
        "8": _("This email not enabled"),
        "9": _("Blocked moderator id"),
        "10": _("Error manual phone list"),
        "11": _("Empty message text"),
        "12": _("Empty phone list"),
        "13": _("Stop service"),
        "14": _("Error format date"),
        "15": _("Double sent from web interface"),
        "17": _("Error multiaccess"),
        "20": _("Incorrect Group"),
        "21": _("Empty password"),
        "22": _("Empty login"),
        "23": _("Invalid FromPhone"),
        "24": _("Flood"),
    }

    def send(self, message):

        params = {
            'http_username': settings.WEBSMS_USERNAME,
            'http_password': settings.WEBSMS_PASSWORD,
            'phone_list': message.receiver_number,
            'fromPhone': message.sender_number or settings.WEBSMS_SENDER,
            'message': message.text.encode('utf-8'),
            'format': 'xml',
            'test': settings.WEBSMS_DEBUG
        }

        try:
            response = urllib2.urlopen('http://websms.ru/http_in6.asp?%s' % urlencode(params)).read()
        except urllib2.URLError, exc:
            raise BackendCoreError("Failed to accesss the API: %s" % force_unicode(exc))

        etree = fromstring(response)
        response_attrs = etree.getchildren()[0].attrib
        status = response_attrs['error_num']

        if status != "0":
            self.log.debug('WEBSMS Error: %s' % status)
            raise self.error(status)
        message.save()
        return message


class MTTBackend(BaseSMSBackend):
    """
    SMS backend, using MTT
    """
    short_name = "mtt"

    def send(self, message):

        params = {
            'operation': 'send',
            'login': settings.MTTSMS_USERNAME,
            'password': settings.MTTSMS_PASSWORD,
            'msisdn': ''.join(char for char in unicode(message.receiver_number) if char.isdigit()),
            'shortcode': settings.MTTSMS_SENDER,
            'text': message.text.encode('utf-8'),
        }

        try:
            response = urllib2.urlopen('http://91.213.5.13:8000/send?%s' % urlencode(params)).read()
        except urllib2.URLError, exc:
            raise BackendCoreError("Failed to accesss the API: %s" % force_unicode(exc))

        if not response.isdigit():
            raise self.error(response)

        message.save()
        return message

    def error(self, code=None):  # MTT provides error values as text, so we won't process it
        return BackendCoreError(code)


class PrintBackend(BaseSMSBackend):
    short_name = "print"

    def send(self, message):
        print "SMS:", message.receiver_number, message.text, message.params
        message.save()
        return message


class PlivoSMSBackend(BaseSMSBackend):
    """
    SMS backend, using Plivo
    """
    short_name = "plivo"

    def send(self, message):
        import plivo
        p = plivo.RestAPI(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)

        params = {
            'type': "sms",
            'src': settings.PLIVO_SENDER,  # Caller Id
            'dst' : ''.join(char for char in unicode(message.receiver_number) if char.isdigit()),
            'text': message.text.encode('utf-8'),
        }

        code, details = p.send_message(params)
        if code != 202:
            raise BackendCoreError(details)
        message.save()
        return message
