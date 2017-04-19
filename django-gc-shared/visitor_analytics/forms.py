# coding=utf-8
from django import forms

from visitor_analytics.models import UtmAnalytics


class UtmReportForm(forms.Form):
    date_from = forms.DateField(label=u'От')
    date_to = forms.DateField(label=u'До')
    utm_source = forms.MultipleChoiceField(label="utm_source", required=False)
    utm_medium = forms.MultipleChoiceField(label="utm_medium", required=False)
    utm_campaign = forms.MultipleChoiceField(label="utm_campaign", required=False)

    def __init__(self, *args, **kwargs):
        super(UtmReportForm, self).__init__(*args, **kwargs)
        urm_sources = list(UtmAnalytics.objects.order_by('utm_source').distinct('utm_source')
                                       .values_list('utm_source', flat=True))
        self.fields['utm_source'].choices = zip(urm_sources, urm_sources)
        utm_mediums = list(UtmAnalytics.objects.order_by('utm_medium').distinct('utm_medium')
                                       .values_list('utm_medium', flat=True))
        self.fields['utm_medium'].choices = zip(utm_mediums, utm_mediums)
        utm_campaigns = list(UtmAnalytics.objects.order_by('utm_campaign').distinct('utm_campaign')
                                         .values_list('utm_campaign', flat=True))
        self.fields['utm_campaign'].choices = zip(utm_campaigns, utm_campaigns)