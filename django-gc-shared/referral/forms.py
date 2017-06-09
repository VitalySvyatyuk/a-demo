# coding: utf-8

import re

from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _

from referral.models import PartnerCertificateIssue


class PartnerCertificateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(PartnerCertificateForm, self).__init__(*args, **kwargs)

    def clean(self):

        if not self.request.user.accounts.real_ib():
            raise forms.ValidationError(_(u"You don't have a RealIB account"))

        if PartnerCertificateIssue.objects.filter(author=self.request.user,
                                                  status='open'):
            raise forms.ValidationError(_(u"You've already made a request for certificate creation"))

    def save(self):
        usr = self.request.user
        #fetching partner account nubmer
        partner_account = usr.accounts.real_ib()[0]

        if partner_account:
            partner_account_number = partner_account.mt4_id
        else:
            partner_account_number = None

        #fetching phone nubmer
        p = usr.profile
        tel_numb = p.phone_mobile or p.phone_work or p.phone_home or None

        return PartnerCertificateIssue.objects.create(
            author=self.request.user,
            partner_account_number=partner_account_number,
            tel_numb=tel_numb
        )


class DomainValidator(validators.RegexValidator):
    regex = re.compile(
        r'(?:(?:[А-ЯЁA-Z0-9](?:[А-ЯЁA-Z0-9-]{0,61}[А-ЯЁA-Z0-9])?\.)+(?:[А-ЯЁA-Z]{2,6}\.?|[А-ЯЁA-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$' # ...or ip
        , re.IGNORECASE | re.UNICODE)


class PartnerAPIKeyForm(forms.Form):
    domain = forms.CharField(label=_("Domain"), validators=[DomainValidator()],
                             help_text=_(u"API will be valid for the domain and all its subdomains. "
                                         u"Example: grandcapital.ru"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('current_user')
        super(forms.Form, self).__init__(*args, **kwargs)
        self.fields['ib_account'] = forms.ModelChoiceField(queryset=self.user.accounts.real_ib().active(),
                            label=_(u"Partner account"),
                                help_text=_(u'Referral number of this account will be used for links from this domain.'))