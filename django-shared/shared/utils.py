# -*- coding: utf-8 -*-
from django.core.urlresolvers import NoReverseMatch, reverse

import os
import re
import uuid
from urlparse import urljoin
from datetime import datetime, date, time, timedelta

from BeautifulSoup import BeautifulSoup, Comment
from django.conf import settings
from django.utils.deconstruct import deconstructible


def get_admin_url(obj):
    try:
        return reverse("admin:%s_%s_change" % (obj._meta.app_label,
                                               obj._meta.model_name),
                       args=[obj.pk])
    except NoReverseMatch:
        return


def define(name, default=None):
    """
    Updates settings module with a given default value for an
    option, if it's not defined already.
    """
    if not hasattr(settings, name):
        return setattr(settings, name, default)


VALID_TAGS = 'p i strong b u a h1 h2 h3 pre br img'


# From django snippets
def sanitize_html(value, valid_tags=VALID_TAGS, base_url=None):
    """Remove all html tags except VALID_TAGS"""
    rjs = r'[\s]*(&#x.{1,7})?'.join(list('javascript:'))
    rvb = r'[\s]*(&#x.{1,7})?'.join(list('vbscript:'))
    re_scripts = re.compile('(%s)|(%s)' % (rjs, rvb), re.IGNORECASE)
    validTags = valid_tags.split()
    validAttrs = 'href src width height'.split()
    urlAttrs = 'href src'.split() # Attributes which should have a URL
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        attrs = tag.attrs
        tag.attrs = []
        for attr, val in attrs:
            if attr in validAttrs:
                val = re_scripts.sub('', val) # Remove scripts (vbs & js)
                if attr in urlAttrs:
                    val = urljoin(base_url, val) # Calculate the absolute url
                tag.attrs.append((attr, val))

    return soup.renderContents().decode('utf8')


@deconstructible
class UploadTo(object):
    """
    Helper class, allowing FileField to "randomly" rename uploaded
    files.

    Usage:

        class SomeModel(models.Model):
            ...
            avatar = models.ImageField(upload_to=UploadTo("avatars/")
    """
    def __init__(self, prefix):
        upload_path = os.path.join(settings.UPLOAD_PATH, prefix)
        upload_path_absolute = os.path.join(settings.MEDIA_ROOT, upload_path)
        if not os.path.isdir(upload_path_absolute):
            os.makedirs(upload_path_absolute)
        self.upload_path = upload_path

    def __eq__(self, other):
        return self.upload_path == other.upload_path

    def __call__(self, instance, filename):
        fname, fext = os.path.splitext(filename)
        path = os.path.join(
            self.upload_path,
            uuid.uuid1().hex + fext)
        return path


def upload_to(prefix):
    return UploadTo(prefix)


def work_days_since_now(days, obj=None):
    """Adds N working days to original date."""
    if not obj:
        obj = datetime.now()
    counter = days
    newdate = obj + timedelta(0) # Like .copy()
    while counter >= 0:
        newdate = newdate + timedelta(1)
        if newdate.weekday() not in [6, 7]:
            counter -= 1
    return newdate


def get_last_weekday(weekday_iso_number, in_future=False, from_date=None):
    """Gets datetime object for the last ISO Weekday (1=Monday, 7=Sunday).
        If in_future is True, the Weekday is not the last, but the next.

        If today is Weekday, return today. If in_future, return the next Weekday.

        from_date should be date
        """

    if from_date:
        if isinstance(from_date, datetime):
            from_date = from_date.date()
        if not isinstance(from_date, date):
            raise ValueError("from_date should be date or at least datetime")
        date = from_date
    else:
        date = datetime.now().date()
    date_day_number = date.isoweekday()

    if date_day_number >= weekday_iso_number:
        if in_future:
            return date + timedelta(days=7 - date_day_number + weekday_iso_number)
        else:
            return date + timedelta(days=weekday_iso_number - date_day_number)
    else:
        if in_future:
            return date + timedelta(days=weekday_iso_number - date_day_number)
        else:
            return date + timedelta(days=-date_day_number - (7 - weekday_iso_number))


def random_media_url(path=''):
    #if settings.DEBUG or not settings.STATIC_URLS:
    return settings.STATIC_URL + path
    #try:
    #    return random.choice(settings.STATIC_URLS) + path
    #except AttributeError:
    #    return settings.STATIC_URL


def raw_to_tree_builder(query_set, fields_list):
    """
        Generates variations tree from raw table set.
        Tree stores as nested biltin python dicts
    """
    res_dict = {}

    #if no fields left to iterate
    if len(fields_list) == 0:
        return res_dict

    #getting all values for all fields and attach them to tree node
    for k in query_set.values_list(fields_list[0], flat=True):
        #pushing next node name to kwargs for QuerySet.filter() func
        kwargs = {fields_list[0]: k}
        #getting children nodes
        res_dict[k] = raw_to_tree_builder(query_set.filter(**kwargs), fields_list[1:])

    return res_dict


def get_combinations_regexp(values):
    """From a list of strings generate a regexp, which will contain
    lower, upper and title versions of this string"""
    result = []
    for value in values:
        result.extend([value.lower(), value.upper(), value.title()])
    return '|'.join(result)


def log_change(request, object, message):
    """
    Log that an object has been successfully changed.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, CHANGE
    from django.contrib.contenttypes.models import ContentType
    from django.utils.encoding import force_unicode

    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        object_repr=force_unicode(object),
        action_flag=CHANGE,
        change_message=message
    )


def descr(text=None, **kwargs):
    """
    Decorator function, wraps django.contrib.admin.ModelAdmin methods,
    and sets short_description and allow_tags attributes to the values
    passed to the decorator. If text argument is missing, it's populated
    from the method's name.
    """

    def decorator(func):
        func.short_description = text or func.__name__
        if "allow_tags" not in kwargs:
            kwargs["allow_tags"] = True
        for attr, value in kwargs.iteritems():
            setattr(func, attr, value)
        return func
    return decorator