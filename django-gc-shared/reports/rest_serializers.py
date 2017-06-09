# coding=utf-8
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from project.rest_fields import ExtraMetadataChoiceField

import reports
from reports.models import SavedReport, AccountGroup
from django.contrib.auth.models import User


class SavedReportSerializer(serializers.ModelSerializer):
    view_link = serializers.CharField(read_only=True)
    is_ready = serializers.BooleanField(read_only=True)

    class Meta:
        model = SavedReport
        fields = ('name', 'creation_ts', 'view_link', 'is_ready')


class ReportOrderSerializer(serializers.Serializer):
    start = serializers.DateField(label=_("Start date"))
    end = serializers.DateField(label=_("End date"))

    def __init__(self, *args, **kwargs):
        super(ReportOrderSerializer, self).__init__(*args, **kwargs)
        self.user = self.context["request"].user

        if self.user.has_perm("reports.can_use_any_account"):
            self.fields["account"] = serializers.IntegerField(
                label=_("Account"),
                help_text=_("ID of the account you want to generate report for."),
                required=False,
                allow_null=True,
            )
        else:
            self.fields["account"] = serializers.ChoiceField(
                label=_("Account"),
                help_text=_("Select one of your accounts."),
                choices=((acc.mt4_id, unicode(acc)) for acc in self.user.accounts.real_ib()),
                required=False,
                allow_null=True,
            )

        if self.user.has_perm("reports.can_use_any_user"):
            self.fields["user"] = serializers.ChoiceField(
                label=u"От имени пользователя",
                choices=((user.pk, u'%s %s' % (user.last_name, user.first_name)) for user in
                         User.objects.filter(is_staff=True).order_by('last_name')),
                required=False,
                allow_null=True,
            )


        available_reports = [(codename, report)
                             for codename, report in settings.REPORTS.iteritems()
                             if self.user.has_perm("reports.can_generate_%s" % codename)]

        # если есть групповые отчеты среди доступных пользователю
        if any([report["type"] == reports.ACCOUNT_GROUP for name, report in available_reports]):
            qs = AccountGroup.objects.for_user(self.user)

            # если пользователь в группах не состоит, то пустые виджеты не выводим
            if qs:
                choices = [(group.pk, group.name) for group in qs]
                self.fields["account_group_include"] = serializers.MultipleChoiceField(
                    label=_("Include"),
                    choices=choices,
                    required=False,
                    allow_null=True,
                )
                self.fields["account_group_exclude"] = serializers.MultipleChoiceField(
                    label=_("Exclude"),
                    choices=choices,
                    required=False,
                    allow_null=True,
                )
        else:
            qs = None

        choices = [(codename, report["name"])
                   for codename, report in available_reports
                   # ----------------------------------------------
                   # account_group_filter     |      qs   |   show?
                   # ----------------------------------------------
                   #          True            |      []   |   no
                   #          True            |     [..]  |   yes
                   #          False           |      []   |   yes
                   #          False           |     [..]  |   yes
                   if (not report["type"] == reports.ACCOUNT_GROUP) or bool(qs)]
        choices.sort(key=lambda i: i[1])

        group_reports = [codename for codename, report in available_reports
                         if report["type"] == reports.ACCOUNT_GROUP]

        no_account_reports = [codename
                              for codename, report in available_reports
                              if report["type"] in (reports.GLOBAL, reports.PRIVATE_OFFICE)]

        private_office_reports = [codename
                                  for codename, report in available_reports
                                  if report["type"] == reports.PRIVATE_OFFICE]

        self.fields["report_type"] = ExtraMetadataChoiceField(
            label=_("Report type"),
            choices=choices,
            help_text=_("Choose one of the report types"),
            required=True,
            extra_metadata={
                'group_reports': group_reports,
                'no_account_reports': no_account_reports,
                'private_office_reports': private_office_reports,
                'excluded_for_user': set(AccountGroup.objects.excluded_for_user(self.user).values_list('name', flat=True))
            })

    def validate(self, attrs):
        errors = {}

        if ("start" in attrs) and ("end" in attrs) and attrs["start"] > attrs["end"]:
            errors["start"] = _("The end date of the period must be later than the start date")

        if ("start" in attrs) and ("end" in attrs) and (attrs["end"] - attrs["start"]).days > 65:
            errors["end"] = _("You can't order a report for a period longer than 65 days")

        report = settings.REPORTS[attrs["report_type"]]
        if report["type"] == reports.ACCOUNT_GROUP:
            if self.user.has_perm("reports.can_use_any_account"):
                required_fields = []
            else:
                required_fields = ["account_group_include"]
        elif report["type"] in (reports.GLOBAL, reports.PRIVATE_OFFICE):
            required_fields = []
        else:
            required_fields = ["account"]

        for field in required_fields:
            if not attrs[field]:
                errors[field] = "This field is required"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
