# -*- coding: utf-8 -*-
import re
import os
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language
from shared.utils import upload_to
from project.validators import allow_file_extensions, allow_file_size
from django.contrib.postgres.fields import ArrayField

from node.models import Node
from pytils.dt import ru_strftime
import settings


class AnalyticsQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published=True, event_date__lte=datetime.now())


class AnalyticsMixin(models.Model):
    """Fields and functions added to each analytics model"""

    event_date = models.DateTimeField(_('Date'), db_index=True)

    template_name = 'uptrader_cms/analytics.html'
    objects = AnalyticsQuerySet.as_manager()

    @property
    def month(self):
        return datetime(self.event_date.year, self.event_date.month, 1)

    class Meta:
        abstract = True
        ordering = ['-event_date']


class CompanyNews(AnalyticsMixin, Node):
    slug = models.SlugField(default="", help_text=_("It will be used as the address of the page"), verbose_name=_("Slug"))
    image = models.ImageField(upload_to="news_images/%Y/%m/%d", max_length=2048, blank=True, null=True)
    template_name = 'uptrader_cms/company_news_detail.jade'

    hide = True

    class Meta:
        ordering = ['-event_date']
        verbose_name = _('Company news')
        verbose_name_plural = _('Company news')

    def __unicode__(self):
        return u"%s - %s" % (self.event_date.strftime("%H:%M %d.%m.%Y"), self.title)

    def get_context_values(self):
        values = super(CompanyNews, self).get_context_values()
        other_news = CompanyNews.objects.published().filter(language=self.language).exclude(pk=self.pk)[:3]

        values.update({
            "header": _("Company news"),
            "node": self,
            "other_news": other_news,
        })
        return values

    def clean(self):
        if self.slug and CompanyNews.objects.filter(language=self.language, slug=self.slug)\
                .exclude(pk=self.pk).exists():
            raise ValidationError(_("News with current language and slug already exists!"))
        super(CompanyNews, self).clean()

    def get_absolute_url(self):
        if self.slug:
            return reverse('company_news_by_slug', args=[self.slug])
        return reverse('company_news_by_id', args=[self.id])


# ECONOMIC CALENDAR


class IndicatorCountry(models.Model):
    name = models.CharField(_('Country'), max_length=20)
    slug = models.SlugField(_('Slug'))
    drupal_id = models.IntegerField(_('Old drupal id'), null=True, blank=True)
    code = models.CharField(max_length=3, null=True, blank=True)
    rate_name = models.CharField(_('Discount rate'), max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Country for indicator')
        verbose_name_plural = _('Countries for indicators')


class Indicator(models.Model):
    name = models.CharField(_('Indicator name'), max_length=255, null=True, default="")
    country = models.ForeignKey(IndicatorCountry, verbose_name=_('Country'), null=True)
    fxstreet_id = models.CharField(_('FxStreet ID'), max_length=255, blank=True, default="")

    def __unicode__(self):
        # FIXME HACK
        if get_language() == 'en' and self.name_en:
            return self.name_en
        if self.name_en:
            return '%s (%s)' % (self.name, self.name_en)

        return self.name

    class Meta:
        verbose_name = _('Economic indicator')
        verbose_name_plural = _('Economic indicators')


IMPORTANCE_CHOICES = (
    (1, _("Usual")),
    (2, _("Important")),
    (3, _("Very important")),
)

PERIOD_CHOICES = (
    ('week', _('a week before')),
    ('quarter', _('quarter')),
    ('month', _('month')),
)

class IndicatorEvent(models.Model):
    title = models.CharField(_('Event name'), max_length=255)
    importance = models.IntegerField(_('Importance'), choices=IMPORTANCE_CHOICES)
    indicator = models.ForeignKey(Indicator, verbose_name=_('Indicator'),
                                  help_text=_('Start typing the name of the indicator'))
    event_date = models.DateTimeField(_('Event time'))
    period = models.CharField(_('Period'), max_length=255, null=True,
                              blank=True, choices=PERIOD_CHOICES)
    period_date = models.DateField(_('Period'), null=True, blank=True)
    previous = models.CharField(_('Previous'), max_length=255, null=True,
                                blank=True)
    forecast = models.CharField(_('Prediction'), max_length=255, null=True,
                                blank=True)
    facts = models.CharField(_('Facts'), max_length=255, null=True, blank=True)

    #### START OF HACKS
    # FIXME
    # A series of UGLY, VERY UGLY localization HACKS
    REPLACEMENTS = (
        (re.compile(u'м/м'), _('m/m')),
        (re.compile(u'кв/кв'), _('q/q')),
        (re.compile(u'г/г'), _('y/y')),
        (re.compile(u'1 кв.'), _('1th quarter')),
        (re.compile(u'2 кв.'), _('2nd quarter')),
        (re.compile(u'3 кв.'), _('3rd quarter')),
        (re.compile(u'4 кв.'), _('4th quarter')),
        (re.compile(u'за нед. до.'), _('4th quarter')),
        (re.compile(u'млрд'), _('bln')),
        (re.compile(u'млн'), _('mln')),
        (re.compile(u'тыс.'), _('thousand')),
        (re.compile(u'барр'), _('barr')),
    )

    QUARTERS = {
        4: _('4th quarter of'),
        3: _('3rd quarter of'),
        2: _('2nd quarter of'),
        1: _('1st quarter of'),
    }

    def _get_value_display(name):
        def inner(self):
            value = getattr(self, name)
            if not value:
                return ""
            value = re.sub(r'&(?:\w+|#\d+);', '', value)  # Remove enitities like &nbsp;
            if get_language() == 'ru':
                return value
            for regex, repl in self.REPLACEMENTS:
                match = regex.search(value)
                if match:
                    value = regex.sub(repl, value)
            return value

        return inner

    get_forecast_display = _get_value_display('forecast')
    get_previous_display = _get_value_display('previous')
    get_facts_display = _get_value_display('facts')

    def get_period_display(self):
        if not self.period_date:
            return self.period

        lang = get_language()
        if self.period == 'week':
            if lang == 'ru':
                return ru_strftime(u'за нед. до %d %B', self.period_date, inflected=True)
            else:
                return self.period_date.strftime('a week before %B, %d')
        elif self.period == 'month':
            if lang == 'ru':
                return ru_strftime(u'%B', self.period_date)
            else:
                return self.period_date.strftime('%B')
        elif self.period == 'quarter':
            return u'%s %s' % (self.QUARTERS[(self.period_date.month - 1) / 3 + 1], self.period_date.year)

    # This is a hack to display importance
    # This can be easily fixed, but too lazy to do that
    @property
    def importance_css(self):
        maps = {1: '', 2: 'important', 3: 'very-important'}
        return maps[self.importance]

    ##### END OF HACKS

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-event_date']
        verbose_name = _('Economic event')
        verbose_name_plural = _('Economic events')


def docs_default_languages():
    return [x for x, _ in settings.LANGUAGES]


class LegalDocument(models.Model):

    name = models.CharField(_('Document name'), max_length=100)
    priority = models.IntegerField(_('Priority'), help_text=_('Display order from min(first) to max (last)'), default=0)
    languages = ArrayField(models.CharField(max_length=10),
                           default=docs_default_languages)

    EXTENSIONS = 'doc', 'docx', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pdf', 'xls', 'xlsx'
    FILESIZE_LIMIT = 1024 ** 2 * 15
    FILE_HELP_TEXT = _('Supported extensions: %(ext)s. Filesize limit: %(limit)s Mb') % {
        'ext': ', '.join(EXTENSIONS),
        'limit': '%.2f' % (FILESIZE_LIMIT / 1024.0 / 1024)
    }
    file = models.FileField(
        _("File"),
        upload_to=upload_to("legal_documents"),
        help_text=FILE_HELP_TEXT,
        validators=[
            allow_file_extensions(EXTENSIONS),
            allow_file_size(FILESIZE_LIMIT)
        ]
    )

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Legal document")
        verbose_name_plural = _("Legal documents")
