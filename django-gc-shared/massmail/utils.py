# -*- coding: utf-8 -*-

import hmac
import urllib

from django.conf import settings
from django.core.urlresolvers import reverse
from project.utils import get_current_domain


def get_signature(email):
    if isinstance(email, unicode):
        email = email.encode('utf-8')
    return hmac.new('%s:%s' % (email, settings.SECRET_KEY)).hexdigest()


def get_unsubscribe_url(email, campaign_id, language=None):
    from profiles.models import UserProfile

    signature = get_signature(email)
    domain = get_current_domain(language=language)
    is_our_client = UserProfile.objects.filter(user__email=email).exists()

    if not is_our_client:
        args = [signature, urllib.quote(email)]
        return domain + reverse('massmail_unsubscribe_email', args=args)

    else:
        args = [signature, campaign_id, urllib.quote(email)]
        return domain + reverse('massmail_unsubscribe_email_id', args=args)  



def get_email_signature(email):
    if isinstance(email, unicode):
        email = email.encode('utf-8')
    from hashlib import sha1
    return sha1('%s:%s' % (email.lower(), settings.EMAIL_UNSUBSCRIBE_SECRET_KEY)).hexdigest()


def get_unsubscribe_email(email, campaign_id, language=None):
    signature = get_email_signature(email)
    mailbox, domain = settings.MASSMAIL_UNSUBSCRIBE_EMAIL.split('@')
    return "%s+%s+%s@%s" % (mailbox, signature, campaign_id, domain)
