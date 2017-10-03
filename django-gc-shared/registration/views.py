# -*- coding: utf-8 -*-

import hashlib
import time
import urlparse
from datetime import datetime, timedelta

from annoying.decorators import render_to
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login, REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.contrib.auth.views import password_reset as django_password_reset
from django.core.cache import cache
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse, Resolver404, resolve
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import is_safe_url
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from social.actions import do_complete
from social.apps.django_app.utils import psa
from social.apps.django_app.views import _do_login

from backends import register_user, phone_based_registration
from forms import ProfileRegistrationForm, PasswordResetByPhoneForm, EmailAuthenticationForm
from log.models import Logger, Events
from otp.models import SMSDevice
from project.utils import maybe_ajax
from registration.models import RegistrationProfile
from registration.signals import user_activated

from logging import getLogger
log = getLogger(__name__)


def get_private_office_from_next(next_url):
    try:
        next_resolved = resolve(next_url)
    except Resolver404:
        pass
    else:
        if next_resolved.url_name == "private_offices":
            return next_resolved.kwargs['slug']
    return ''


@csrf_exempt
@maybe_ajax()
def register(request, extra_context=None, next=None, form_class=ProfileRegistrationForm,
             template='registration/register.html', *args, **kwargs):
    redirect_to = '/account/profile/info'

    social_auth_pipeline = request.session.get('partial_pipeline', {})

    if request.method == 'POST':
        if not request.session.get('registration_page'):
            request.session['registration_page'] = request.META.get('HTTP_REFERER')

        form = form_class(data=request.POST, files=request.FILES, request=request, label_suffix='')
        if form.is_valid():
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = ""
            new_user = register_user(request=request, **form.cleaned_data)

            if phone_based_registration(new_user):
                new_user.last_login = datetime.fromtimestamp(0)
                new_user.save()
                request.session["user_id"] = new_user.pk
                messages.add_message(request, messages.SUCCESS,
                                     "Your password was sent via SMS to your phone number")
            if social_auth_pipeline:
                request.session['partial_pipeline']['user'] = new_user
                social_auth_redirect_url = reverse('social:complete', args=(social_auth_pipeline.get('backend'),))
                if new_user.last_login == datetime.fromtimestamp(0):
                    social_auth_redirect_url += '?next=' + reverse('auth_login')
                else:
                    social_auth_redirect_url += '?next=' + reverse('account_app')
                redirect_to = social_auth_redirect_url
            request.session["new_registration"] = 'true'
            if request.is_ajax():
                response = {
                    "ok": True,
                    "redirect": redirect_to or reverse('mt4_create'),
                }
                if phone_based_registration(new_user):
                    response['simple_redirect'] = redirect_to
                    del response['redirect']
                return response
            return redirect(redirect_to or "mt4_create")
        else:
            if request.is_ajax():
                return {
                    "nok": True,
                    "errors": {k: map(unicode, v) for k, v in form.errors.items()}
                }
    else:
        initial = {'registered_from': get_private_office_from_next(redirect_to)}
        if social_auth_pipeline:
            details = social_auth_pipeline.get('kwargs', {}).get('details', {})
            initial.update(details)
        form = form_class(request=request, label_suffix='',
                          initial=initial)

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    context['next'] = redirect_to

    if request.is_ajax():
        return render_to_response("reveal_forms/registration.html", RequestContext(request,
                                                                                   {
                                                                                       "form": form,
                                                                                       "next": redirect_to,
                                                                                   }))

    return {
        'form': form,
        "next": redirect_to,
        'TEMPLATE': template,
    }


@maybe_ajax("registration/login.html",)
def login(request, next=None, *args, **kwargs):
    """
    Main login view.
    """
    next = request.REQUEST.get('next', next)
    user = None
    user_id = request.session.get("user_id")
    if user_id:
        del request.session["user_id"]  # We probably don't need it for more than one pageload
        if User.objects.filter(pk=user_id).exists():
            user = User.objects.get(pk=user_id)

    if next is None:
        if request.path != reverse('auth_login'):
            next = request.path
        else:
            next = '/account/profile/info'

    if request.method == "POST":
        ip = request.META["REMOTE_ADDR"]

        cache_key = 'login_%s' % ip
        login_try = cache.get(cache_key)

        # Anti-Bruteforce
        if login_try > 19:
            request.method = 'GET'
            messages.error(request, _(u'Your IP address has been blocked due to 20 unsuccessfull logon '
                                      u'attempts. Please wait at least 20 minutes before trying again'))
            cache.set(cache_key, login_try+1, 20*60)
            subject = u'Возможная попытка взлома системы'
            message = u'IP %s пытается войти в систему. Данный IP был заблокирован на ближайшие ' \
                      u'20 минут, вследствие 20 неудачных попыток войти в систему.' % ip
            mail_admins(subject=subject, message=message)

    form = EmailAuthenticationForm(data=request.POST or None, request=request,
                                   prefix="auth", label_suffix='',
                                   initial={
                                       'login_from': get_private_office_from_next(next),
                                       'email_phone': user.profile.phone_mobile if user else None
                                   })

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()

            if user.last_login == datetime.fromtimestamp(0) and not user.profile.has_otp_devices:
                SMSDevice.objects.create(
                    user=user, phone_number=user.profile.phone_mobile
                )
                user.profile.make_valid("phone_mobile")
                user.profile.lost_otp = False
                user.profile.save()

            # if user.profile.ask_on_login:
            #     result = security_check(request, user)
            #     if result:
            #         return result

            django_login(request, user)

            Logger(content_object=request.user, ip=request.META["REMOTE_ADDR"],
                   user=request.user, event=Events.LOGIN_OK).save()

            profile = request.user.profile

            language = request.session.get('django_language', settings.LANGUAGE_CODE)

            if profile.language != language:
                profile.language = language
                profile.save()

            if not form.cleaned_data["remember"]:
                days = 0  # Log the user out after a day.
            else:
                days = settings.LOGIN_FOR

            request.session.set_expiry(60 * 60 * 24 * days)

            if request.user.profile.lost_otp:
                if request.is_ajax():
                    return {
                        "ok": True,
                        "redirect": reverse("otp_security") + "?next=" + next
                    }

            next_url = '{}://{}{}'.format(request.META['wsgi.url_scheme'],
                                          request.get_host(),
                                          request.GET.get("next", "/"))

            request.session['login_ts'] = time.time()
            request.session['xnext'] = '{}://{}{}'.format(request.META['wsgi.url_scheme'],
                                                          request.get_host(),
                                                          request.GET.get("next", "/"))

            if settings.XDOMAINS and not request.user.profile.registered_from:
                request.session['redirect_ts'] = time.time()
                request.session['xnext'] = next_url
                session_hashed = hashlib.md5(request.session.session_key).hexdigest()
                cache.set('sess_' + session_hashed, request.session.session_key, 30)

                redirect_to = '{}://{}{}?token={}'.format(request.META['wsgi.url_scheme'],
                                                          settings.XDOMAINS[0],
                                                          reverse('xdomain_auth'),
                                                          session_hashed)
            else:
                redirect_to = next_url

            if request.is_ajax():
                return {
                    "ok": True,
                    "simple_redirect": redirect_to
                }

            print redirect_to
            return redirect(redirect_to)

        else:
            # сделано из-за странной ошибки с именованием поля.
            # видимо, где-то есть форма со старым названием поля;
            # можно удалить лет через 10, когда все устаканится
            email = request.POST.get("auth-email_phone") or request.POST.get("email")
            users = User.objects.filter(email=email)
            kwargs = {"content_object": users[0]} if users else {}

            Logger(ip=request.META["REMOTE_ADDR"], event=Events.LOGIN_FAIL,
                   params={"email": email}, **kwargs).save()

            if login_try:
                cache.set(cache_key, login_try+1, 20*60)
            else:
                cache.set(cache_key, 1, 20*60)

            if request.is_ajax():
                return {
                    "nok": True,
                    "errors": {k: map(unicode, v) for k, v in form.errors.items()}
                }

    if request.is_ajax():
        return render_to_response("reveal_forms/login.html", RequestContext(request, {"form": form, "next": next}))

    return {
        "form": form,
        "next": next,
        "first_login": True if user else False
    }


def password_reset(request, *args, **kwargs):
    if request.POST:
        u = User.objects.filter(email__iexact=request.POST.get("email")).first()
        if not u:
            messages.add_message(request, messages.ERROR,
                                 _("Your e-mail has not been confirmed or not in the database. "
                                   "Please use the form password recovery through SMS"))
            return HttpResponseRedirect(reverse('password_reset'))
        elif phone_based_registration(u) and u.last_login == datetime.fromtimestamp(0):
            messages.add_message(request, messages.ERROR,
                                 _("Phone number for your account is not confirmed. Please use "
                                   "phone-base password recovery."))
            return HttpResponseRedirect(reverse('password_reset_by_phone'))
    response = django_password_reset(request, *args, post_reset_redirect=reverse("password_reset_done"), **kwargs)
    if request.method == "POST" and isinstance(response, HttpResponseRedirect):
        users = User.objects.filter(email=request.POST["email"])

        kwargs = {"content_object": users[0], "user": users[0]} if users else {}

        Logger(ip=request.META["REMOTE_ADDR"], event=Events.PASSWORD_RESTORED,
               params={"email": request.POST["email"]}, **kwargs).save()
    return response


def password_reset_by_phone(request):
    return render_to_response(
        'registration/custom_password_reset_form_by_phone.html',
        RequestContext(request, {
            "form": PasswordResetByPhoneForm(),
        })
    )


def password_reset_by_phone_done(request):
    return render_to_response(
        'registration/custom_password_reset_done_by_phone.html',
        RequestContext(request, {"form": PasswordResetByPhoneForm()})
    )


def xdomain_auth(request):
    loop_auth = request.GET.get('loop_auth', True)
    if loop_auth == "False":
        loop_auth = False
    if 'token' in request.GET:
        from django.contrib.sessions.models import Session
        token = request.GET.get('token')
        session_key = cache.get('sess_' + token)
        try:
            s = Session.objects.filter(session_key=session_key)[0]
        except IndexError:
            return HttpResponseForbidden()

        data = s.get_decoded()

        if 'redirect_ts' not in data or (time.time() - data['redirect_ts']) > 30:
            return HttpResponseForbidden()

        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore(s.session_key)
        request.session.accessed = True
        request.session.modified = True  # Tell session middleware to send new cookie for sure

        if not loop_auth:
            return HttpResponseRedirect(data['xnext'])

        try:
            domain = '{}://{}{}?token={}'.format(request.META['wsgi.url_scheme'],
                                                 settings.XDOMAINS[settings.XDOMAINS.index(request.get_host()) + 1],
                                                 reverse('xdomain_auth'),
                                                 token)
        except IndexError:
            # No more domains to authenticate
            return HttpResponseRedirect(data['xnext'])
        else:
            return HttpResponseRedirect(domain)
    else:
        raise Http404()


@psa('social:complete')
def complete_social_auth(request, backend, *args, **kwargs):
    return do_complete(request.backend, login_func, request.user,
                       redirect_name=REDIRECT_FIELD_NAME, *args, **kwargs)


def login_func(backend, user, social_user):
    if user.last_login != datetime.fromtimestamp(0):
        _do_login(backend, user, social_user)


def login_as(request, user_id):
    """Login as user_id.

    If there is "was_another_user" key in the session, allow login, bypassing
    the superuser check.
    """
    previous_user_id = request.session.pop('was_another_user', None)

    # Actually, if there is such a key in the session, you can login as anyone
    # you want through this url.
    # This should be secure, as soon as the user could only receive this
    # session key only being a superuser
    if not (request.user.is_superuser or previous_user_id):
        return HttpResponseForbidden()
    user = get_object_or_404(User, pk=user_id)
    # This is needed for "login" function to operate correctly
    user.backend = "django.contrib.auth.backends.ModelBackend"

    # Login the user and set the session key if it was not set before
    request_user_id = request.user.pk
    django_login(request, user)
    if not previous_user_id:
        request.session['was_another_user'] = request_user_id
    return redirect('account_app')


def activate(request, activation_key):
    log.info("Activating key %s" % activation_key)
    account = RegistrationProfile.objects.activate_user(activation_key)

    log.debug("Account=%s" % account)

    if account:
        user_activated.send(sender=None, user=account, request=request)
        return redirect('registration_activation_complete')

    context = RequestContext(request)

    return render_to_response('registration/activate.html', context_instance=context)
