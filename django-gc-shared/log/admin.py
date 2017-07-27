# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from project.utils import show_differences
from log.models import Logger

from requisits.models import UserRequisit
from shared.admin import with_link
from shared.utils import get_admin_url, descr



class LoggerAdmin(admin.ModelAdmin):

    date_hierarchy = "at"
    list_display = ('id', 'user_with_link', 'at', 'event', 'ip')
    search_fields = ('user__pk', 'user__email', 'ip',)
    raw_id_fields = ['user']
    list_filter = ("event",)
    fields = ('user_with_link', 'event', 'object_with_link', 'at', 'ip', 'json_as_table')
    readonly_fields = ['event', 'ip', 'object_with_link', 'at', 'user_with_link', 'json_as_table']

    user_with_link = with_link("user", name=_("User"))
    object_with_link = with_link("content_object", name=_("Changing object"))

    @descr(_("Information"))
    def json_as_table(self, object):

        if not object.params:
            return "&mdash;"

        params = dict(object.params)
        fields = OrderedDict()

        if "from" in params and "to" in params:
            if "field" in params:
                fields[u"Поле"] = params["field"]
                del params["field"]

            if isinstance(params["from"], basestring) and isinstance(params["from"], basestring):
                diff_before, diff_now = show_differences(unicode(params["from"]), unicode(params["to"]))
            else:
                diff_before, diff_now = params["from"], params["to"]

            fields[u"Значение"] = mark_safe("%(before)s -> %(now)s" % {"now": diff_now, "before": diff_before})

            del params["from"]
            del params["to"]

        replaces = {
            "field": u"Поле",
            "state": u"Область",
            "agent_code": u"Агентский код",
            "currency": u"Валюта",
            "amount": u"Сумма",
            "auto": u"Ручной перевод",
            "email": u"Адрес почты",
            "account_status": u"Статус",
            "equity": u"Эквити",
            "account_minimal_equity": u"Минимальное эквити",
            "alias": u"Название",
            "purse": u"Кошелек",
            "new_requisit_id": u"Новый реквизит",
        }

        for k, v in params.items():

            if k == "new_requisit_id":
                req = UserRequisit.objects.get(id=v)
                v = mark_safe("<a href='%s'>%s</a>" % (get_admin_url(req), req))
            elif isinstance(v, dict):
                if k in ["state", "city", "country"]:
                    v = "%s -> %s" % (v["from"] or "None", v["to"] or "None")
                else:
                    diff_now, diff_before = show_differences(v["to"], v["from"])
                    v = mark_safe("%(before)s -> %(now)s" % {"now": diff_now, "before": diff_before})

            fields[replaces.get(k, k)] = v

        return render_to_string("log/json_as_table.html", {"fields": fields})


admin.site.register(Logger, LoggerAdmin)
