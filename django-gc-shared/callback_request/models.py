# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy


CATEGORY_CHOICES = (
    ("general", _("General questions")),
    ("financial", _("Financial questions")),
    ("technical", _("Technical questions")),
    ("partnership", _("Request for partnership"))
)


class CallbackRequest(models.Model):
    phone_number = models.CharField(pgettext_lazy("callback", "Phone"), max_length=25)
    email = models.CharField(_("Email"), max_length=50, default="", blank=True)
    name = models.CharField(pgettext_lazy("callback", "Name"), max_length=255, null=False, default="")
    country = models.ForeignKey('geobase.Country', verbose_name=_('Country'),
                                blank=True, null=True, help_text=_('Example: Russia'))
    call_date = models.DateField(_("Date"), auto_now_add=True)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES, default="partnership")
    comment = models.CharField(max_length=255, default="", blank=True)
    time_start = models.CharField(pgettext_lazy("callback", "From"), max_length=5, blank=True)
    time_end = models.CharField(pgettext_lazy("callback", "To"), max_length=5, blank=True)
    request_processed = models.BooleanField(_("Request processed"), default=False)
    internal_comment = models.TextField(_("Internal comment"), blank=True, default="")
    creation_ts = models.DateTimeField(auto_now_add=True)
