# -*- coding: utf-8 -*-

import re

from django.contrib import admin
from django.utils.safestring import mark_safe

from project.utils import show_differences
from geobase.utils import get_country
from shared.admin import BaseAdmin, with_link
from requisits.models import UserRequisit
from payments.filterspecs import PaymentSystemFilter
from log.models import Logger, Events
from shared.utils import descr


class UserRequisitAdmin(BaseAdmin):

    list_display = ("purse", "user_with_link", "payment_system", "is_valid", "is_deleted", "creation_ts", "previous_with_link")
    list_filter = (('payment_system', PaymentSystemFilter), "is_deleted", "creation_ts")
    search_fields = ["user__username", "purse"]

    readonly_fields = ("user_with_link", "purse", "payment_system",
                       "previous_with_link", "creation_ts", "get_params")
    fieldsets = (
        (None, {
            "fields": ("user_with_link", "alias", ("purse", "payment_system", "previous_with_link"),
                       "creation_ts", "is_valid", "comment", "get_params", "is_deleted")
        }),
    )

    user_with_link = with_link("user")
    previous_with_link = with_link("previous", "previous version of requisit")

    @descr(u"Кошелек")
    def maybe_purse(self, obj):
        if not obj.purse or re.match(r"[a-z0-9]{32}", obj.purse):
            return mark_safe(u"&mdash;")
        else:
            return obj.purse

    def save_model(self, request, obj, form, change):
        obj.save()
        if 'is_valid' in obj.changes:
            Logger(
                user=request.user, content_object=obj, ip=request.META["REMOTE_ADDR"],
                event=Events.REQUISIT_VALIDATION_UPDATE,
                params={'is_valid': obj.is_valid}).save()

    def get_params(self, obj):
        try:
            if obj.get_params():
                res = ["<table>"]
                if obj.previous:
                    res.append(u"<thead><tr><th>Название</th>"
                               u"<th>В этом реквизите</th>"
                               u"<th class='prev'>Ранее</th></tr>")

                    for (k, v), (k_prev, v_prev) in zip(obj.get_params().iteritems(),
                                                        obj.previous.get_params().iteritems()):
                        key = v.key
                        v = v.value
                        v_prev = v_prev.value

                        if key in ["country", "correspondent"]:
                            # обычно для стран и банка-корреспондента бессмысленно считать
                            # изменения посимвольно, так что выделяем сразу все слово
                            if v != v_prev:
                                v = u"<span class='replace'>%s</span>" % v
                                v_prev = u"<span class='replace'>%s</span>" % v_prev
                        else:
                            v, v_prev = show_differences(v, v_prev)

                        res.append(u"<tr><td>%s</td><td>%s</td><td class='prev'>%s</td></tr>" % (unicode(k), v, v_prev))
                else:
                    res.append(u"<thead><tr><th>Параметр</th><th>В этом реквизите</th></tr>")
                    for k, v in obj.get_params().iteritems():
                        if v.key == "country":
                            v = get_country(v.value)
                        else:
                            v = v.value
                        res.append(u"<tr><td>%s</td><td>%s</td></tr>" % (unicode(k), v))
                value = "".join(res + [u"</table>"])
            else:
                value = u"&mdash;"

            return mark_safe(value)
        except Exception as e:
            pass


admin.site.register(UserRequisit, UserRequisitAdmin)
