# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _
# from supercaptcha import CaptchaField

from shared.widgets import DateWidget


class AccountChooseForm(forms.Form):
    def __init__(self, accounts=[], *args, **kwargs):
        super(AccountChooseForm, self).__init__(*args, **kwargs)

        if len(accounts) > 1:
            self.fields["account_id"] = forms.ChoiceField(
                label=_("Select one of your accounts"),
                choices=[(a.mt4_id, unicode(a)) for a in accounts]
            )


# class CaptchaForm(forms.Form):
#     captcha = CaptchaField(label=_("are you human enough?"))


class MinMaxDateForm(forms.Form):
    min_date = forms.DateField(widget=DateWidget, label=_('Date from'), required=False)
    max_date = forms.DateField(widget=DateWidget, label=_('Date to'), required=False)

    def save(self, query, field_name='event_date'):
        min_date = self.cleaned_data.get('min_date')
        max_date = self.cleaned_data.get('max_date')
        if min_date:
            kwargs = {'%s__gte' % field_name: min_date}
            query = query.filter(**kwargs)
        if max_date:
            kwargs = {'%s__lte' % field_name: max_date +
                    timedelta(days=1)}
            query = query.filter(**kwargs)
        if min_date:
            query = query.order_by(field_name)
        return query

    def get_grouper(self, default):
        min_date = self.cleaned_data.get('min_date')
        max_date = self.cleaned_data.get('max_date')

        if max_date and min_date:
            if (max_date - min_date).days == 0:
                return "day"
            elif (max_date - min_date).days < 8:
                return "week"
            elif (max_date - min_date).days < 32:
                return "month"
            else:
                return "year"
        else:
            return default
