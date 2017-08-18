# coding: utf-8
from email.header import Header
from email.mime.image import MIMEImage
import bleach

from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.template import Context, Template
from django.template.base import TemplateDoesNotExist
from django.template.defaultfilters import linebreaksbr, urlize, striptags
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, activate
from django.utils.translation import ugettext_lazy as _

from private_messages import models as django_messages
from project.fields import LanguageField
from sms import send as sms_send

import logging
log = logging.getLogger(__name__)


class LanguageStoreNotAvailable(Exception):
    pass


class MessageTemplate(models.Model):
    """A spam message template.

    Can contain MIME attachments (added easily via admin interface).
    Build the resulting email with "create_email". See it's docs for more
    info.
    """
    name = models.CharField(_("Template name"),
                            max_length=255)
    subject = models.CharField(_("Subject"), max_length=255,
                               help_text=_("The default subject if a campaign doesn't specify it"))
    text = models.TextField(_("Plaintext message"), null=True, blank=True,
                            help_text=u"Available variables: current_site, domain, "
                                      u"unsubscribe_url, browser_url, subject")
    html = models.TextField(_("HTML message"), null=True, blank=True,
                            help_text=u"Available variables: current_site, domain, "
                                      u"unsubscribe_url, browser_url, subject")
    language = LanguageField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Message template")
        verbose_name_plural = _("Message templates")

    def render_html(self, context):
        return template.Template(self.html).render(context)

    def render_text(self, context):
        return template.Template(self.text).render(context)

    def create_email(self, context=None, context_text=None,
                     context_html=None, subject=None,
                     html_processor=lambda text: text,
                     email_to=None, email_from=None,
                     reply_to=None, connection=None, msgtype=None):

        """Build an email.Message instance from self.

        self.text and self.html are django templates, and are rendered
        with context

        Creates a MIME alternative message with text/plain and text/html
        messages embedded.
        """
        # Create django template context from contexts
        if not context or not isinstance(context, template.Context):
            context = template.Context(context)

        # Create the email itself
        subject = Header(template.Template(subject or self.subject).render(context).encode('utf-8'), 'utf-8')

        translation.activate(self.language)

        if self.text:
            context.update(context_text or {})
            text = self.render_text(context).encode('utf-8')
            context.pop()
        else:
            text = ""

        if self.html:
            context.update(context_html or {})
            html = self.render_html(context)
            html = html_processor(html.encode('utf-8'))
            context.pop()
        else:
            html = ""

        if email_to is None:
            email_to = []
        elif isinstance(email_to, basestring):
            email_to = [email_to]
        if email_from is None:
            email_from = ""

        kwargs = {
            "subject": subject,
            "body": text,
            "from_email": email_from,
            "to": email_to,
            "headers": {},
        }

        if reply_to is not None:
            kwargs['headers']['Reply-To'] = reply_to

        if msgtype is not None:
            kwargs['headers']['X-Postmaster-Msgtype'] = msgtype
            kwargs['headers']['List-id'] = "<%s>" % msgtype

        list_unsubscribe = []
        if context.get('unsubscribe_email'):
            list_unsubscribe.append('<mailto:{}>'.format(context['unsubscribe_email']))

        if context.get('unsubscribe_url'):
            list_unsubscribe.append('<{}>'.format(context['unsubscribe_url']))

        if list_unsubscribe:
            kwargs['headers']['List-Unsubscribe'] = ", ".join(list_unsubscribe)

        if connection is not None:
            kwargs["connection"] = connection
        msg = EmailMultiAlternatives(**kwargs)
        msg.attach_alternative(html, "text/html")

        # Attach MIME attachments to the email
        # This is needed to display images embedded into html
        for attachment in self.attachments.all():
            image = MIMEImage(attachment.file.read())
            image.add_header('Content-ID', '<%s>' % attachment.content_id)
            image.add_header('Content-Disposition', 'inline')
            msg.attach(image)

        return msg


class NotificationSettingsQuerySet(models.QuerySet):
    def get_for_lang(self, language):
        result = self.filter(language__in=(language, "en"))
        if not result:
            raise self.model.DoesNotExist()
        elif len(result) == 1:
            return result[0]
        else:
            for item in result:
                if item.language == language:
                    return item


class NotificationSettings(models.Model):
    default_notification_template = models.ForeignKey(MessageTemplate, verbose_name=_('Letter template'))
    language = models.CharField('Language', default=settings.LANGUAGE_CODE, unique=True,
                                choices=settings.LANGUAGES, max_length=10)

    objects = NotificationSettingsQuerySet.as_manager()

    class Meta:
        verbose_name = _("Notification options")
        verbose_name_plural = _("Notifications options")


class NotificationTypesRegister(object):
    notification_types = []
    docs = {}
    app_names = {}

    @classmethod
    def register_notification(cls, code, verbose_name=None, app_name='', docs=''):
        """
        :param code: notification codename
        :param verbose_name: human-readable notification name
        :param app_name: Django application name
        :param docs: notification docs - available variables, etc.
        """
        if not verbose_name:
            verbose_name = code
        if code in cls.docs:
            raise ValueError("Duplicate declaration! Notification with codename '%s' already exists" % code)
        cls.notification_types.append((code, verbose_name))
        cls.docs[code] = docs
        cls.app_names[code] = app_name

    def __iter__(self):
        return iter(self.notification_types)


class NotificationQuerySet(NotificationSettingsQuerySet):
    def get_notification(self, code, language):
        return self.filter(published=True, notification_type=code).get_for_lang(language)

    def get_notification_for_user(self, code, user):
        if hasattr(user, 'profile'):
            if user.profile.country:
                language = user.profile.country.language
            else:
                language = "en"
        else:
            language = get_language()  # We'll just take the currently active language
        return self.get_notification(code, language)


class Notification(models.Model):
    notification_type = models.CharField(choices=NotificationTypesRegister(), max_length=2048,
                                         verbose_name=_("Notification type"))
    language = models.CharField('Language', default=settings.LANGUAGE_CODE,
                                choices=settings.LANGUAGES, max_length=10)
    published = models.BooleanField(_("Published"), default=False,
                                    help_text=_("If not published, it will not be used"))
    send_in_private = models.BooleanField(_('Send to private office/ My messages'), default=True)
    email_subject = models.CharField(
        _('Letter subject'), max_length=255,
    )
    html = models.TextField(verbose_name=_('Notification text'))

    duplicate_by_sms = models.BooleanField(verbose_name=_("Duplicate by SMS?"), default=False)
    text = models.TextField(verbose_name=_("SMS text"), blank=True, null=True, help_text=_('8 messages max'))

    objects = NotificationQuerySet.as_manager()

    def preview(self, parent=None):
        """ Shows preview of the notification as html

        :param parent: id of the notification parent template if None used current language
        :return: Html of the faceless notification
        """
        context = Context()

        if parent is None:
            settings_object = NotificationSettings.objects.get_for_lang(self.language)
        else:
            settings_object = NotificationSettings.objects.get(pk=parent)

        context["main_content"] = self.html_to_empty_template()

        template_object = settings_object.default_notification_template
        html_body = template_object.render_html(context)

        return html_body

    def html_to_empty_template(self):
        """
        Makes template from self.html with empty context and escaped variables
        """
        import re
        not_escaping_tags = ["load", "with", "endwith"]

        block_templatetag = re.compile(r"{{%(\s*(?!\s+)(?!{}).*?)%}}".format('|'.join(not_escaping_tags)))
        message_text = self.html
        message_text = block_templatetag.sub(r"{% templatetag openblock %}\1{% templatetag closeblock %}", message_text)
        message_text = message_text.replace(r"{{", r"{% templatetag openvariable %}")
        message_text = message_text.replace(r"}}", r"{% templatetag closevariable %}")

        return Template(message_text).render(Context())


    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        unique_together = (('notification_type', 'language'), )


def get_notification_language(user):
    """
    Returns site-specific notification language for this user. Raises
    LanguageStoreNotAvailable if this site does not use translated
    notifications.
    """
    try:
        if user.profile.country and user.profile.country.is_russian_language:
            return "ru"
        else:
            return "en"
    except:
        raise LanguageStoreNotAvailable


def get_formatted_messages(formats, label, context):
    """
    Returns a dictionary with the format identifier as the key. The values are
    are fully rendered templates with the given context.
    """
    format_templates = {}
    for format in formats:
        # conditionally turn off autoescaping for .txt extensions in format
        if format.endswith(".txt"):
            context.autoescape = False
        else:
            context.autoescape = True
        format_templates[format] = render_to_string('notification/%s/%s' % (label, format), context_instance=context)

    return format_templates


class CurrentSite(object):
    """
    A django.contrib.sites.Site-like object
    """
    def __init__(self, language="ru", user=None):
        if user is not None and hasattr(user, 'profile') and user.profile.registered_from in settings.PRIVATE_OFFICES:
            self.name = settings.PRIVATE_OFFICES[user.profile.registered_from]['site_name']
            self.domain = settings.PRIVATE_OFFICES[user.profile.registered_from]['domain']
        else:
            self.name = settings.SITE_NAME
            language_settings = settings.LANGUAGE_SETTINGS.get(language)
            if language_settings:
                self.domain = language_settings['redirect_to']
            else:
                self.domain = settings.LANGUAGE_SETTINGS['ru']['redirect_to']

    def __unicode__(self):
        return self.domain


def get_from_email(site_version):
    return settings.EMAILS.get(site_version, settings.DEFAULT_FROM_EMAIL)


def send(users, label, extra_context=None, display_subject_prefix=False, no_django_message=False):
    if extra_context is None:
        extra_context = {}

    current_language = get_language()

    formats = (
        'short.txt',
        'full.txt',
    )  # TODO make formats configurable

    for user in users:
        if isinstance(user, basestring):
            user = User(email=user)

        recipients = []
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        try:
            language = get_notification_language(user)
        except LanguageStoreNotAvailable:
            language = "ru"

        # update context with user specific translations
        context = Context({
            "user": user,
            "current_site": CurrentSite(language=language, user=user),
        })
        context.update(extra_context)
        try:
            notification = Notification.objects.get_notification_for_user(label, user)
        except Notification.DoesNotExist:
            log.warn('Notification named {1} did not find! current language {2}'
                     .format(user, label, language))
            notification = None

        sms_text = None
        if notification:
            language = notification.language
            activate(language)
            message_subject = Template(notification.email_subject).render(context)
            message_html = Template(notification.html).render(context)

            # strip all tags exclude bleach.sanitizer.ALLOWED_TAGS
            # a tags allowed
            message_text = mark_safe(bleach.clean(message_html, strip=True))
            
            if notification.duplicate_by_sms and notification.text:
                sms_text = Template(notification.text).render(context)
        else:
            activate(language)
            # get prerendered format messages
            try:
                messages = get_formatted_messages(formats, label, context)
            except TemplateDoesNotExist:
                return
            message_subject = messages['short.txt']
            message_text = messages['full.txt']
            message_html = linebreaksbr(urlize(messages['full.txt']))

        # Strip newlines from subject
        subject = ''.join(render_to_string('notification/email_subject.txt', {
            'message': message_subject,
            'display_prefix': display_subject_prefix,
        }, context).splitlines())

        profile = getattr(user, 'profile', None)
        site_version = profile.registered_from if profile else None

        settings_object = NotificationSettings.objects.get_for_lang(language)

        if settings_object and not site_version:
            context["main_content"] = message_html
            template_object = settings_object.default_notification_template
            html_body = template_object.render_html(context)
        else:
            html_body = None

        context['message'] = message_text
        text_body = render_to_string('notification/email_body.txt', context_instance=context)

        # GCPatch: create a new message using django-messages
        django_messages_recipients = []

        if user.pk:
            django_messages_recipients.append(user)

        if user.email:  # Email
            recipients.append(user.email)

        if not no_django_message and (not notification or notification.send_in_private):
            for recipient in django_messages_recipients:
                msg = django_messages.Message(subject=subject, body=text_body,
                                              recipient=recipient)
                msg.save()

        send_mail(subject, text_body,
                  get_from_email(site_version), recipients,
                  html_message=html_body)

        # sends sms if notification was found in db
        if notification:
            if sms_text and profile.phone_mobile:
                sms_send(to=profile.phone_mobile, text=sms_text)

    # reset environment to original language
    activate(current_language)
