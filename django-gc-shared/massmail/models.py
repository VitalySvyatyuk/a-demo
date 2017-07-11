# coding: utf-8

import cgi
import hmac
import logging
import smtplib
import sys
import urllib
import urlparse
import datetime as datetime_module
from datetime import datetime
from email.header import Header
from email.mime.image import MIMEImage

from BeautifulSoup import BeautifulSoup
from annoying.decorators import signals
from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import QuerySet
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from platforms.models import TradingAccount
from platforms.mt4.external.models_users import RealUser

# import mt4.models
# import mt4.types
from massmail.utils import get_unsubscribe_url, get_signature, get_unsubscribe_email
from private_messages.models import Message
from project.fields import LanguageField
from project.utils import get_current_domain
from shared.utils import upload_to
from shared.validators import email_re
from sms import send

log = logging.getLogger(__name__)

def remove_emails_lte_hours(emails, previous_date_emails, hours_after_previous_campaign):
    """Method removes emails from email list which innapropriate by hours"""
    for e in emails.keys():
        if e not in {i[0] for i in previous_date_emails}:  # i[0] means emails
            del emails[e]
        else:
            sent_dates = (i[1] for i in previous_date_emails if i[0] == e)  # i[1] means dates
            # if atleast one sent message date from each of previous campaigns earlier
            # then {{hours_after_previous_campaign}} days -> remove mail
            for sent_date in sent_dates:
                if sent_date + datetime_module.timedelta(hours=hours_after_previous_campaign) > datetime.now():
                    del emails[e]
                    break
    return emails


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


class TemplateAttachment(models.Model):
    """A file attachment for the MessageTemplate"""
    file = models.FileField(upload_to=upload_to('attachments'))
    template = models.ForeignKey(MessageTemplate, related_name='attachments')
    content_id = models.SlugField(u'Content id',
            help_text='Used to insert links to the HTML message, for example Content id = "testimage",'
                      ' &ltimg src="cid:testimage" /&gt')

    def __unicode__(self):
        return u'%s: %s' % (self.template, self.content_id)


class Unsubscribed(models.Model):
    """An unsubscribed user"""
    email = models.EmailField(unique=True)
    creation_ts = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.email

    class Meta:
        ordering = ['email']


@signals.post_save(sender=Unsubscribed)
def make_profile_subscription_empty(sender, instance, created, **kwargs):
    if created:
        for user in User.objects.filter(email=instance.email):
            profile = user.profile
            profile.subscription.clear()


class MailingList(models.Model):
    """A dynamic mailing list"""
    name = models.CharField(max_length=255)
    query = models.TextField(u'Eval-query', null=True, blank=True,
                   help_text=u'Should return a list of Users')
    subscribers_count = models.PositiveIntegerField(default=0,
                                help_text=_("Number of subscribers"))
    creation_ts = models.DateTimeField(auto_now_add=True)
    auto_campaign_name = models.CharField(max_length=1000, editable=False, null=True, unique=True)

    def __unicode__(self):
        return _(u'%s (%s emails)') % (self.name, self.subscribers_count)

    class Meta:
        verbose_name = _('Mailing list')
        verbose_name_plural = _(u'Mailing lists')
        ordering = ['name']

    @property
    def countries(self):
        from geobase.models import Country

        if getattr(self, 'languages', None):
            return Country.objects.filter(language__in=self.languages)
        else:
            return Country.objects.all()

    def _eval_query(self):
        """Evaluate the query"""
        result = {}
        if not self.query:
            return result
        users = eval(self.query, {}, {'User': User, 'datetime': datetime_module, 'Q': models.Q, "TradingAccount": TradingAccount, "RealUser":RealUser,
                                      # 'account_types': mt4.types, 'mt4_models': mt4.models,
                                      'massmail_models': sys.modules[__name__]})
        if isinstance(users, QuerySet):
            users = users.filter(models.Q(profile__country__in=self.countries) |
                                 models.Q(profile__country__isnull=True))
        else:
            from profiles.models import UserProfile
            allowed_profiles = UserProfile.objects.filter(models.Q(country__in=self.countries) |
                                                          models.Q(country__isnull=True))
            users = (user for user in users if user.profile in allowed_profiles)
        for user in users:
            result[user.email] = (user.first_name, user.last_name)
        return result

    def get_emails(self, languages=None, ignore_unsubscribed=False):
        """Get unique emails for this mailing list
        """
        self.languages = languages
        result = {}
        result.update(self._eval_query())
        subscribers = self.subscribers.all()
        if subscribers:
            from geobase.models import Country
            negative_countries = Country.objects.exclude(id__in=self.countries.values('id'))
            subscribers = subscribers.exclude(email__in=User.objects.filter(email__in=subscribers.values('email'),
                                                                            profile__country__in=negative_countries)
                                                                    .values('email'))
        for subscriber in subscribers:
            result[subscriber.email] = (subscriber.first_name,
                                        subscriber.last_name)

        if not ignore_unsubscribed:
            for email in Unsubscribed.objects.values_list('email', flat=True):
                if email in result:
                    del(result[email])

        # Filter only valid emails
        result = dict((email, data) for email, data in result.iteritems()\
                if email_re.match(email))

        return result

    def get_phone_numbers(self, languages=None, confirmed_only=True):
        from profiles.models import UserProfile
        emails = self.get_emails(
            languages=languages,
        ).keys()
        result = UserProfile.objects.filter(user__email__in=emails).values_list("phone_mobile", flat=True)

        if confirmed_only:
            result = result.filter(user__validations__key="phone_mobile", user__validations__is_valid=True)
        return set(result)


class Subscribed(models.Model):
    mailing_list = models.ForeignKey(MailingList, related_name='subscribers')
    email = models.EmailField()
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    creation_ts = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s: %s' % (self.mailing_list, self.email)


class CampaignType(models.Model):
    title = models.CharField(max_length=100)
    unsubscribed = models.PositiveIntegerField(_('Unsubscribed'), default=0)

    def __unicode__(self):
        return self.title


def campaign_languages_default():  # OK.
    return ['ru']


class Campaign(models.Model):
    CAMPAIGN_STRATEGY = (  # TODO: Translations here won't work since it's inside class definition
        ('none', _("Didn't get the message")),
        ('all', _("Got the message")),
        ('read', _("Read the message")),
        ('unread', _("Didn't read the message")),
        ("clicked", _("Clicked on a link")),
        ("unclicked", _("Read, but didn't click on a link")),
    )

    name = models.CharField(max_length=255, verbose_name=_("Campaign name"))
    security_notification = models.BooleanField(_("Force send"), default=False,
                                                help_text=_("Forcefully sent to unsubscribed clients"))
    template = models.ForeignKey(MessageTemplate, verbose_name=_("Template"))
    mailing_list = models.ManyToManyField(MailingList, verbose_name=_("Mailing lists"), blank=True)
    negative_mailing_list = models.ManyToManyField(
        MailingList, verbose_name=_("Exclusion lists"), related_name="excluded_from_campaigns", blank=True, null=True,
        help_text=_("These emails will be excluded from the campaign"),
    )

    order_weight = models.IntegerField(_("Weight of campaign"),
                                       help_text=_("Lower value means this campaign trying to send first"),
                                       default = 0)
    previous_campaigns = models.ManyToManyField('self', related_name="next_campaigns", blank=True, null=True, help_text="Just ctrl+click to previous campaign(s) ")
    previous_campaigns_type = models.CharField(max_length=20, choices=CAMPAIGN_STRATEGY, default='', blank=True)

    hours_after_previous_campaign = models.FloatField(_("Hours from previous campaign"), default=0,
                                                       help_text=_("Users which received mail from previous campaign earlier than this hours will be ignored"))

    languages = ArrayField(models.CharField(max_length=10), default=campaign_languages_default)
    is_active = models.BooleanField(_("Active"), default=False,
                                    help_text=_("Set campaign to Active to send it immediately"))
    is_sent = models.BooleanField(_("Is sent"), default=False)

    send_once = models.BooleanField(_("Delayed campaign"), default=False)
    send_once_datetime = models.DateTimeField(_("Date of mailing"), null=True, blank=True)

    send_period = models.BooleanField(_("Send periodicaly"), default=False)
    cron = models.CharField(_("Schedule (in cron format)"), max_length=100, blank=True, null=True)

    personal = models.BooleanField(_("Personal greeting"), default=True)
    send_email = models.BooleanField(_("Send email"), default=True)
    send_in_private = models.BooleanField(_("Send to internal messages"), default=True)
    ga_slug = models.SlugField(_("Name in GA"), help_text=_("Name in Google Analytics"), null=True, blank=True)
    email_subject = models.CharField(
        _("Message subject"), max_length=255,
        help_text="Available variables: first_name, last_name For example: Hi, {{first_name}}!"
    )
    custom_email_from = models.CharField(
        _("Sender's email"), max_length=100, default='', blank=True,
        help_text=_("name@example.com Leave empty to use default address")
    )
    custom_email_from_name = models.CharField(
        _("Sender's name"), max_length=255, default='', blank=True,
        help_text=_("Leave empty to use default name")
    )

    po_sent_count = models.PositiveIntegerField(_("Messages sent"), default=0)
    _lock = models.BooleanField("Lock", default=False, help_text=_("Lock is active when campaign is being sent"))
    creation_ts = models.DateTimeField(_("Creation date"), auto_now_add=True)
    unsubscribed = models.PositiveIntegerField(_("Unsubscribed"), default=0)
    is_auto = models.BooleanField(_("Automatical"), default=False)
    campaign_type = models.ManyToManyField(CampaignType, verbose_name=_("Campaign type"), blank=False, null=True)

    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def __unicode__(self):
        return self.name

    @property
    def click_count(self):
        return self.clicks.filter(clicked=True).count()

    @property
    def open_count(self):
        return self.clicks.filter(opened=True).count()

    @property
    def sent_count(self):
        return self.sent_messages.count()

    def _generate_unique_token(self, email):
        """Generate a unique identifier for campaign and email

        This is used to count unique clicks
        """
        return hmac.new('%s:%s' % (self.id, email)).hexdigest()

    def process_html(self, html, email=None):
        """Process the raw html specifically for this email

        1. Insert google analytics urls if needed
        2. Insert email, campaign_id and hash to all images and links
           to determine if the email was opened
        3. Insert email, campaign_id and hash
           to every A link to determine that a link was clicked from an email
        """

        # Add google analytics urls and middleware identification params into
        # "a" tags
        soup = BeautifulSoup(html)

        for tag in soup.findAll(['a', 'img']):
            attr_name = tag.name == 'a' and 'href' or 'src'
            parsed_url = urlparse.urlparse(tag[attr_name])
            # Do not add utm marks if it is an external link
            if not any(map(lambda h: h in parsed_url.netloc, settings.ALLOWED_HOSTS)):
                continue
            qs = dict(cgi.parse_qsl(parsed_url.query))
            if tag.name == 'a' and self.ga_slug:
                qs['utm_source'] = 'email'
                qs['utm_medium'] = 'emailsend'
                qs['utm_campaign'] = self.ga_slug
            if email:
                qs['email'] = email
                qs['campaign_id'] = self.id
                qs['signature'] = get_signature(email)
            tag[attr_name] = urlparse.urlunparse(
                (parsed_url.scheme,
                 parsed_url.netloc,
                 parsed_url.path,
                 parsed_url.params,
                 urllib.urlencode(qs),
                 parsed_url.fragment))

        return unicode(soup)

    def send(self, send_inactive=False, mail_list=None, global_template_context=None):
        """Send mass mail.

        Read the comments to understand WHAT it does.
        send_inactive added for sending mail once or on cron task
        """
        if not self.is_active and not send_inactive:
            return
        # Lock through DB from sending more than one thread at a time
        if self._lock:
            return
        translation.activate(self.template.language)
        self._lock = True
        self.save()
        server = None
        try:
            # Get the emails list
            emails = {}
            for ml in self.mailing_list.all():
                emails.update(ml.get_emails(languages=self.languages,
                                            ignore_unsubscribed=self.security_notification))

            # If mail_list argument provided append them to emails
            if mail_list is not None:
                emails.update(mail_list)

            # Delete emails from negative lists
            for nml in self.negative_mailing_list.all():
                for email in nml.get_emails(ignore_unsubscribed=self.security_notification):
                    if email in emails:
                        del emails[email]


            if not self.security_notification:
                #Delete emails of users,which unsubscribed for this type of campaign
                from profiles.models import UserProfile
                unsubscribed_profiles = UserProfile.objects.filter(user__email__in=emails)\
                                                           .exclude(subscription__in=self.campaign_type.all())

                for profile in unsubscribed_profiles:
                    if profile.user.email in emails:
                        del emails[profile.user.email]


            # Do not send message to already sent emails
            for msg in self.sent_messages.all():
                if msg.email in emails:
                    del(emails[msg.email])

            if self.previous_campaigns_type == "all":
                previous_date_emails = []
                for c in self.previous_campaigns.all():
                    previous_date_emails += (c.sent_messages.all().values_list('email', "creation_ts"))
                emails = remove_emails_lte_hours(emails, previous_date_emails, self.hours_after_previous_campaign)

            elif self.previous_campaigns_type == "none":
                previous_emails = set()
                for c in self.previous_campaigns.all():
                    previous_emails |= set(c.sent_messages.all().values_list('email', flat=True))
                for e in emails.keys():
                    if e in previous_emails:
                        del emails[e]

            elif self.previous_campaigns_type == "read":
                previous_date_emails = []
                for c in self.previous_campaigns.all():
                    previous_date_emails += c.clicks.filter(opened=True).values_list('email', "creation_ts")
                emails = remove_emails_lte_hours(emails, previous_date_emails, self.hours_after_previous_campaign)

            elif self.previous_campaigns_type == "unread":
                previous_date_emails = []
                for c in self.previous_campaigns.all():
                    previous_date_emails += c.clicks.filter(opened=False).values_list('email', "creation_ts")
                emails = remove_emails_lte_hours(emails, previous_date_emails, self.hours_after_previous_campaign)
            elif self.previous_campaigns_type == "clicked":
                previous_date_emails = []
                for c in self.previous_campaigns.all():
                    previous_date_emails += c.clicks.filter(clicked=False).values_list('email', "creation_ts")
                emails = remove_emails_lte_hours(emails, previous_date_emails, self.hours_after_previous_campaign)
            elif self.previous_campaigns_type == "unclicked":
                previous_date_emails = []
                for c in self.previous_campaigns.all():
                    previous_date_emails += c.clicks.filter(clicked=False).values_list('email', "creation_ts")
                emails = remove_emails_lte_hours(emails, previous_date_emails, self.hours_after_previous_campaign)

            # this branch means if campaign have no previous(type) but has delay days from previous
            # (than we calculate days after user registration)
            elif self.hours_after_previous_campaign > 0:
                previous_emails_registered = dict(User.objects.filter(email__in=emails.keys()).values_list('email', "date_joined"))

                for e in emails.keys():
                    try:
                        if previous_emails_registered[e] + \
                                datetime_module.timedelta(hours=self.hours_after_previous_campaign) > datetime.now():
                            del emails[e]
                    except IndexError:
                        log.warning("Trying to send massmail to {} "
                                    "but failed because user with current email didnt found in user db".format(e))




            # Get Django's SMTP connection
            server = get_connection()
            server.open()

            sent_emails = []

            for email, data in emails.iteritems():

                if self.send_in_private:
                    log.debug('Sending message (campaign_id %s) to %s' % (self.id, email))
                    users = User.objects.filter(email=email)
                    if users:
                        user = users[0]
                        if not user.received_messages.filter(campaign=self).exists():
                            context = template.Context({'first_name': user.first_name, 'last_name': user.last_name})
                            subject = template.Template(self.email_subject).render(context).encode('utf-8')
                            message_private_office = Message(campaign=self, recipient=user, subject=subject)
                            message_private_office.save()

                            self.po_sent_count += 1
                            self.save()
                    else:
                        log.exception('Error while sending message to %s: no profile' % email)

                if self.send_email:

                    if email in sent_emails:
                        continue

                    if not email_re.match(email):
                        log.error('Email %s does not look like an email, skipping' % email)
                        continue

                    # Check twice, that we haven't sent the message yet
                    # FIXME:
                    # This creates some overhead, but it is a quick way to solve
                    # concurrecy problems
                    if self.sent_messages.filter(email=email).exists():
                        continue

                    if len(data) > 2:
                        # local context is specific for this email and is set at mail_list,
                        # global context is the same for all emails and is set at send
                        first_name, last_name, per_user_template_context = data
                    else:
                        first_name, last_name = data
                        per_user_template_context = None

                    context = self.get_context(first_name, last_name, email)

                    if global_template_context is not None:
                        context.update(global_template_context)
                    if per_user_template_context is not None:
                        context.update(per_user_template_context)

                    # Make separate contexts for html and text versions
                    context_text, context_html = self._get_block_context(context)

                    if self.custom_email_from:
                        email_from = "%s <%s>" % (self.custom_email_from_name, self.custom_email_from)
                        reply_to = self.custom_email_from
                    else:
                        email_from = settings.MASSMAIL_DEFAULT_FROM_EMAIL
                        reply_to = settings.MASSMAIL_DEFAULT_REPLY_TO

                    # Create a proper MIME/Multipart email and send it
                    msg = self.template.create_email(context,
                                                     context_text=context_text,
                                                     context_html=context_html,
                                                     subject=self.email_subject,
                                                     html_processor=lambda text: self.process_html(text, email=email),
                                                     email_to=email,
                                                     email_from=email_from,
                                                     reply_to=reply_to,
                                                     connection=server,
                                                     msgtype='massmail_campaign_{}'.format(self.pk),
                                                     )

                    log.debug('Sending email (campaign_id %s) to %s' % (self.id, email))
                    try:
                        msg.send()
                    except smtplib.SMTPRecipientsRefused:
                        log.exception('Error while sending to email %s' % email)
                        continue
                    sent_emails.append(email)
                    SentMessage.objects.create(campaign=self, email=email)

            self.is_active = False
            self.is_sent = True
        finally:
            if server is not None:
                server.close()
            self._lock = False
            self.save()

    def _get_default_context(self, email=None):
        domain = get_current_domain()
        # 'current_site' used to be Site object, but we dont use it anymore, so lets just mimic it
        context = {
            'current_site': {"domain": domain.lstrip("https://")},
            'domain': domain,
        }
        if email and not self.security_notification:
            context['unsubscribe_url'] = get_unsubscribe_url(email, self.id, language=self.template.language)
            context['unsubscribe_email'] = get_unsubscribe_email(email, self.id, language=self.template.language)
        context['browser_url'] = domain + self.get_absolute_url()
        context['subject'] = template.Template(self.email_subject).render(template.Context({}))

        return template.Context(context)

    def get_context(self, first_name, last_name, email):

        context = self._get_default_context(email)

        # Fill the context with names if needed
        if self.personal:
            context['first_name'] = first_name
            context['last_name'] = last_name

        return context

    def get_absolute_url(self):
        return reverse('massmail_view_campaign', args=[self.id])

    def _get_block_context(self, context=None):
        if not context:
            context = self._get_default_context()
        context_text = {}
        context_html = {}
        for block in self.blocks.all():
            # Render block context as templates to place context
            # variables into them
            context_text[block.key] = template.\
                Template(block.value_text).render(template.Context(context))
            context_html[block.key] = template.\
                Template(block.value_html).render(template.Context(context))

        return template.Context(context_text), template.Context(context_html)

    def render_html(self, **context):
        translation.activate(self.template.language)
        _context = self._get_default_context()
        if context:
            _context.update(context)
        html_context = self._get_block_context(_context)[1]
        _context.update(html_context)
        html = self.template.render_html(_context)
        html = self.process_html(html.encode('utf-8'), email=context.get('email'))
        return html

    def render_text(self, **context):
        translation.activate(self.template.language)
        _context = self._get_default_context()
        if context:
            _context.update(context)
        text_context = self._get_block_context(_context)[0]
        _context.update(text_context)
        text = self.template.render_text(_context)
        return text


class OpenedCampaign(models.Model):
    """If an email opened the campaign or clicked a link in it"""
    campaign = models.ForeignKey(Campaign, db_index=True, related_name='clicks')
    email = models.EmailField()
    creation_ts = models.DateTimeField(auto_now_add=True)
    clicked = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s: %s' % (self.campaign, self.email)

    class Meta:
        unique_together = ('campaign', 'email')


class MessageBlock(models.Model):
    """A variable in django template"""
    campaign = models.ForeignKey(Campaign, related_name='blocks')
    key = models.SlugField(_('Key'),
                           help_text=_("Name of the block in the template, for example main_content"),
                           default='main_content')
    value_text = models.TextField(verbose_name=_("Plaintext message"),
                                  null=True, blank=True,
                                  help_text="Available variables: first_name, last_name For example: Hi, {{first_name}}!")
    value_html = models.TextField(verbose_name=_("HTML message"),
                                  null=True, blank=True,
                                  help_text="Available variables: first_name, last_name For example: Hi, {{first_name}}!")

    def __unicode__(self):
        return u'%s: %s' % (self.campaign, self.key)

    class Meta:
        verbose_name = _("Content block")
        verbose_name_plural = _("Content blocks")


class SentMessage(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='sent_messages')
    email = models.EmailField()
    creation_ts = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s: %s' % (self.campaign, self.email)


class SmsCampaign(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Campaign name"))
    mailing_list = models.ManyToManyField(MailingList,
                                          verbose_name=_("Mailing lists"), blank=True)
    negative_mailing_list = models.ManyToManyField(MailingList,
                                          verbose_name=_("Exclusion lists"),
                                          help_text=_("These emails will be excluded from the campaign"),
                                          related_name="excluded_from_sms_campaigns",
                                          blank=True, null=True)
    is_active = models.BooleanField(_("Active"), default=False,
                help_text=_("Set campaign to Active to send it immediately"))
    is_sent = models.BooleanField(_("Is sent"), default=False)
    is_scheduled = models.BooleanField(_("Scheduled"), default=False)
    languages = ArrayField(models.CharField(max_length=10), default=campaign_languages_default)
    schedule_date = models.DateField(_("Send at (date)"), null=True, blank=True)
    schedule_time = models.TimeField(_("Send at (time)"), null=True, blank=True)
    creation_ts = models.DateTimeField(auto_now_add=True)
    campaign_type = models.ManyToManyField(CampaignType,
                                          blank=True, null=True)
    unsubscribed = models.PositiveIntegerField(_("Unsubscribed"), default=0)

    text = models.TextField(_("Message text"), help_text=_("8 SMS max"))
    confirmed_only = models.BooleanField(_("Send only to verified phone numbers"), default=True)
    _lock = models.BooleanField(u'Lock', default=False,
                                help_text=_("Lock is active when campaign is being sent"))

    def __unicode__(self):
        return self.name

    @property
    def sent_count(self):
        return self.sent_messages.count()

    def send(self):
        """Send mass sms.

        Read the comments to understand WHAT it does.
        send_inactive added for sending mail once or on cron task
        """

        if not self.is_active:
            return
        # Lock through DB from sending more than one thread at a time
        if self._lock:
            return
        self._lock = True
        self.save()
        try:
            # Get the phones list
            phone_numbers = []
            for ml in self.mailing_list.all():
                phone_numbers.extend(ml.get_phone_numbers(
                    languages=self.languages,
                    confirmed_only=self.confirmed_only
                ))
            # Delete phones from negative lists
            for nml in self.negative_mailing_list.all():
                for phone_number in nml.get_phone_numbers():
                    if phone_number in phone_numbers:
                        phone_numbers.remove(phone_number)
            from profiles.models import UserProfile
            unsubscribed_profiles = UserProfile.objects.filter(phone_mobile__in=phone_numbers)\
                                                       .exclude(subscription__in=self.campaign_type.all())

            for profile in unsubscribed_profiles:
                if profile.phone_mobile in phone_numbers:
                    phone_numbers.remove(profile.phone_mobile)
            for msg in self.sent_messages.all():
                if msg.phone_number in phone_numbers:
                    phone_numbers.remove(msg.phone_number)
            sent_sms = []
            for phone_number in phone_numbers:
                if phone_number in sent_sms:
                    continue

                # Check twice, that we haven't sent the message yet
                # FIXME:
                # This creates some overhead, but it is a quick way to solve
                # concurrecy problems
                if phone_number in self.sent_messages.values_list('phone_number', flat=True):
                    continue

                send(to=phone_number,text=self.text)
                sent_sms.append(phone_number)
                SentSms.objects.create(campaign=self, phone_number=phone_number)

            self.is_active = False
            self.is_sent = True
            self.is_scheduled = False
            self.save()
        finally:
            self._lock = False
            self.save()

class SentSms(models.Model):
    campaign = models.ForeignKey(SmsCampaign, related_name='sent_messages')
    phone_number = models.CharField(max_length=20)
    creation_ts = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s: %s' % (self.campaign, self.phone_number)
