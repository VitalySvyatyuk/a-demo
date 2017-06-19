# -*- coding: utf-8 -*-

import re
from datetime import datetime
import time

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.urlresolvers import reverse
from annoying.decorators import signals
from django.utils.translation import ugettext_lazy as _

from shared.werkzeug_utils import cached_property
from notification import models as notification
from shared.models import StateSavingModel
from shared.utils import get_admin_url
from video.models import YoutubeVideoMixin
from project.fields import LanguageField


class BaseTutorial(StateSavingModel):
    """An abstract base for Live and Remote tutorials"""
    name = models.CharField(_('Seminar'), max_length=100)
    slug = models.SlugField(_('Slug'), help_text=_("Machine name (for URL's)"))

    price = models.PositiveIntegerField(_("Price"), default=0)

    @cached_property
    def tutorial_count(self):
        return self.tutorials.count()

    @property
    def is_free(self):
        return self.price == 0

    def get_admin_url(self):
        return get_admin_url(self)

    def recorded(self):
        try:
            return self.tutorials.recorded()[0]
        except IndexError:
            return

    @property
    def length(self):
        """The total length of all the lessons"""
        return self.lessons.all().aggregate(sum=models.Sum('length'))['sum'] or 0

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


WEBINAR_CATEGORIES = (
    ("basic", _("For beginners")),
    ("topic", _("For advanced traders")),
    ("analytic", _("Market reviews")),
    ("for_partners", _("For partners")),
)


class Webinar(BaseTutorial):
    category = models.CharField(_("Webinar category"), choices=WEBINAR_CATEGORIES, max_length=20)
    description = models.TextField(_("Webinar description"))
    favorite = models.BooleanField(_("Favorite webinar"), default=False,
                                   help_text=_("If selected it is shown next to the webinars calendar"))
    password = models.CharField(_("Room password"), max_length=100, default='', blank=True)
    speaker = models.CharField(_("Webinar leader"), default='', max_length=200)
    language = LanguageField()

    class Meta:
        verbose_name = _('Webinar')
        verbose_name_plural = _('Webinars')

    def __unicode__(self):
        return self.name

    def get_education_type(self):
        return "webinar"

    @property
    def is_live(self):
        return False

    @property
    def is_remote(self):
        return False

    @property
    def is_webinar(self):
        return True

    def get_absolute_url(self):
        return reverse('education_tutorial_detail', args=['webinar', self.slug])

    def get_latest_recorded_event(self):
        return self.webinarevent_set.filter(youtube_video_url__isnull=False).exclude(youtube_video_url='').first()


class WebinarEvent(StateSavingModel, YoutubeVideoMixin):
    webinar = models.ForeignKey(Webinar, null=True)
    slug = models.SlugField(_('Slug'), help_text=_("Machine name (for URL's)"), unique=True)
    starts_at = models.DateTimeField(_("Webinar date"))
    link_to_room = models.URLField(_("Link to webinar room"), null=True, blank=True)

    class Meta:
        ordering = ("-starts_at",)

    def __unicode__(self):
        return u"%s - %s" % (self.starts_at.strftime("%H:%M %d.%m.%Y"), self.webinar.name)

    @property
    def is_free(self):
        return self.webinar.is_free

    @property
    def is_webinar(self):
        return self.webinar.is_webinar

    @property
    def as_ts(self):
        return int(time.mktime(self.starts_at.timetuple()))

    @property
    def in_future(self):
        return self.starts_at > datetime.now()

    @property
    def youtube_id(self):
        if not self.record:
            return
        match = re.search('.*v=([^&]+)', self.record)
        if match:
            return match.group(1)


@signals.post_save(sender=WebinarEvent)
def webinar_event_fill_slug(sender, instance, created, *args, **kwargs):
    if created:
        instance.slug = instance.webinar.slug + "_" + datetime.strftime(instance.starts_at, "%d%m%y")
        instance.save()


@signals.post_save(sender=WebinarEvent)
def on_webinar_changed(sender, instance, created, *args, **kwargs):
    is_record_changed = instance.changes.get('youtube_video_url')
    if is_record_changed is not None:
        users = [x.user for x in instance.registrations.all()]
        if is_record_changed[0] == "":
            notification.send(users, 'webinar_has_record', {'event': instance})
        else:
            notification.send(users, 'webinar_link_to_record_changed', {'event': instance})


class BaseRegistration(StateSavingModel):
    user = models.ForeignKey('auth.User', verbose_name=_('User'), null=True, related_name="%(class)s")
    creation_ts = models.DateTimeField(_('Registration time'), auto_now_add=True)
    is_paid = models.BooleanField(_('Paid'), default=False)
    paid_ts = models.DateTimeField(_('Paid time'), null=True, blank=True)
    content_type = models.ForeignKey(ContentType, editable=False, null=True)

    def __unicode__(self):
        return "%s - %s %s" % tuple(map(unicode, (self.tutorial, self.user.first_name, self.user.last_name)))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)

        if self.tutorial.is_free:
            self.is_paid = True
            self.paid_ts = datetime.now()

        if self.is_paid and not self.paid_ts:
            self.paid_ts = datetime.now()

        return super(BaseRegistration, self).save(*args, **kwargs)


class WebinarRegistration(BaseRegistration):
    tutorial = models.ForeignKey(WebinarEvent, related_name="registrations", verbose_name=u"Webinar")

    def __unicode__(self):
        return self.tutorial.webinar.name

    class Meta:
        verbose_name = _(u'Registration for the webinar')
        verbose_name_plural = _(u'Registration for the webinar')

    @cached_property
    def status(self):
        from pytz import timezone, utc
        unix = datetime(1970, 1, 1, tzinfo=utc)
        tz = timezone("Europe/Moscow")
        now = datetime.now()

        starts_at_utc = utc.normalize(tz.localize(self.tutorial.starts_at))
        td = starts_at_utc-unix
        self.starts_at_utc = int(
            (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6 * 1000)
        if self.tutorial.starts_at > now:
            return 'early'
        elif self.tutorial.starts_at <= now and (now-self.tutorial.starts_at).seconds < 15*60:
            return 'in_time'
        elif self.tutorial.youtube_video_url:
            return 'recorded'
        else:
            return 'late'
