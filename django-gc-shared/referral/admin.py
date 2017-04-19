# -*- coding: utf-8 -*-
from django.contrib import admin

from issuetracker.admin import IssueAdmin
from referral.models import PartnerCertificateIssue, PartnerDomain


class PartnerDomainAdmin(admin.ModelAdmin):
     list_display = ('id', 'account','domain','creation_ts', 'ib_account')
     readonly_fields = ('account', 'api_key')
     raw_id_fields = ('ib_account',)

admin.site.register(PartnerDomain, PartnerDomainAdmin)


class PartnerCertificateIssueAdmin(IssueAdmin):
     list_display = [
        "id", "author_with_link", "tel_numb","partner_account_number","title",
        "department", "creation_ts", "status",
    ]


admin.site.register(PartnerCertificateIssue, PartnerCertificateIssueAdmin)
