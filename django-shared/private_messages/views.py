from datetime import datetime, date, time, timedelta

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages as django_messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.template.loader import get_template
from django.template import Context

from annoying.decorators import ajax_request, render_to

from private_messages.models import Message
from private_messages.forms import ComposeForm
from private_messages.utils import format_quote


@login_required
@render_to('messages/inbox.html')
def inbox(request):
    """
    Displays a list of received messages for the current user.
    with pagination by 30 messages per page
    """
    message_list = Message.objects.inbox_for(request.user)
    return {
        'message_list': message_list
    }


@login_required
def outbox(request, template_name='messages/outbox.html'):
    """
    Displays a list of sent messages by the current user.
    Optional arguments:
        ``template_name``: name of the template to use.
    """
    message_list = Message.objects.outbox_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list,
    }, context_instance=RequestContext(request))


@login_required
def trash(request, template_name='messages/trash.html'):
    """
    Displays a list of deleted messages.
    Optional arguments:
        ``template_name``: name of the template to use
    Hint: A Cron-Job could periodicly clean up old messages, which are deleted
    by sender and recipient.
    """
    message_list = Message.objects.trash_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list,
    }, context_instance=RequestContext(request))


@login_required
def compose(request, recipient_id=None, form_class=ComposeForm,
            template_name='messages/compose.html', success_url=None, recipient_filter=None):
    """
    Displays and handles the ``form_class`` form to compose new messages.
    Required Arguments: None
    Optional Arguments:
        ``recipient_id``: ID of a `django.contrib.auth` User, who should
                       receive the message
        ``form_class``: the form-class to use
        ``template_name``: the template to use
        ``success_url``: where to redirect after successfull submission
    """
    if request.method == "POST":
        form = form_class(request.POST, recipient_filter=recipient_filter, user=request.user)
        if form.is_valid():
            form.save(sender=request.user)
            django_messages.add_message(request, django_messages.SUCCESS, _(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            if request.GET.has_key('next'):
                success_url = request.GET['next']
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(user=request.user)
        if recipient_id is not None:
            recipients = list(User.objects.filter(pk=recipient_id))
            form.fields['recipient'].initial = recipients
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def reply(request, message_id, form_class=ComposeForm,
          template_name='messages/compose.html', success_url=None, recipient_filter=None):
    """
    Prepares the ``form_class`` form for writing a reply to a given message
    (specified via ``message_id``). Uses the ``format_quote`` helper from
    ``messages.utils`` to pre-format the quote.
    """
    parent = get_object_or_404(Message, id=message_id)

    if parent.sender != request.user and parent.recipient != request.user:
        raise Http404

    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter, user=request.user)
        if form.is_valid():
            form.save(sender=request.user, parent_msg=parent)
            django_messages.add_message(request, django_messages.SUCCESS, _(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            return HttpResponseRedirect(success_url)
    else:
        form = form_class({
                              'body': _(u"%(sender)s wrote:\n%(body)s") % {
                                  'sender': parent.sender,
                                  'body': format_quote(parent.body)
                              },
                              'subject': _(u"Re: %(subject)s") % {'subject': parent.subject},
                              'recipient': [parent.sender, ]
                          }, user=request.user)
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def delete(request, message_id, success_url=None):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's safe to remove it completely.
    A cron-job should prune the database and remove old messages which are
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.

    You can pass ?next=/foo/bar/ via the url to redirect the user to a different
    page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
    """
    user = request.user
    now = datetime.now()
    message = get_object_or_404(Message, id=message_id)
    deleted = False
    if success_url is None:
        success_url = reverse('messages_inbox')
    if request.GET.has_key('next'):
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == user:
        message.recipient_deleted_at = now
        deleted = True
    if deleted:
        message.save()
        django_messages.add_message(request, django_messages.SUCCESS, _(u"Message successfully deleted."))
        #if notification:
        #    notification.send([user], "messages_deleted", {'message': message,})
        return HttpResponseRedirect(success_url)
    raise Http404


@login_required
def undelete(request, message_id, success_url=None):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    user = request.user
    message = get_object_or_404(Message, id=message_id)
    undeleted = False
    if success_url is None:
        success_url = reverse('messages_inbox')
    if request.GET.has_key('next'):
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = None
        undeleted = True
    if message.recipient == user:
        message.recipient_deleted_at = None
        undeleted = True
    if undeleted:
        message.save()
        django_messages.add_message(request, django_messages.SUCCESS, _(u"Message successfully recovered."))
        #if notification:
        #    notification.send([user], "messages_recovered", {'message': message,})
        return HttpResponseRedirect(success_url)
    raise Http404


@login_required
def view(request, message_id, template_name='messages/view.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either
    the sender or the recipient. If the user is not allowed a 404
    is raised.
    If the user is the recipient and the message is unread
    ``read_at`` is set to the current datetime.
    """
    user = request.user
    now = datetime.now()
    message = get_object_or_404(Message, id=message_id)
    if (message.sender != user) and (message.recipient != user):
        raise Http404
    if message.read_at is None and message.recipient == user:
        message.read_at = now
        message.save()
    return render_to_response(template_name, {
        'message': message,
    }, context_instance=RequestContext(request))


@login_required
@require_POST
@ajax_request
def mark_as(request, mode):

    if request.POST and request.POST.get("message_ids"):

        for message_id in request.POST['message_ids'].split():
            message = Message.objects.get(pk=message_id)

            if message.recipient == request.user:

                if mode == "unread":
                    message.read_at = None
                elif mode == "read":
                    message.read_at = datetime.now()
                elif mode == "deleted":
                    message.recipient_deleted_at = datetime.now()

                message.save()
    return {}
