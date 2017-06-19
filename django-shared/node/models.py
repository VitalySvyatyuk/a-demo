# -*- coding: utf-8 -*-
import logging
from itertools import chain

from access import PublicAccessMixin, LoggedInAccessMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _, get_language
from shared.utils import get_admin_url


log = logging.getLogger(__name__)

bodyFormats = (
    ('stripped', _('Stripped HTML')),
    ('html', _('Full HTML'))
)


class Node(models.Model, PublicAccessMixin):
    language = models.CharField(_('Language'), default=settings.LANGUAGE_CODE, db_index=True,
                                choices=settings.LANGUAGES, max_length=10)
    content_type = models.ForeignKey(ContentType, editable=False, null=True)
    title = models.CharField(_('Title'), max_length=250)
    url_alias = models.CharField(_('URL alias'), max_length=160, blank=True)
    body = models.TextField(u"Тело")
    published = models.BooleanField(_('Published'), default=False)
    sitemapped = models.BooleanField(u"Включить в карту сайта", default=False)
    creation_ts = models.DateTimeField(_('Creation timestamp'), auto_now_add=True)
    update_ts = models.DateTimeField(_('Update timestamp'), auto_now=True)
    author = models.ForeignKey(User, verbose_name=_('Author'), editable=False)
    template_name = 'node/default.jade'
    hide = False

    @classmethod
    def object_list_url(cls):
        return reverse('%s_list' % cls.__name__.lower())

    def get_template_name(self, request):
        return self.template_name

    def save(self, *args, **kwargs):
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        super(Node, self).save(*args, **kwargs)

    def as_leaf_class(self):
        content_type = self.content_type
        model = content_type.model_class()
        if model == Node:
            return self
        return model.objects.get(id=self.id)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        raise NotImplementedError("Tried to access 'get_absolute_url' on Node model class")

    def render(self):
        t = Template(self.body)
        try:
            return t.render(Context(self.get_context_values()))
        except:
            log.exception('Error while rendering node %s' % self.id)
            return self.body

    def edit_link(self):
        return get_admin_url(self)

    def get_context_values(self):
        return {'LANGUAGE_CODE': get_language()}

    class Meta:
        ordering = ('-creation_ts',)
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')


class Page(Node):
    header = models.CharField(_('Header'), max_length=255)

    def get_absolute_url(self):
        domain = settings.LANGUAGE_SETTINGS[self.language]["redirect_to"]
        if self.url_alias:
            return '%s/%s' % (domain, self.url_alias)
        return domain + reverse('node.views.node', args=[self.id])

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')


class LoggedInUserPage(LoggedInAccessMixin, Page):
    class Meta:
        verbose_name = _('LoggedInUserPage')
        verbose_name_plural = _('LoggedInUserPages')
