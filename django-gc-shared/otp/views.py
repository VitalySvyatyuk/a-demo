# -*- coding: utf-8 -*-
import StringIO
import hashlib
import json
import time
from datetime import datetime, timedelta
from functools import wraps

import qrcode
from annoying.decorators import ajax_request
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import mail_admins
from django.http import Http404
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from log.models import Logger, Events
from otp.forms import OTPForm, PhoneForm, SMSForm
from otp.models import SMSDevice, OTPDevice, random_base32, VoiceDevice
from project.utils import maybe_ajax
from shared.utils import get_admin_url


def make_hash(fields, target=None, secret=None):

    secret_map = {
        "main": "|#^4e12)fejh478oh3*i(vub%r%q&5qjvj#",
        "preview": "7fwefwfqwfDFAFfdZG8PUOxsrC"
    }

    return hashlib.sha1(
        json.dumps(sorted(fields.items()))
        +
        (secret or secret_map[target or "main"])
    ).hexdigest()


def get_extra_fields(request, **extra):
    fields_not_to_hash = ["hash", "otp-token", "next", "csrfmiddlewaretoken", "target"]
    extra_fields = {k: v
                    for k, v in request.POST.items() + extra.items()
                    if k not in fields_not_to_hash}

    return extra_fields


# should return None or context
def sms_check(request, user):

    if user.profile.has_otp_devices:
        target = "main"
    else:
        target = request.POST.get("target", "main")
    extra_fields = get_extra_fields(request)

    # if there is no 'hash' then it's first we hit this code
    if "hash" in request.POST:

        form = SMSForm(data=request.POST, request=request, user=user, prefix="otp")

        fields_hash = request.POST["preview_hash" if target == "preview" else "hash"]

        timestamp = datetime.fromtimestamp(float(request.POST["timestamp"]))

        if datetime.now()-timestamp > timedelta(minutes=30):
            return {"session_expired": True}

        if form.is_valid():

            if target == "preview":
                phone_form = PhoneForm(data=request.POST)
                phone_form.is_valid()

                extra_fields = {
                    "phone_mobile": phone_form.cleaned_data["phone_mobile"]
                }

            extra_fields["token"] = form.cleaned_data["token"]
            new_hash = make_hash(extra_fields, target=target)

            if new_hash == fields_hash:
                return None

            extra_fields = get_extra_fields(request)

        step2 = True
        form.errors["token"] = [_("Wrong token")]
    else:
        form = SMSForm(request=request, user=user, prefix="otp")

        extra_fields["timestamp"] = str(int(time.time()))

        fields_hash = make_hash(extra_fields, target=target)
        step2 = False

    # нельзя показывать пользователю токен :)
    extra_fields.pop("token", None)
    extra_fields["hash"] = fields_hash

    form.extra_fields = extra_fields
    form.auth_scheme = "sms"
    form.step2 = step2

    return {"form": form}


def otp_check(request, user):
    scheme = user.profile.auth_scheme
    extra_fields = get_extra_fields(request)

    # if there is no 'hash' then it's first we hit this code
    if "hash" in request.POST:

        form = OTPForm(data=request.POST, request=request, user=user, prefix="otp")

        fields_hash = request.POST["hash"]

        if form.is_valid():
            new_hash = make_hash(extra_fields)
            if new_hash == fields_hash:
                return None

            form.errors["token"] = [_("Wrong token")]
    else:
        form = OTPForm(request=request, user=user, prefix="otp")
        fields_hash = make_hash(extra_fields)

    # нельзя показывать пользователю токен :)
    extra_fields["hash"] = fields_hash

    form.extra_fields = extra_fields
    form.auth_scheme = scheme

    return {"form": form}


# не является самостоятельным view, вызывается только из других представлений
# используется при входе, так что там request.user == AnonymousUser и поэтому
# нужно явное указание юзера вторым аргументом
def security_check(request, user, return_form=False):
    scheme = user.profile.auth_scheme
    cache_key = "otp_check_%s" % user.pk

    # нет OTP-привязок
    if not user.profile.has_otp_devices:
        return None

    check_map = {
        "sms": sms_check,
        "otp": otp_check,
    }

    # if there is no 'hash' then it's first we hit this code
    if "hash" in request.POST:

        # даем 5 попыток на логин, иначе выкидываем из ЛК
        attempts_to_login = cache.get(cache_key, 1)
        if attempts_to_login == 5:
            cache.delete(cache_key)
            logout(request)
            return redirect("/my/")

        cache.set(cache_key, attempts_to_login+1)

    check = check_map[scheme]
    res = check(request, user)

    if request.user.is_authenticated():
        kwargs = {
            "user": request.user,
            "content_object": request.user,
        }
    else:
        try:
            maybe_user = User.objects.get(email__icontains=request.POST["auth-email"])
            kwargs = {
                "user": maybe_user,
                "content_object": maybe_user,
            }
        except User.DoesNotExist, User.MultipleObjectsReturned:
            kwargs = {}

    if res is None:
        Logger(event=Events.OTP_OK, ip=request.META["REMOTE_ADDR"], params={"path": request.path}, **kwargs).save()
        cache.delete(cache_key)
        return res
    elif "hash" in request.POST:
        Logger(event=Events.OTP_FAIL, ip=request.META["REMOTE_ADDR"], params={"path": request.path}, **kwargs).save()

    if return_form:
        return render_to_string("otp/includes/otp_form.html", RequestContext(request, res))

    return render_to_response("otp/otp_check.html", RequestContext(request, res))


def convert_to_base64(img):
    stream = StringIO.StringIO()
    img.save(stream, "png")
    img_base64 = stream.getvalue().encode("base64")
    return img_base64


@login_required
@ajax_request
def refresh_qr_code(request):
    device = OTPDevice(key=random_base32())
    uri = device.uri("%s@%s" % (request.user.username, settings.ROOT_HOSTNAME))

    return {
        "qr_code": convert_to_base64(qrcode.make(uri)),
        "secret": device.key,
    }


@login_required
@require_POST
@ajax_request
def check_sync(request):
    secret = request.POST["secret"]
    value = request.POST["value"]

    device = OTPDevice(key=secret)

    return {
        "result": device.verify_token(value, request),
    }


@login_required
@ensure_csrf_cookie
@maybe_ajax('otp/security.html')
def security(request):
    if request.user.profile.has_otp_devices:
        raise Http404()

    new_device = OTPDevice(key=random_base32())
    new_secret = new_device.key
    uri_domain = u"%(name)s@%(debug)s%(domain)s" % {
        "debug": "debug." if settings.DEBUG else "",
        "name": request.user.username,
        "domain": settings.ROOT_HOSTNAME,
    }
    uri = new_device.uri(uri_domain)
    old_hash = ""

    next = request.GET.get("next") or request.POST.get("next") or request.path

    if request.method == "POST":

        auth_type = request.POST.get("auth_type")
        model, check_key = {
            "sms": (SMSDevice, "sms_check"),
            "otp": (OTPDevice, "otp_check"),
        }[auth_type]

        if auth_type in ["sms", "voice"]:
            phone_form = PhoneForm(data=request.POST)
            phone_form.step2 = True

            if not phone_form.is_valid():
                return {
                    "qr_code": convert_to_base64(qrcode.make(uri)),
                    "secret": new_secret,
                    "devices": request.user.profile.otp_devices,
                    "phone_form": phone_form,
                }
        else:
            phone_form = PhoneForm(number=request.user.profile.phone_mobile)
            phone_form.step2 = False

        device = model(user=request.user, name=auth_type.upper())
        if auth_type == "otp":
            secret = request.POST["device_secret"]
            device.key = secret

        if (check_key in request.POST
            and device.verify_token(request.POST[check_key], request)):

            result = security_check(request, request.user)
            if result:
                return result

            if auth_type == "sms":
                device.phone_number = phone_form.cleaned_data["phone_mobile"]

            # только один девайс на юзера
            request.user.profile.otp_devices.update(is_deleted=True)

            if auth_type == "sms":
                profile = request.user.profile
                profile.make_valid("phone_mobile")
                phone_number = phone_form.cleaned_data["phone_mobile"]
                phone_number_profile = profile.phone_mobile if profile.phone_mobile else ""

                profile_phone_clean = "".join(x for x in phone_number_profile if x in "1234567890+")
                phone_number_clean = "".join(x for x in phone_number if x in "1234567890+")

                if profile_phone_clean != phone_number_clean:
                    mail_admins(
                        u"Номер в СМС-привязке не совпадает с номером в профиле",
                        u"Клиент %(user)s (%(user_admin_url)s) создал СМС-привязку, "
                        u"номер которой не совпадает с номером телефона в профиле\n"
                        u"%(profile_phone)s - в профиле\n"
                        u"%(binding_phone)s - в привязке\n"
                        u"Телефон в профиле был обновлен на телефон в привязке" % {
                            "user": request.user,
                            "user_admin_url": request.build_absolute_uri(get_admin_url(request.user)),
                            "profile_phone": profile_phone_clean,
                            "binding_phone": phone_number_clean
                        }
                    )

                    profile.phone_mobile = phone_number
                    profile.save()

                    Logger(event=Events.PROFILE_CHANGED, user=request.user,
                           ip=request.META["REMOTE_ADDR"], content_object=profile,
                           params={'phone_mobile': {"from": profile.phone_mobile, "to": phone_number}}).save()

            device.save()

            Logger(event=Events.OTP_BINDING_CREATED, user=request.user,
                   ip=request.META["REMOTE_ADDR"], content_object=device).save()

            request.user.profile.auth_scheme = auth_type
            request.user.profile.lost_otp = False
            request.user.profile.save()

            if request.is_ajax():
                return {
                    "ok": True,
                    "redirect": next,
                }

            messages.success(request, _("Device %s has been saved") % device.name)

            return redirect(next)
        else:
            if request.is_ajax():
                return {
                    "nok": True,
                    "errors": {
                        (auth_type + "_check"): [unicode(_("Wrong code"))]
                    }
                }
            messages.error(request, _("Wrong code"))
            old_hash = request.POST.get("preview_hash", "")
    else:
        phone_form = PhoneForm(number=request.user.profile.phone_mobile)

    context = {
        "qr_code": convert_to_base64(qrcode.make(uri)),
        "secret": new_secret,
        "devices": request.user.profile.otp_devices,
        "phone_form": phone_form,
        "auth_type": request.REQUEST.get("auth_type", "sms"),
        "preview_hash": old_hash,
        "next": next
    }

    if request.is_ajax():
        return render_to_response("reveal_forms/create_otp.html", RequestContext(request, context))

    return context


@login_required
def confirm(request):

    if request.user.profile.auth_scheme == "sms":
        return render_to_response("otp/confirmation.html",
                                  RequestContext(request, {"have_sms_binding": True}))

    result = sms_check(request, request.user)

    if result:
        return render_to_response("otp/confirmation.html",
                                  RequestContext(request, result))

    phone_raw = request.POST["phone_mobile_0"] + request.POST["phone_mobile_1"]
    phone = "".join(c for c in phone_raw if c in "1234567890+")
    profile = request.user.profile

    if profile.phone_mobile != phone:
        Logger(event=Events.PROFILE_CHANGED, user=request.user, ip=request.META["REMOTE_ADDR"],
               content_object=profile, params={'phone_mobile': {"from": profile.phone_mobile, "to": phone}}).save()

        profile.phone_mobile = phone
        profile.save()

    validation, created = request.user.validations.get_or_create(key="phone_mobile")
    old_status = validation.is_valid
    validation.is_valid = True
    validation.save()

    Logger(user=request.user, content_object=profile,
           ip=request.META["REMOTE_ADDR"], event=Events.PHONE_VALIDATION_BY_USER,
           params={"field": "phone_mobile", "from": old_status, "to": True}).save()

    return redirect(request.GET.get("next", "profiles_edit_profile"))


def retries_counter(key=None):

    key = key or "otp"

    def outer(f):
        @wraps(f)
        def inner(request, *args, **kwargs):
            target = request.POST.get("target", "main")

            cache_key = "%s_count_user_%s_%s" % (key, request.user.pk, target)
            cached = cache.get(cache_key)

            retries = None
            ts = None
            TIMEOUT = 5
            RETRIES = 105

            if cached:
                ts = cached["first_try_at"]
                retries = cached["retries"]
                # 5 попыток за 5 минут
                if retries > RETRIES and datetime.now()-ts < timedelta(minutes=TIMEOUT):
                    return {"res": "nok", "too_much_retries": True}

            cache.set(cache_key, {
                "retries": retries+1 if retries else 1,
                "first_try_at": ts if ts else datetime.now()
            }, 30*TIMEOUT)  # 5 minutes

            return f(request, *args, **kwargs)
        return inner
    return outer


@login_required
@require_POST
@ajax_request
@retries_counter("sms")
def send_sms(request):

    token = SMSDevice.generate_token()
    if request.user.profile.has_otp_devices:
        target = "main"
    else:
        target = request.POST["target"]

    if target == "main":
        phone_number = request.user.profile.otp_device.phone_number
        extra_fields = get_extra_fields(request, token=token)
    else:
        form = PhoneForm(data=request.POST)

        if not form.is_valid():
            return {
                "nok": True,
                "bad_phone": True
            }

        phone_number = form.cleaned_data["phone_mobile"]

        extra_fields = {
            "token": token,
            "phone_mobile": phone_number
        }

    fields_hash = make_hash(extra_fields, target=target)
    phone_number = "".join([c for c in phone_number if c in "+1234567890"])

    if settings.DEBUG:
        print 'SMS Token: ', token

    if not settings.DEBUG and SMSDevice.send_sms(phone_number, token=token) is None:
            return {
                "nok": True,
                "bad_phone": True
            }

    return {
        "ok": "True",
        "hash": fields_hash
    }


@login_required
@require_POST
@ajax_request
@retries_counter("call")
def make_call(request):

    target = request.POST["target"]
    token = VoiceDevice.generate_token()

    if target == "main":
        phone_number = request.user.profile.phone_mobile
        extra_fields = get_extra_fields(request, token=token)
    else:
        form = PhoneForm(data=request.POST)

        if not form.is_valid():
            return {
                "nok": True,
                "bad_phone": True
            }

        phone_number = form.cleaned_data["phone_mobile"]

        extra_fields = {
            "token": token,
            "phone_mobile": phone_number
        }

    fields_hash = make_hash(extra_fields, target=target)
    phone_number = "".join([c for c in phone_number if c in "+1234567890"])

    VoiceDevice.deliver_token(request=request, phone=phone_number, token=token)

    return {
        "ok": "True",
        "hash": fields_hash
    }


@ajax_request
def check_sms(request):
    token = request.GET.get("sms_check", "")
    form = PhoneForm(data=request.GET)

    if not form.is_valid():
        return {"nok": True}

    phone_number = form.cleaned_data["phone_mobile"]
    old_hash = request.GET.get("preview_hash", "")

    extra_fields = {
        "token": token,
        "phone_mobile": phone_number
    }

    if make_hash(extra_fields, target="preview") == old_hash:
        return {"ok": True}
    return {"nok": True}
