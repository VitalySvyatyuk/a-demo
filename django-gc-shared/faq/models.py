# coding: utf-8

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings


class Category(models.Model):
    MAIN_FAQ = 0
    GLOSSARY = 1
    INSTRUMENTS_INFO = 2

    FAQ_VERSIONS = (
        (MAIN_FAQ, "Main FAQ"),
        (GLOSSARY, "Glossary"),
        (INSTRUMENTS_INFO, "Instruments information"),
    )

    name = models.CharField(_('name'), max_length=160)
    priority = models.PositiveSmallIntegerField(_('priority'), default=0, help_text=_('defines order in category list'))
    slug = models.SlugField(_('slug'), help_text=_('short url name'))
    lang = models.CharField(_('language'), max_length=10, default=settings.LANGUAGES[0][0], choices=settings.LANGUAGES)
    faq_version = models.PositiveSmallIntegerField(u"Версия FAQ", choices=FAQ_VERSIONS, default=0)

    def __unicode__(self):
        return '%s [%s] [%s]' % (self.name, self.slug, self.get_lang_display())

    def natural_key(self):
        return self.slug

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ("-priority", )
        unique_together = ("slug", "lang")


class Question(models.Model):
    question = models.CharField(_('question'), max_length='1024')
    answer = models.TextField(_('answer'))
    priority = models.PositiveSmallIntegerField(_('priority'), default=0, help_text=_('defines order in category list'))
    categories = models.ManyToManyField(Category, related_name="questions")
    is_top10 = models.BooleanField(_('in TOP 10'), default=False)
    lang = models.CharField(_('language'), max_length=10, default=settings.LANGUAGES[0][0], choices=settings.LANGUAGES)
    published = models.BooleanField(u"Опубликовано", default=True)

    def __unicode__(self):
        return '%s' % self.question

    class Meta:
        verbose_name = _('Quesstion')
        verbose_name_plural = _('Quesstions')
        ordering = ("-priority", "-question",)
