# -*- coding: utf-8 -*-

import types
import json

from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.urlresolvers import NoReverseMatch
from django.http import HttpResponseForbidden

from shared.models import VideoStat
from shared.utils import get_admin_url, descr
import settings


class VideoStatAdmin(admin.ModelAdmin):
    readonly_fields = ('user', 'videofile', 'timestamp')
    list_display = ('user', 'videofile', 'timestamp')
    list_filter = ('videofile',)
    search_fields = ('user__username', 'user__email', 'videofile')


class BaseAdmin(admin.ModelAdmin):
    actions_on_bottom = False
    actions_on_top = True
    list_per_page = 25
    list_select_related = True
    change_list_template = "admin/change_list_hidable.html"


class ViewLoggingAdmin(admin.ModelAdmin):
    @staticmethod
    def get_user_field(obj):
        return obj.user


class EasyCommentCreatorAdminMixin(object):
    """
    Allows adding EasyComment functionality in admin classes.
    Usage:

    step 1: create in your admin class a new class called EasyComment with special
    attributes, e.g.

    class EasyComment:
        easy_comment_field = "some_field" # EasyComment functionality will be
                    # linked to onclick of this field in list_display.
        typical_private_comments = ["comment1", "comment2"]
        typical_public_comments = ["comment1", "comment2"]
        private_comments_field = "field_name"
        public_comments_field = "field_name"

    You are not forced to specify both private and public comment fields, only one
    can be used.

    step 2: if you have changelist_view function overridden in your class, you must
      add 'EasyAdmin': EasyAdmin to its extra_context section. If you don't have changelist_view,
      you needn't worry: everything will be done automatically.
    """

    def __new__(cls, *args, **kwargs):
        model = args[0]  # see ModelAdmin.__init__

        def curry_list_disp_func(attr_name):
            def list_disp_func(self, obj):
                fld = None
                for field in obj._meta.fields:
                    if field.name == attr_name:
                        fld = field
                        break
                field_text = admin.util.display_for_field(getattr(obj, attr_name), fld)
                return "<span id='ec-%i' class='easy-comment'>%s</span>" % (obj.pk, field_text)

            list_disp_func.allow_tags = True
            list_disp_func.admin_order_field = attr_name
            list_disp_func.short_description = model._meta.get_field(attr_name).verbose_name
            return list_disp_func

        obj = super(EasyCommentCreatorAdminMixin, cls).__new__(cls)

        if hasattr(obj, "EasyComment"):
            comment_field = obj.EasyComment.__dict__.get("easy_comment_field")
            list_display = obj.list_display
            # prepare list_display
            if comment_field and (comment_field in list_display):
                list_display = list(list_display)
                disp_func_name = comment_field + "_prepared_for_comments"
                list_display[list_display.index(comment_field)] = disp_func_name
                obj.list_display = tuple(list_display)
                curried_function = curry_list_disp_func(comment_field)
                curried_function.__name__ = comment_field
                setattr(obj, disp_func_name,
                        types.MethodType(curried_function, obj, obj.__class__))

            # set template
            if obj.change_list_template:
                obj.EasyComment.parent_template = obj.change_list_template
            else:
                obj.EasyComment.parent_template = "admin/change_list.html"
            obj.change_list_template = "admin/change_list_easy_comment.html"

            # add info about model
            obj.EasyComment.module = model.__module__
            obj.EasyComment.model = model._meta.object_name

            # jsonize typical comments
            obj.EasyComment.typical_comments_json = json.dumps({
                "private": obj.EasyComment.typical_private_comments
                if hasattr(obj.EasyComment, "typical_private_comments") else "",
                "public": obj.EasyComment.typical_public_comments
                if hasattr(obj.EasyComment, "typical_public_comments") else "",
            })

            # set Media.js
            if not hasattr(obj, "Media"):
                class Media(object):
                    pass

                obj.Media = Media
            if not hasattr(obj.Media, "js"):
                obj.Media.js = []
            obj.Media.js.append(settings.STATIC_URL + "js/easy-comment.js")

            # set extra_context if changelist_view is not overridden
            if obj.changelist_view.im_func == admin.ModelAdmin.changelist_view.im_func:
                def changelist_view(self, request, extra_context=None):
                    extra_context = {'EasyComment': obj.EasyComment}
                    return super(obj.__class__, self).changelist_view(request, extra_context)

                setattr(obj, 'changelist_view',
                        types.MethodType(changelist_view, obj, obj.__class__))

        return obj


def urlize(obj, text=None):
    """
    Returns an edit link for a given object, link text can be provided
    optionally, else object.__unicode__ is used.
    """
    text = text or unicode(obj)
    try:
        link = get_admin_url(obj)
    except (AttributeError, NoReverseMatch):
        return text
    else:
        return u"<a href=\"%s\">%s</a>" % (link, text)


def with_link(field, name=None):
    name = name or field.replace("_", " ")

    @descr(name, admin_order_field=field)
    def inner(self, obj):
        f = getattr(obj, field)
        if f is None:
            return "&mdash;"
        return urlize(f)

    return inner


# Ease attachment of short_description attribute, that is used a lot by django admin
def short_descr(text):
    def inner(f):
        f.short_description = text
        return f
    return inner


admin.site.register(VideoStat, VideoStatAdmin)
