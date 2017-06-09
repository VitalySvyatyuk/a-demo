# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
import re

from issuetracker.models import (
    UserIssue, IssueComment, IssueAttachment, ISSUE_STATUSES
)
from shared.widgets import DateWidget

from project.models import GROUP_NAMES

ALLOWED_GROUPS = (
    GROUP_NAMES[0],  # Portfolio management
    GROUP_NAMES[2],  # Back office
)


class UserIssueForm(forms.ModelForm):
    attachment = forms.FileField(label=_("Attachment"), required=False)
    department = forms.ChoiceField(label=_('Department'), widget=forms.HiddenInput,
                                   choices=ALLOWED_GROUPS, initial="Managers")

    FILESIZE_LIMIT = 1024 ** 2 * 5
    EXTENSIONS = ('doc', 'docx', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pdf')

    class Meta:
        model = UserIssue
        fields = ('title', 'department', 'text')

    def __init__(self, *args, **kwargs):
        super(UserIssueForm, self).__init__(*args, **kwargs)
        self.fields['attachment'].help_text = _('Supported extensions: %(ext)s. Filesize limit: %(limit)s Mb') % {
            'ext': ', '.join(self.EXTENSIONS),
            'limit': '%.2f' % (self.FILESIZE_LIMIT / 1024.0 / 1024)
        }
        self.fields["attachment"].validators = [self.check_extensions]

    def check_extensions(self, file):
        if not re.search('\.(%s)' % '|'.join(self.EXTENSIONS), file.name.lower()):
            raise forms.ValidationError(_('Unsupported file extension'))
        if file.size > self.FILESIZE_LIMIT:
            raise forms.ValidationError(_('File is too big.'))
        return file

    def clean_department(self):
        return Group.objects.get(name=self.cleaned_data['department'])

    def save(self, *args, **kwargs):
        author = kwargs.pop('author')
        kwargs['commit'] = False
        instance = super(UserIssueForm, self).save(*args, **kwargs)
        instance.author = author
        instance.save()  # Can't use commit=False, attachment needs pk

        if self.cleaned_data['attachment']:
            IssueAttachment.objects.create(issue=instance, user=author, file=self.cleaned_data['attachment'])
        return instance



class FilterIssuesForm(forms.Form):
    status = forms.ChoiceField(label=_('Status'), required=False, choices=ISSUE_STATUSES)
    from_date = forms.DateField(label=_('From date'), required=False, widget=DateWidget())
    to_date = forms.DateField(label=_('To date'), required=False, widget=DateWidget())

    def __init__(self, *args, **kwargs):
        super(FilterIssuesForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.choices[0] = ('', _('All'))


class IssueCommentForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ('text', )

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit') if kwargs.has_key('commit') else True
        kwargs['commit'] = False
        user = kwargs.pop('user')
        issue = kwargs.pop('issue')
        instance = super(IssueCommentForm, self).save(*args, **kwargs)
        instance.user = user
        instance.issue = issue
        if commit: instance.save()
        return instance


class IssueAttachmentForm(forms.ModelForm):
    class Meta:
        model = IssueAttachment
        fields = ('file', )

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit') if kwargs.has_key('commit') else True
        kwargs['commit'] = False
        user = kwargs.pop('user')
        issue = kwargs.pop('issue')
        instance = super(IssueAttachmentForm, self).save(*args, **kwargs)
        instance.user = user
        instance.issue = issue
        if commit: instance.save()
        return instance

