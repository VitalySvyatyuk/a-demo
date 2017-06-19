# -*- coding: utf-8 -*-
from collections import namedtuple

from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from django.utils.datastructures import SortedDict
from geobase.utils import get_country

from payments.fields import PaymentSystemField
import settings
from shared.models import StateSavingModel
from payments.utils import load_payment_system


class RequisitManager(models.Manager):
    def visible(self):
        return self.get_queryset().filter(is_deleted=False)


class UserRequisit(StateSavingModel):
    alias = models.CharField(_("alias"), max_length=255, default="", blank=True,
                             help_text=_('Give these payment details a name, for example "Forex wallet". '
                                         'It will help you find them in forms more easily'))
    purse = models.CharField(_("purse"), max_length=255, db_index=True, blank=True)
    user = models.ForeignKey(User, related_name="requisits", verbose_name=_("user"), blank=True)
    payment_system = PaymentSystemField(_("payment system"))
    is_valid = models.NullBooleanField(_("is the data valid?"), blank=True,
                                       null=True, default=False)
    is_deleted = models.BooleanField(_('Is deleted'), help_text=_('Users do not see deleted requisits'),
                                     default=False)
    comment = models.TextField(_("manager comment"), blank=True, null=True,
                               help_text=_("If you reject a requisit, leave a comment here"))
    params = JSONField(_("details"), blank=True, null=True)
    creation_ts = models.DateTimeField(_("created at"), auto_now_add=True)
    previous = models.ForeignKey('self', blank=True, null=True,
                                 verbose_name=_("previous version of requisit"))
    objects = RequisitManager()

    class Meta:
        verbose_name = _("user requisit")
        verbose_name_plural = _("user requisits")
        ordering = ["payment_system", "-creation_ts"]
        unique_together = ("purse", "payment_system", "user")

    def __unicode__(self):
        return "%s" % (self.purse if self.alias == "" else self.alias)

    def get_params(self, flat=False):
        """Определяет порядок полей при выводе в списке реквизитов и выдает правильные названия полей"""

        from payments.models import REASONS_TO_WITHDRAWAL

        order = {
            "bankrur": [("bank_account", _("Bank account")), ("name", _("Name")), ("tin", _("TIN")),
                        ("bank", _("Bank")), ("credit_card_number", _("Credit card number")),
                        ("correspondent", _("Correspondent")), ("bic", _("BIC")),
                        ("payment_details", _("Payment details"))],
            "bankeur": [("bank_account", _("Bank account")), ("name", _("Sender")),
                        ("country", _("Country")), ("address", _("Address")), ("bank", _("Bank")),
                        ("bank_swift", _("Bank's SWIFT code")), ("correspondent", _("Correspondent"))],
            "bankusd": [("bank_account", _("Bank account")), ("name", _("Sender")),
                        ("country", _("Country")), ("address", _("Address")), ("bank", _("Bank")),
                        ("bank_swift", _("Bank's SWIFT code")), ("correspondent", _("Correspondent"))],
            "bankuah": [("bank_account", _("Bank account")), ("name", _("Name")), ("tin", _("TIN")),
                        ("bank", _("Bank")), ("credit_card_number", _("Credit card number")),
                        ("correspondent", _("Correspondent")), ("bic", _("BIC")),
                        ("payment_details", _("Payment details"))],
            "default": []
        }
        d = SortedDict()

        system = self.payment_system
        if not system:
            return None

        if isinstance(system, basestring):
            system = load_payment_system(self.payment_system)

        if system.slug in order:
            key = system.slug
        else:
            key = "default"

        val = namedtuple("NiceKey", ("key", "value"))

        if self.params:
            for real_key, display_key in order[key]:
                if self.params.get(real_key) in ["", None]:
                    # пустое значение обозначается длинным дефисом mdash
                    # mark_safe нужен для корректного отображения &mdash;
                    d[display_key] = val(key=real_key,
                                         value=mark_safe("&mdash;"))
                else:
                    if real_key == "correspondent" and system.slug in ["bankeur", "bankusd"]:
                        currency = system.currency
                        if currency in settings.BANK_ACCOUNTS:
                            d[display_key] = val(key=real_key,
                                                 value=settings.BANK_ACCOUNTS[currency][int(self.params[real_key])][0])
                    elif real_key == "country":
                        d[display_key] = val(key=real_key,
                                             value=get_country(self.params[real_key]))
                    elif real_key == "reason":
                        d[display_key] = val(key=real_key,
                                             value=REASONS_TO_WITHDRAWAL[self.params[real_key]])
                    else:
                        d[display_key] = val(key=real_key,
                                             value=self.params[real_key])
        if flat:
            d = SortedDict((key, res.value) for (key, res) in d.iteritems())

        return d


# @signals.post_save(sender=UserRequisit)
# def requisit_saved(sender, instance, created, **kwargs):
#     if 'is_valid' in instance.changes:
#         Logger(
#             user=None, content_object=instance, ip=None,
#             event=Events.REQUISIT_VALIDATION_UPDATE,
#             params={'is_valid': instance.is_valid}).save()
