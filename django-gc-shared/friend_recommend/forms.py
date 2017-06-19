# coding: utf-8
from datetime import datetime, timedelta

from django import forms

from models import Recommendation


class RecommendationForm(forms.ModelForm):

    class Meta:
        model = Recommendation
        exclude = ()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        has_ib_account = kwargs.pop('has_ib_account')
        super(RecommendationForm, self).__init__(*args, **kwargs)
        self.fields['ib_account'].queryset = self.request.user.accounts.real_ib()
        self.fields['ib_account'].empty_label = None
        if not has_ib_account:
            self.fields['ib_account'].widget = forms.HiddenInput()
        del self.fields['user']

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean(self):
        user = self.request.user
        email = self.cleaned_data.get('email')
        ib_account = self.cleaned_data.get('ib_account')
        if user and email:
            if Recommendation.objects.filter(user=user,
                                             email=email,
                                             creation_ts__gte=datetime.now()-timedelta(90)
                                             ).exists() or \
               Recommendation.objects.filter(ib_account=ib_account,
                                              email=email,
                                              creation_ts__gte=datetime.now()-timedelta(90)
                                              ).exists():
                raise forms.ValidationError(u'Вы уже посылали'
                                            u' приглашение на этот email')
            if user.email.lower() == email:
                raise forms.ValidationError(u'Вы не можете посылать'
                                            u' приглашение самому себе')
            if (Recommendation.objects.filter(user=user)
                .filter(creation_ts__gte=datetime.now()-timedelta(1)).count() >= 20 or
                (ib_account and Recommendation.objects.filter(ib_account=ib_account)
                                .filter(creation_ts__gte=datetime.now()-timedelta(1)).count() >= 20)):
                raise forms.ValidationError(u'Вы не можете приглашать более 20 человек в день')

        return self.cleaned_data

    def save(self, commit=True):
        instance = super(RecommendationForm, self).save(commit=False)
        instance.user = self.request.user
        instance.save(commit)
        return instance
