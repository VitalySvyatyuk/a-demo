# -*- coding: utf-8 -*-

import os
from urlparse import urlparse

from django.contrib.staticfiles.templatetags.staticfiles import do_static
from django.core.urlresolvers import resolve, Resolver404
from django.db.models import Q
from django.forms import ChoiceField, FileField, CheckboxInput, Select
from django.template import Library, Node, Variable, VariableDoesNotExist, TemplateSyntaxError
from django.template.defaulttags import url
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from uptrader_cms.models import LegalDocument
from treemenus.models import MenuItem
from project.agreements import get_agreements
from shared.utils import get_admin_url
from shared.utils import sanitize_html

register = Library()

register.filter("sanitize", stringfilter(sanitize_html))


class VarNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = Variable(value)

    def get_context(self, top_context):
        for context in top_context.dicts:
            if self.name in context:
                return context
        return top_context

    def render(self, context):
        try:
            value = self.value.resolve(context)
            self.get_context(context)[self.name] = value
        except VariableDoesNotExist:
            self.get_context(context)[self.name] = ""

        return ""


@register.tag
def var(parser, token):
    """
    Simple template tag for creating new context variables from inside
    the template (might not be a good thing :/).

    Example:
      {% var somevar = "somevalue" %}
      {{ somevar } ==> somevalue

    © Pinax
    """
    bits = token.split_contents()

    if len(bits) != 4 or bits[2] != "=":
        raise TemplateSyntaxError(
            "%r expected format is 'foo = bar'." % bits[0])
    return VarNode(bits[1], bits[3])


@register.filter
def field_value(field):
    """
    Returns the value for this BoundField, as rendered in widgets.
    """
    if field.form.is_bound:
        if isinstance(field.field, FileField) and field.data is None:
            val = field.form.initial.get(field.name, field.field.initial)
        else:
            val = field.data
    else:
        val = field.form.initial.get(field.name, field.field.initial)
        if callable(val):
            val = val()

    if val is None:
        val = ""

    return val


@register.filter
def display_value(field):
    """
    Returns the displayed value for this BoundField, as rendered in widgets.
    """
    value = field_value(field)

    if isinstance(field.field, ChoiceField):
        return dict((unicode(k), v)
                    for k, v in field.field.choices).get(unicode(value))
    else:
        return value


@register.simple_tag
def contact(url, title, image=None):
    """Simple tag, rendering a contact button with a given url and title.

    Optionaly an image name can be provided, which should be a file in
    MEDIA_URL/images/contact/, otherwise it's parsed from a give url.
    """
    # Parsing out 2nd level domain name from a given url.
    # Example: 'http://gcanalyst.livejournal.com' --> 'livejournal'
    image = image or urlparse(url).netloc.split(".")[-2]
    return mark_safe("""
        <a href="%(url)s" title="%(title)s" class="contact %(image)s">
        </a>""") % {
        "image": image,
        "title": title,
        "url": url
    }


@register.simple_tag
def morelink(url, title, color, attrs="", additional_style=""):
    return mark_safe("""
        <a class="newmorelink %(color)s" style="cursor: hand; %(additional_style)s" href="%(url)s" %(attr)s>
           <em></em>
           <span>%(title)s</span>
           <b></b>
        </a>
        """) % {
        "color": color,
        "title": title,
        "url": url,
        "attr": attrs,
        "additional_style": additional_style
    }


@register.simple_tag
def gcbutton(type, title, color, attrs=""):
    return mark_safe("""
           <input type="%(type)s" class="button %(color)s" value="%(title)s" %(attrs)s/>
        """) % {
        "color": color,
        "title": title,
        "type": type,
        "attrs": attrs
    }

@register.filter
def divide(value, arg):
    try:
        return round(float(value / arg), 4)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter(name='is_checkbox')
def is_checkbox(value):
    field = getattr(value, "field", None)
    if field:
        return isinstance(field.widget, CheckboxInput)
    return isinstance(value, CheckboxInput)


@register.filter(name='is_select')
def is_select(value):
    field = getattr(value, "field", None)
    if field:
        return isinstance(field.widget, Select)
    return isinstance(value, Select)


@register.filter
def add_class(value, css_class):
    """
    Add class to form elements and etc.
    """

    import re
    class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')

    string = unicode(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class,
                                                    css_class, css_class), match.group(1))
        print match.group(1)
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class,
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value


# @register.simple_tag(takes_context=True)
# def pay_or_watch(context, color):
#     # парсим адрес страницы, для которой делаем тэг
#     # путь выглядит примерно так: /education/remote/mt4_education/recorded/description/
#     # тогда 3я, 4я, 5я часть пути это тип образования (remote), слаг(mt4_education) и
#     # тип семинара (recorded)
#     tokens = context["request"].path.rsplit("/")
#     education_type, slug, tutorial_type = tokens[2:5]
#
#     kwargs = {
#         "slug": slug,
#     }
#     if education_type == "remote":
#         tutorial = RemoteTutorial
#         registration = RemoteTutorialTypeRegistration
#         kwargs["tutorial_type"] = tutorial_type
#     elif education_type == "live":
#         tutorial = LiveTutorial
#         registration = LiveTutorialTypeRegistration
#
#     tutorial = tutorial.objects.get(**kwargs)
#
#     d = {
#         "register": (tutorial.form_link(), u"Зарегистрироваться на семинар"),
#         "pay": (reverse_with_my("education_user_registrations") + "?highlight=%s", u"Оплатить семинар"),
#         "watch": (reverse_with_my("education_user_registrations") + "?highlight=%s", u"Смотреть семинар"),
#     }
#
#     if context["request"].user.is_authenticated():
#         regs = registration.objects.filter(user=context["request"].user, tutorial=tutorial)
#         if len(regs) > 0:
#             if regs[0].is_paid:
#                 url, label = d["watch"]
#             else:
#                 url, label = d["pay"]
#             url %= regs[0].pk
#         else:
#             url, label = d["register"]
#     else:
#         url, label = d["register"]
#     return morelink(url, label, color)


# class My(Node):
#     def __init__(self, my, node):
#         self.my = my
#         self.node = node
#
#     def render(self, context):
#         link = self.node.render(context)
#         handler = set_prefix if self.my else chop_prefix
#         return handler("my", link)


# @register.tag
# def my(parser, token):
#     node = url(parser, token)
#
#     # первый параметр - отвечает за то, добавлять ли в начало /my/ или нет
#     # в данном случае - да
#     return My(True, node)
#
#
# @register.tag
# def not_my(parser, token):
#     node = url(parser, token)
#
#     # первый параметр - отвечает за то, добавлять ли в начало /my/ или нет
#     # в данном случае - нет
#     return My(False, node)


@register.simple_tag
def string_format_dict(format_string, **kwargs):
    return format_string % kwargs


@register.filter
def interpolate(value, arg):
    """
    Interpolates value with argument
    """

    try:
        return mark_safe(value % arg)
    except:
        return ''


class AbsoluteUrl(Node):
    def __init__(self, node):
        self.node = node

    def render(self, context):
        from django.conf import settings
        if ("%s" % (self.node.view_name.var)).startswith("/"):
            return "https://%s%s" % (settings.SITE_NAME, self.node.view_name.var)

        link = self.node.render(context)
        if "request" in context:
            return context["request"].build_absolute_uri(link)
        else:
            return 'https://' + settings.SITE_NAME + link


@register.tag
def absolute_url(parser, token):
    node = url(parser, token)
    return AbsoluteUrl(node)


class AbsoluteStatic(Node):
    def __init__(self, node):
        self.node = node

    def render(self, context):
        link = self.node.render(context)
        if "request" in context:
            return context["request"].build_absolute_uri(link)
        else:
            if link and link.startswith("https:"):
                return link
            else:
                from settings import SITE_NAME

                return 'https://' + SITE_NAME + link


@register.tag
def absolute_static(parser, token):
    node = do_static(parser, token)
    return AbsoluteStatic(node)


@register.simple_tag(takes_context=True)
def absolute_link(context, link):
    if "request" in context:
        return context["request"].build_absolute_uri(link)
    return ""


@register.simple_tag
def admin_url(request):
    return "<a href='%s' style='text-decoration: inherit; color: rgb(91, 128, 178);'>%s</a>" % (
        get_admin_url(request), request.purse
    )


@register.assignment_tag
def legal_documents(lang):
    return LegalDocument.objects.filter(languages__contains=[lang])


@register.filter
def edit(value):
    return mark_safe("<a href='%s'>Edit</a>" % get_admin_url(value))


@register.filter
def as_timestamp(value):
    """
    Returns date as unix timestamp
    Requires datetime object as value
    """
    import time
    return int(time.mktime(value.timetuple()))


@register.filter
def agreement_url(name):
    if get_language() == "ru":
        if not name.endswith("_ru"):
            name += "_ru"
    agreement_info = get_agreements()[name]
    agreement = agreement_info.get(get_language()) or agreement_info.get("default")
    return agreement


@register.filter
def agreement_label(name):
    agreement_info = get_agreements()[name]
    return agreement_info["label"]


@register.filter
def is_alpha(value):
    return unicode(value).isalpha()


@register.filter
def order_items(items):
    from operator import itemgetter
    return sorted(items, key=itemgetter(0))


@register.filter
def human_join(values, sep=", "):
    out = unicode(sep.join(values[:-1]))
    if out:
        out += ' %s ' % unicode(_("and"))

    if values:
        out += values[-1]

    return out


@register.filter
def substitute(path, languages):
    lang = get_language()
    if lang in languages:
        name, ext = os.path.splitext(path)
        return "%s-%s%s" % (name, lang, ext)
    return path


@register.simple_tag
def versioned(path):
    from django.templatetags.static import static
    static_path = static(path)
    try:
        real_path = os.path.join(settings.STATIC_ROOT, path)
        return "%s?t=%s" % (static_path, os.path.getmtime(real_path))
    except:
        return static_path


@register.inclusion_tag('marketing_site/components/login_popup.jade', takes_context=True)
def auth_popup(context, request):
    from registration.forms import ProfileRegistrationForm
    context["registration_form"] = ProfileRegistrationForm(request=request)
    return context


def get_item(path, menu):
    query = Q(regex_url__iregex=path + "$") | Q(url=path)
    try:
        named_url = resolve(path)
    except Resolver404:
        pass
    else:
        query |= Q(named_url=named_url.url_name)

    lang = get_language()
    item = MenuItem.objects.filter(query, menu__name=menu).\
        exclude(**{"caption_%s" % str(lang).replace('-', '_'): ""}).\
        select_related('parent')
    if item:
        item = item[0]
    return item


@register.inclusion_tag("marketing_site/components/breadcrumbs.jade", takes_context=True)
def breadcrumbs(context, menu="public_menu", name=None, root=None, additional_items=None):
    """
    :param name:
     Name of current item
    :param root:
     Path to use instead of request.path
    :param additional_items:
     List of dicts:
     [
          {
               "caption": "My additional item caption",
               "get_url": "/my/additional/item/url/",
          },
     ]
    """

    path = root or context["request"].path
    if path == "/":
        return {}
    item = get_item(path, menu)
    items = additional_items or []

    if not item:
        item = get_item("/".join(path.rstrip("/").split("/")[:-1]) + "/", menu=menu)  # parent item
        if not item:
            item = get_item("/".join(path.rstrip("/").split("/")[:-2]) + "/", menu=menu)  # parent of parent item
        items.append(item)
    else:
        name = item.caption

    if item:
        while item.parent:
            items.append(item.parent)
            item = item.parent

    return {
        "items": reversed(items),
        "current_item_name": name
    }


@register.simple_tag(takes_context=True)
def mixquery(context, **kwargs):
    from urllib import urlencode
    params = dict(context.request.GET)
    for name in kwargs:
        if name in params:
            del params[name]
    for name, val in kwargs.items():
        if val:
            params.setdefault(name, []).append(val)
    return urlencode(params, doseq=True)


# This function was extracted from linaro-django-pagination module
def get_pagination_links(paginator, current_page, window=4, margin=4):
    page_range = paginator.page_range
    # Calculate the record range in the current page for display.

    # figure window
    window_start = current_page - window - 1
    window_end = current_page + window

    # solve if window exceeded page range
    if window_start < 0:
        window_end -= window_start
        window_start = 0
    if window_end > paginator.num_pages:
        window_start -= window_end - paginator.num_pages
        window_end = paginator.num_pages
    pages = page_range[window_start:window_end]

    # figure margin and add elipses
    if margin > 0:
        # figure margin
        tmp_pages = set(pages)
        tmp_pages = tmp_pages.union(page_range[:margin])
        tmp_pages = tmp_pages.union(page_range[-margin:])
        tmp_pages = list(tmp_pages)
        tmp_pages.sort()
        pages = []
        pages.append(tmp_pages[0])
        for i in range(1, len(tmp_pages)):
            # figure gap size => add elipses or fill in gap
            gap = tmp_pages[i] - tmp_pages[i - 1]
            if gap >= 3:
                pages.append(None)
            elif gap == 2:
                pages.append(tmp_pages[i] - 1)
            pages.append(tmp_pages[i])
    else:
        if pages[0] != 1:
            pages.insert(0, None)
        if pages[-1] != paginator.num_pages:
            pages.append(None)

    return pages


@register.assignment_tag
def pagination_links(*args, **kwargs):
    return get_pagination_links(*args, **kwargs)
