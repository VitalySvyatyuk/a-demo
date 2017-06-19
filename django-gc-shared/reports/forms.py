# -*- coding: utf-8 -*-
import json

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import string_concat
from django.utils.translation import ugettext_lazy as _

import reports
from platforms.models import TradingAccount
from reports.models import AccountGroup
from shared.widgets import DateWidget


class ReportForm(forms.Form):
    """
    Base class for report forms.

    Subclasses should implement `save()` method and define `report_type`
    attribute which is expected to be a string from `REPORTS`
    (see reports/__init__.py:18).
    """
    start = forms.DateField(label=_("Start date"), widget=DateWidget())
    end = forms.DateField(label=_("End date"), widget=DateWidget())
    name = "Generic report (name not specified)"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        account = kwargs.pop("account", None)

        self.user = user

        super(ReportForm, self).__init__(*args, **kwargs)

        # Three possible cases for `account` field:
        # a) account was given as a keyword argument, using a CharField,
        # rendered as a HiddenInput
        # b) account wasn't given explicitly and a user has an uber
        # permission, using a plain CharField
        # c) account wasn't given and a user is a simple user, using a
        # ModelChoiceField with all the user's real ib accounts
        if account:
            self.fields["account"] = forms.IntegerField(
                initial=account.mt4_id,
                widget=forms.HiddenInput,
                required=True
            )
        elif user.has_perm("reports.can_use_any_account"):
            self.fields["account"] = forms.IntegerField(
                label=_("Account"),
                help_text=_("ID of the account you want to generate report for.")
            )
        else:
            self.fields["account"] = forms.ModelChoiceField(
                label=_("Account"),
                help_text=_("Select one of your accounts."),
                queryset=user.accounts.real_ib()
            )

        available_reports = [(codename, report["type"] == reports.ACCOUNT_GROUP,
                              report["type"] in (reports.GLOBAL, reports.PRIVATE_OFFICE))
                             for codename, report in settings.REPORTS.iteritems()
                             if user.has_perm("reports.can_generate_%s" % codename)]

        # если есть групповые отчеты среди доступных пользователю
        if any([is_group_filter for name, is_group_filter, is_no_account in available_reports]):

            qs = AccountGroup.objects.for_user(user)

            # если пользователь в группах не состоит, то пустые виджеты не выводим
            if qs:
                self.fields["account_group_include"] = forms.ModelMultipleChoiceField(
                    label=_("Include"),
                    help_text=mark_safe(string_concat(_("Include accounts from these groups. Empty means ALL accounts"),
                        _('. Click <a href="%s">here</a> to view group contents.') % reverse("reports_view_groups"))),
                    queryset=qs,
                    widget=forms.SelectMultiple(attrs={'size': 11}),
                    required=not user.has_perm("reports.can_use_any_account"),
                )
                self.fields["account_group_exclude"] = forms.ModelMultipleChoiceField(
                    label=_("Exclude"),
                    help_text=_("Exclude accounts from these groups"),
                    queryset=qs,
                    widget=forms.SelectMultiple(attrs={'size': 11}),
                    required=False,
                )

        choices = [(codename, settings.REPORTS[codename]["name"])
                     for codename, account_group_filter, no_account in available_reports
                     # ----------------------------------------------
                     # account_group_filter     |      qs   |   show?
                     # ----------------------------------------------
                     #          True            |      []   |   no
                     #          True            |     [..]  |   yes
                     #          False           |      []   |   yes
                     #          False           |     [..]  |   yes
                    if (not account_group_filter) or bool(qs)]
        choices.sort(key=lambda i: i[1])

        self.fields["report_type"] = forms.ChoiceField(
            label=_("Report type"),
            choices=choices,
            help_text=_("Choose one of the report types"),
            widget=forms.RadioSelect(),
            required=True)

        group_reports = [codename for codename, is_group_report, no_account in available_reports
                         if is_group_report]
        no_account_reports = [codename for codename, is_group_report, no_account in available_reports
                              if no_account]

        self.group_reports = mark_safe(json.dumps(group_reports))
        self.no_account_reports = mark_safe(json.dumps(no_account_reports))

    def clean_account(self):
        value = self.cleaned_data["account"]

        if not isinstance(value, TradingAccount):
            # Note: the underlying API doesn't care if the object
            # is present in the db or not, all it needs is mt4_id
            # set.
            value = TradingAccount(mt4_id=value)

        return value

    def clean_report_type(self):
        value = self.cleaned_data["report_type"]
        self.report_type = value
        return value

    def clean_account_group_exclude(self):
        account_groups = set(self.cleaned_data["account_group_exclude"])
        account_groups.update(set(AccountGroup.objects.excluded_for_user(self.user)))
        return account_groups

    def clean(self):

        cleaned = super(ReportForm, self).clean()

        if ("start" in cleaned) and ("end" in cleaned) and cleaned["start"] > cleaned["end"]:
            self.errors["start"] = [_("The end date of the period must be later than the start date")]

        if ("start" in cleaned) and ("end" in cleaned) and (cleaned["end"] - cleaned["start"]).days > 65:
            self.errors["end"] = [_("You can't order a report for a period longer than 65 days")]

        if "report_type" in cleaned:
            report = settings.REPORTS[cleaned["report_type"]]
            if report["type"] == reports.ACCOUNT_GROUP:
                unused_fields = ["account"]
            elif report["type"] in (reports.GLOBAL, reports.PRIVATE_OFFICE):
                unused_fields = ["account", "account_group_include", "account_group_exclude"]
            else:
                unused_fields = ["account_group_include", "account_group_exclude"]

            for field in unused_fields:
                if field in self.errors:
                    del self.errors[field]

        return cleaned

    def save(self):
        # TODO: do real reporting
        pass

    def __unicode__(self):
        if "cleaned_data" in self and not self.cleaned_data:
            return super(ReportForm, self).__unicode__()

        result = u"(%s - %s)" % (unicode(self.cleaned_data['start']),
                               unicode(self.cleaned_data['end']))
        if self.cleaned_data.get('account'):
            result += u" %s %s" % (_(u'for account'), unicode(self.cleaned_data['account']))
        if self.cleaned_data.get('account_group_include'):
            if self.cleaned_data.get('account_group_exclude'):
                result += " " + _(u'for account groups %(include)s without groups %(exclude)s') % {
                    'include': u", ".join(map(unicode, self.cleaned_data['account_group_include'])),
                    'exclude': u", ".join(map(unicode, self.cleaned_data['account_group_exclude']))
                }
            else:
                result += " " + _(u'for account group %s') % self.cleaned_data['account_group_include'][0]
        return "%s " + result


class MarketingInReportForm(forms.Form):
    start = forms.DateField(label=_("Start date"), widget=DateWidget())
    end = forms.DateField(label=_("End date"), widget=DateWidget())