# -*- coding: utf-8 -*-

from datetime import datetime

from django import forms
from django.contrib.auth.models import User

from crm.form_utils import CSIMultipleChoiceField
from crm.models import ReceptionCall, ManagerReassignRequest, PersonalManager
from shared.widgets import DateWidget


class ReceptionCallForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReceptionCallForm, self).__init__(*args, **kwargs)
        self.fields['switch_to'].widget.attrs['data-bind'] = "value: switch_to"
        self.fields['name'].widget.attrs['data-bind'] = "value: name"
        self.fields['account'].widget.attrs['data-bind'] = "value: account"
        self.fields['manager_assigned'].widget = self.fields['manager_assigned'].hidden_widget()
        self.fields['manager_assigned'].widget.attrs['data-bind'] = "checked: manager_auto_assigned"
        self.fields['lesson_date'].widget = DateWidget()

    def clean(self):
        super(ReceptionCallForm, self).clean()
        self._errors.pop('lesson_date', None)
        if self.data['lesson_date']:
            try:
                lesson_date = datetime.strptime(self.data['lesson_date'], '%d.%m.%Y').date()
                self.cleaned_data['lesson_date'] = lesson_date
            except ValueError:
                raise forms.ValidationError(u"Неверное значение даты")
        else:
            self.cleaned_data['lesson_date'] = None
        return self.cleaned_data

    class Meta:
        model = ReceptionCall
        exclude = ()


class ManagerReassignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(ManagerReassignForm, self).__init__(*args, **kwargs)
        # show only managers with special manager label
        self.fields['assign_to'].label_from_instance = lambda obj: unicode(obj.crm_manager)
        self.fields['assign_to'].queryset = User.objects.exclude(crm_manager=None).filter(is_active=True).order_by('-crm_manager__office', 'username')
        if request and request.user and request.user.crm_manager.office and\
                not request.user.crm_manager.office.is_our:
            self.fields['assign_to'].queryset = self.fields['assign_to'].queryset.filter(
                crm_manager__office=request.user.crm_manager.office
            )

    class Meta:
        model = ManagerReassignRequest
        fields = ('assign_to', 'comment')


class ManagerTasksReportForm(forms.Form):
    manager = forms.ModelChoiceField(PersonalManager.objects.all(), label=u"Менеджер", widget=forms.Select(attrs={'class': 'form-control'}))
    start = forms.DateField(label=u"С", input_formats=["%d.%m.%Y"], widget=forms.DateInput(attrs={'class': 'datepicker'}))
    end = forms.DateField(label=u"По", input_formats=["%d.%m.%Y"], widget=forms.DateInput(attrs={'class': 'datepicker'}))

