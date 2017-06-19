# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from shared.decorators import cached_func
from uptrader_cms.models import LegalDocument

CACHE_TIMEOUT = 900

@cached_func(CACHE_TIMEOUT)
def get_agreements():
    documents_ru = LegalDocument.objects.filter(languages__contains="{ru}")
    documents_en = LegalDocument.objects.filter(languages__contains="{en}")
    document_names_ru = [i.name.lower() for i in documents_ru]
    document_names_en = [i.name.lower() for i in documents_en]

    AGREEMENTS = {

        ###
        # COMMON
        ###

        'client_agreement': {
            "label": _('Client agreement'),

            "default": documents_en[document_names_en.index('client agreement')].file.url
            if 'client agreement' in document_names_en else '/please_upload_client%20agreement',

            "order": 40,
        },
        'risk_disclosure': {
            "label": _('Risk disclosure'),
            "default": documents_en[document_names_en.index('risk disclosure')].file.url
                        if 'risk disclosure' in document_names_en else '/please_upload_risk%20disclosure',
            "order": 10,
        },
        'regulation_of_trades': {
            "label": _('Regulation of trades'),

            "default": documents_en[document_names_en.index('regulation of trades')].file.url
                        if 'regulation of trades' in document_names_en else '/please_upload_regulation%20of%20trades',
            "order": 60,
        },
        'pm_agreement': {
            "label": _('PM Agreement'),

            "default": documents_en[document_names_en.index('pm agreement')].file.url
                        if 'pm agreement' in document_names_en else '/please_upload_pm%20agreement',
            "order": 60,
        },
        'privacy_policy': {
            "label": _('Privacy Policy'),

            "default": documents_en[document_names_en.index('privacy policy')].file.url
                        if 'privacy policy' in document_names_en else '/please_upload_privacy%20policy',
            "order": 60,
        },
        'cookie_policy': {
            "label": _('Privacy Policy'),

            "default": documents_en[document_names_en.index('cookie policy')].file.url
                        if 'cookie policy' in document_names_en else '/please_upload_cookie%20policy',
            "order": 60,
        },
        'instruction_mac': {
            "label": _('Instruction mac'),

            "default": documents_en[document_names_en.index('instruction mac')].file.url
                        if 'instruction mac' in document_names_en else '/please_upload_instruction%20mac',
            "order": 60,
        },
        'vip_service': {
            "label": _('VIP service'),

            "default": documents_en[document_names_en.index('vip service')].file.url
                        if 'vip service' in document_names_en else '/please_upload_vip%20service',
            "order": 60,
        },

        'client_agreement_ru': {
            "label": _('Client agreement'),

            "default": documents_ru[document_names_ru.index('client agreement')].file.url
            if 'client agreement' in document_names_ru else '/please_upload_client%20agreement%20ru',

            "order": 40,
        },
        'risk_disclosure_ru': {
            "label": _('Risk disclosure'),
            "default": documents_ru[document_names_ru.index('risk disclosure')].file.url
            if 'risk disclosure' in document_names_ru else '/please_upload_risk%20disclosure%20ru',
            "order": 10,
        },
        'regulation_of_trades_ru': {
            "label": _('Regulation of trades'),

            "default": documents_ru[document_names_ru.index('regulation of trades')].file.url
            if 'regulation of trades' in document_names_ru else '/please_upload_regulation%20of%20trades%20ru',
            "order": 60,
        },
        'pm_agreement_ru': {
            "label": _('PM Agreement'),

            "default": documents_ru[document_names_ru.index('pm agreement')].file.url
            if 'pm agreement' in document_names_ru else '/please_upload_pm%20agreement%20ru',
            "order": 60,
        },
        'privacy_policy_ru': {
            "label": _('Privacy Policy'),

            "default": documents_ru[document_names_ru.index('privacy policy')].file.url
            if 'privacy policy' in document_names_ru else '/please_upload_privacy%20policy%20ru',
            "order": 60,
        },
        'cookie_policy_ru': {
            "label": _('Privacy Policy'),

            "default": documents_ru[document_names_ru.index('cookie policy')].file.url
            if 'cookie policy' in document_names_ru else '/please_upload_cookie%20policy%20ru',
            "order": 60,
        },
        'instruction_mac_ru': {
            "label": _('Instruction mac'),

            "default": documents_ru[document_names_ru.index('instruction mac')].file.url
            if 'instruction mac' in document_names_ru else '/please_upload_instruction%20mac%20ru',
            "order": 60,
        },
        'vip_service_ru': {
            "label": _('VIP service'),

            "default": documents_ru[document_names_ru.index('vip service')].file.url
            if 'vip service' in document_names_ru else '/please_upload_vip%20service%20ru',
            "order": 60,
        },

        ###
        # REAL IB
        ###
        'real_ib_partner': {
            "label": _(u'Partner agreement'),

            "default": '/static/agreements/Partner_Agreement.pdf',

            "order": 120,
        },
    }
    return AGREEMENTS




