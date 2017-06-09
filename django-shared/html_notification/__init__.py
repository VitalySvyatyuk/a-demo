from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import get_connection, EmailMultiAlternatives

from notification.models import get_notification_language, get_language, LanguageStoreNotAvailable, activate, \
    get_formatted_messages, get_from_email


def send_mail(subject, msg_txt, msg_html, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(username=auth_user,
                                    password=auth_password,
                                    fail_silently=fail_silently)

    msg = EmailMultiAlternatives(subject.encode('utf-8'), msg_txt.encode('utf-8'), from_email, recipient_list,
                        connection=connection)

    msg.attach_alternative(msg_html.encode('utf-8'), 'text/html')

    return msg.send()


def send_now(users, label, extra_context=None, on_site=True, no_django_message=False):
    """
    Creates a new notice.

    This is intended to be how other apps create new notices.

    notification.send(user, 'friends_invite_sent', {
        'spam': 'eggs',
        'foo': 'bar',
    )

    You can pass in on_site=False to prevent the notice emitted from being
    displayed on the site.
    """
    if extra_context is None:
        extra_context = {}

    #protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    #current_site = Site.objects.get_current()

    #notices_url = u"%s://%s%s" % (
    #    protocol,
    #    unicode(current_site),
    #    reverse("notification_notices"),
    #)

    current_language = get_language()

    formats = (
        'short.txt',
        'full.txt',
        'full.html',
    ) # TODO make formats configurable

    for user in users:
        recipients = []
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        try:
            language = get_notification_language(user)
        except LanguageStoreNotAvailable:
            language = None

        if language is not None:
            # activate the user's language
            activate(language)

        # update context with user specific translations
        context = Context({
            "user": user,
            #"notice": ugettext(notice_type.display),
            #"notices_url": notices_url,
            #"current_site": current_site,
        })
        context.update(extra_context)

        # get prerendered format messages
        messages = get_formatted_messages(formats, label, context)

        # Strip newlines from subject
        subject = ''.join(render_to_string('notification/email_subject.txt', {
            'message': messages['short.txt'],
        }, context).splitlines())

        body_txt = render_to_string('notification/email_body.txt', {
            'message': messages['full.txt'],
        }, context)

        body_html = render_to_string('notification/email_body.html', {
            'message': messages['full.html'],
        }, context)

        if user.email: # Email
            recipients.append(user.email)

        profile = getattr(user, 'profile', None)
        site_version = profile.registered_from if profile else None
        send_mail(subject, body_txt, body_html, get_from_email(site_version), recipients)

    # reset environment to original language
    activate(current_language)

send = send_now
