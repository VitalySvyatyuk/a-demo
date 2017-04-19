from datetime import datetime, date, time, timedelta
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.contrib.auth.models import User

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from private_messages.models import Message
from private_messages.fields import CommaSeparatedUserField

class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = CommaSeparatedUserField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))


    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        self.user = kwargs.pop('user')
        super(ComposeForm, self).__init__(*args, **kwargs)
        if recipient_filter is not None:
            self.fields['recipient']._recipient_filter = recipient_filter

    def clean_recipient(self):
        if not self.user.is_active:
            raise forms.ValidationError(_(u"Your account is not activated. You cannot send private messages."))
        return self.cleaned_data['recipient']

    def save(self, sender, parent_msg=None):
        if not self.user.is_active:
            return
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender = sender,
                recipient = r,
                subject = subject,
                body = body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = datetime.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
            if notification:
                if parent_msg is not None:
                    #notification.send([sender], "messages_replied", {'message': msg,}, no_django_message=True)
                    notification.send([r], "messages_reply_received", {'message': msg,}, no_django_message=True)
                else:
                    #notification.send([sender], "messages_sent", {'message': msg,}, no_django_message=True)
                    notification.send([r], "messages_received", {'message': msg,}, no_django_message=True)
        return message_list
