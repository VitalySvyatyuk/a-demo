# coding: utf-8
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from uptrader_cms.models import IndicatorCountry, IMPORTANCE_CHOICES


class IndicatorCountryProxy(IndicatorCountry):
    """FIXME: A hack? Proxy, changes labels in the CalendarForm checkboxes"""

    def __unicode__(self):
        return mark_safe('<div class="flag flag-%s" title="%s (%s)"></div>' %
                         (self.code.lower(), _(self.name), self.slug.upper()))

    class Meta:
        proxy = True


class CalendarForm(forms.Form):
    country = forms.ModelChoiceField(
        label=_('Countries'),
        required=False,
        empty_label=_("All countries"),
        queryset=IndicatorCountry.objects.all(),
        widget=forms.Select(attrs={'class': 'input_box__input select'}),)
    importance = forms.ChoiceField(
        label=_("Importance"),
        choices=(("", _("Any")),) + IMPORTANCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'input_box__input select'}),)
    start_date = forms.DateField(widget=forms.HiddenInput, required=False)
    end_date = forms.DateField(widget=forms.HiddenInput, required=False)
