# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from models import CallbackRequest
from shared.widgets import DateWidget
from geobase.phone_code_widget import CountryPhoneCodeFormField


class CallbackFormInformers(forms.ModelForm):
    class Meta:
        model = CallbackRequest
        fields = ('name', 'phone_number', 'email', 'time_start', 'time_end')
        widgets = {'call_date': DateWidget()}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(CallbackFormInformers, self).__init__(*args, **kwargs)
        self.fields['phone_number'] = CountryPhoneCodeFormField()
        self.fields['phone_number'].help_text = _('Example: +7(911)200-19-15')
        self.fields['phone_number'].label = _('Mobile phone')


TIME_OF_DAY_CHOICES = (
    ("any", "any"),
    ("morning", "morning"),
    ("afternoon", "afternoon"),
    ("evening", "evening"),
)


class CallbackForm(forms.ModelForm):

    time_of_day = forms.ChoiceField(choices=TIME_OF_DAY_CHOICES)

    class Meta:
        model = CallbackRequest
        fields = ('name', 'phone_number', 'category', 'comment', 'time_start', 'time_end')

    def clean(self):

        if "time_of_day" in self.cleaned_data:

            call_time = {
                "any": ("09:00", "20:00"),
                "morning": ("09:00", "12:00"),
                "afternoon": ("12:00", "16:00"),
                "evening": ("16:00", "20:00"),
            }[self.cleaned_data["time_of_day"]]

            self.cleaned_data["time_start"], self.cleaned_data["time_end"] = call_time

        return self.cleaned_data
