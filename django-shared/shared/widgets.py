# -*- coding: utf-8 -*-

from django.conf import settings
from django.forms import DateInput, Media, Widget
from django.utils.safestring import mark_safe
from django.utils.translation import get_language


class DateWidget(DateInput):
    @property
    def media(self):
        js = [settings.STATIC_URL + 'js/jquery-ui-1.10.4.custom.min.js', settings.STATIC_URL + 'js/datepicker.js']
        css = [settings.STATIC_URL + 'css/gcapital-ui/1.10.4/jquery-ui-1.10.4.custom.min.css']
        if get_language() == 'ru':
            js.append(settings.STATIC_URL + 'js/jquery.ui.datepicker-ru.js')
        return Media(js=js, css={"all": css})

    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        attrs['class'] = 'datepicker'
        kwargs['attrs'] = attrs
        super(DateWidget, self).__init__(*args, **kwargs)


# TODO: fix shared.fields JSONField to make use of this widget by default
class JsonInput(Widget):
    """ A widget to use with jsonfield.JSONField

    Copied from http://code.djangoproject.com/ticket/7406
    and modified a bit
    """

    def render(self, name, value, attrs=None):
        ret = ''
        if value and len(value) > 0:
            for key in value.keys():
                ret += '<input type="text" name="json_key_%(name)s[]"'\
                       ' value="%(key)s"> <input type="text" '\
                       'name="json_value_%(name)s[]" '\
                       'value="%(value)s"><br />' % {
                    'name': name,
                    'key': key,
                    'value': value[key]
                }
        ret += '<input type="text" name="json_key[]"> <input type="text"'\
            ' name="json_value[]">'
        return mark_safe(ret)

    def value_from_datadict(self, data, files, name):
        json = data.copy()
        if json.has_key('json_key_%s[]' % name) and \
                json.has_key('json_value_%s[]' % name):
            keys = json.getlist("json_key_%s[]" % name)
            values = json.getlist("json_value_%s[]" % name)
            jsonDict = {}
            for (key, value) in zip(keys, values):
                if key:
                    jsonDict[key] = value
            return jsonDict
