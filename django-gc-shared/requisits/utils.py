# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from log.models import Logger, Events
from payments.utils import load_payment_system
from shared.decorators import as_json


def update_requisit(request, create=False, commit=True):

    payment_system = load_payment_system(request.POST["ps"])

    if create:
        form = payment_system.WithdrawForm(request.POST, request=request)

        if form.is_valid():
            requisits = request.user.requisits.filter(purse=form.cleaned_data[form.get_purse_field_name()],
                                                      is_deleted=False)

            if requisits:
                return True, requisits[0]

            req = form.save(commit=commit)
            req.user = request.user
            req.save()
            Logger(user=request.user, content_object=req, ip=request.META["REMOTE_ADDR"],
                   event=Events.REQUISIT_CREATED).save()
            return True, req
    else:
        if hasattr(payment_system, "LinkForm") and 'requisit' in request.POST:
            requisit = request.user.requisits.filter(pk=request.POST['requisit'])
            if not requisit:
                raise
            requisit = requisit[0]

            form = payment_system.WithdrawForm(request.POST, request=request, instance=requisit)
            if form.is_valid():

                instance = form.save(commit=False)
                changes = dict(instance.changes)
                # если изменили еще что-то кроме названия реквизита,
                # то создаем его копию, но уже с обновленными данными
                if changes:
                    req = request.user.requisits.get(pk=request.POST['requisit'])
                    if not(len(changes) == 1 and "alias" in changes):
                        instance.previous = req
                        instance.alias = request.POST.get("alias", False) or req.alias
                        instance.pk = None
                        instance.is_valid = False

                        req.is_deleted = True

                        if instance.user.profile.auth_scheme and instance.user.date_joined > datetime(2013, 12, 6):
                            instance.is_valid = True

                        req_changes = {change[0]: {"from": unicode(change[1][0]), "to": unicode(change[1][1])}
                                       for change in changes.items()}
                        req_changes["new_requisit_id"] = instance.pk
                        Logger(user=request.user, ip=request.META["REMOTE_ADDR"],
                               event=Events.REQUISIT_CHANGED, content_object=req,
                               params=req_changes).save()

                        return True, instance
                    else:
                        instance.alias = changes["alias"][1]
                if commit:
                    instance.save()
                return True, instance

    return False, form


@login_required
@require_GET
@as_json
def autocomplete_requisit(request):
    qs = request.user.requisits

    term = request.GET.get('term')
    payment_system = request.GET.get('payment_system')

    if term:
        qs = qs.filter(purse__startswith=term)
    if payment_system:
        qs = qs.filter(payment_system=payment_system)

    return tuple(qs.values_list("purse", flat=True)), 200
