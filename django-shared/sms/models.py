# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import HStoreField


class SMSMessage(models.Model):
    backend = models.CharField(max_length=100, editable=False)
    code = models.CharField(max_length=100, editable=False)
    receiver_number = models.CharField(_('Receiver number'), max_length=50,
        help_text=_('A number in format +70000000000'))
    sender_number = models.CharField(_('Sender number'), max_length=50,
        blank=True, null=True, editable=False,
        help_text=_('Leave empty if you don\'t know what it is'))
    text = models.TextField(_('Message text'), help_text=_('Maximum 160 characters'))
    timestamp = models.DateTimeField(auto_now_add=True)
    params = HStoreField(default={})

    class Meta:
        verbose_name = _('SMS message')
        verbose_name_plural = _('SMS messages')

    def __unicode__(self):
        return u'%s' % (self.receiver_number)
