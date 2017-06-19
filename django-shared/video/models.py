# coding: utf-8

import re

import urlparse
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from django.utils.translation import ugettext_lazy as _
from django.db import models

YOUTUBE_RE = re.compile('https?:\/\/.*\/(v|embed)\/([a-zA-Z-_0-9]+)')

class YoutubeVideo(object):
    def __init__(self, url=None, video_id=None):
        self.url = url
        self._video_id = video_id

    @staticmethod
    def video_id_from_url(url):
        qs = urlparse.urlparse(url).query
        try:
            return parse_qs(qs)['v'][0]
        except KeyError:
            pass
        match = YOUTUBE_RE.match(url)
        if match:
            return match.group(2)

    def embed_html(self, width=320, height=240):
        return '<iframe width="{}" height="{}" src="//www.youtube.com/embed/{}"' \
               ' frameborder="0" allowfullscreen></iframe>'.format(width, height, self.video_id)

    @property
    def video_id(self):
        return self._video_id or self.video_id_from_url(self.url)

    @property
    def screenshot_url(self):
        return 'https://img.youtube.com/vi/%s/0.jpg' % self.video_id

    def __getattribute__(self, attr):
        if attr.startswith('get_embed_html_'):
            width, height = attr[15:].split('_')
            return self.embed_html(int(width), int(height))
        return super(YoutubeVideo, self).__getattribute__(attr)


class VkontakteVideo(object):
    def __init__(self, embed_code):
        self.embed_code = embed_code

    def embed_html(self, width=320, height=240):
        code = re.sub('width="\d+"', 'width="%s"' % width, self.embed_code)
        code = re.sub('height="\d+"', 'height="%s"' % height, code)
        return code

    def __getattribute__(self, attr):
        if attr.startswith('get_embed_html_'):
            width, height = attr[15:].split('_')
            return self.embed_html(int(width), int(height))
        return super(VkontakteVideo, self).__getattribute__(attr)


class YoutubeVideoMixin(models.Model):
    youtube_video_url = models.CharField(_('Youtube video url'), max_length=50,
        help_text=_('A full url to youtube video, e.g.'
                    ' http://www.youtube.com/watch?v=IqaAZi2ppCE'),
        null=True,
        blank=True)

    @property
    def youtube(self):
        if self.youtube_video_url:
            return YoutubeVideo(url=self.youtube_video_url)

    class Meta:
        abstract = True


class VkontakteVideoMixin(models.Model):
    vkontakte_embed_code = models.TextField(_('Vkontakte embed code'),
        null=True,
        blank=True)

    @property
    def vkvideo(self):
        if self.vkontakte_embed_code:
            return VkontakteVideo(self.vkontakte_embed_code)

    class Meta:
        abstract = True
