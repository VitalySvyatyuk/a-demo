# -*- coding: utf-8 -*-

from django.conf.urls import *
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from forms import EmailAuthenticationForm, ShortLandingProfileRegistrationForm

#from registration.views import LoginWizard, FORMS, show_otp

urlpatterns = patterns(
    '',
    url(r'^login_as/(?P<user_id>\d+)/$', 'registration.views.login_as', name='login_as_user_id'),

    # Login/logout/register
    url(r'^register/$', 'registration.views.register', name='registration_register'),
    url(r'^register_iframe/$', 'registration.views.register', name='registration_iframe_register',
        kwargs={
            'template': 'registration/iframe_registration.html',
            'next': '/my/accounts/register_iframe/',
        }),
    url(r'^login/$', 'registration.views.login',
        {'authentication_form': EmailAuthenticationForm},
        name='auth_login'),
    url(r'^login/(?P<user_id>\d+)/$', 'registration.views.login',
        {'authentication_form': EmailAuthenticationForm},
        name='auth_login_phone'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='auth_logout'),

    url(r'^xauth/$', 'registration.views.xdomain_auth', name='xdomain_auth'),

    # Account activation
    url(r'^activate/complete/$', RedirectView.as_view(url='/account/profile/info'),
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$', "registration.views.activate", name='registration_activate'),

    # Password reset
    url(r'^passreset/$', "registration.views.password_reset",
        {'template_name': 'registration/custom_password_reset_form.html'},
        name='password_reset'),
    url(r'^passreset/phone/$', "registration.views.password_reset_by_phone",
        name='password_reset_by_phone'),
    url(r'^passreset/phone/done/$', "registration.views.password_reset_by_phone_done",
        name='password_reset_by_phone_done'),

    url(r'^passresetdone/$', auth_views.password_reset_done,
        {'template_name': 'registration/custom_password_reset_done.html'},
        name='password_reset_done'),
    url(r'^passresetconfirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'template_name': 'registration/custom_password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^passresetcomplete/$', auth_views.password_reset_complete,
        {'template_name': 'registration/custom_password_reset_complete.html'},
        name='password_reset_complete'),
)
