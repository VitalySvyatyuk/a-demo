# coding=utf-8
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib import messages
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from geobase.phone_code_widget import split_phone_number
from geobase.utils import get_geo_data

from notification.models import get_from_email, send as send_notification
from profiles.models import UserProfile
from .models import RegistrationProfile
from registration.utils import generate_username_from_email
from sms import send


from signals import user_registered


class EmailBackend(ModelBackend):
    def authenticate(self, email_phone=None, password=None, login_from=''):
        try:
            user = User.objects.get(Q(email__iexact=email_phone) |
                                    Q(profile__phone_mobile__iexact=email_phone) |
                                    Q(username__iexact=email_phone),
                                    profile__registered_from=login_from)
            if user.check_password(password):
                return user
        except (User.DoesNotExist, User.MultipleObjectsReturned,
                ValueError):  # No email provided.
            return None


def phone_based_registration(user):
    return True 


def send_activation_email(user, password, reg_profile):
    context = {
        "user": user,
        "password": password,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        'activation_key': reg_profile.activation_key,
    }
    send_notification([user], "user_registered", context)


def register_user(email, request=None, **kwargs):
    username, email, password = generate_username_from_email(email), email, User.objects.make_random_password(8)
    new_user = User.objects.create_user(username, email, password)
    new_user.first_name = kwargs.get('first_name')
    new_user.last_name = kwargs.get('last_name', '')
    new_user.save()
    user_registered.send(sender=None, user=new_user, request=request)

    registration_profile = RegistrationProfile.objects.create_profile(new_user)



    UserProfile.objects.get_or_create(user=new_user)
    new_user.profile.refresh_state()

    new_user.profile.phone_mobile = kwargs.get('phone_mobile')
    geo_data = get_geo_data(request) if request else {}
    new_user.profile.country = kwargs.get('country') or split_phone_number(new_user.profile.phone_mobile)[2] or geo_data.get("country")
    new_user.profile.state = kwargs.get('state') or geo_data.get("region")
    if new_user.profile.state and new_user.profile.state.country != new_user.profile.country:
        new_user.profile.state = None
    new_user.profile.city = kwargs.get('city')
    new_user.profile.address = kwargs.get('address')
    if kwargs.get('agent_code'):
        new_user.profile.agent_code = kwargs.get('agent_code')
    elif request and 'agent_code' in request.session:
        new_user.profile.agent_code = request.session['agent_code']

    new_user.profile.registered_from = kwargs.get('registered_from', '')

    # we should not create tasks with clients from partner offices
    new_user.profile.registered_from = kwargs.get('registered_from', '')
    if phone_based_registration(new_user):
        hostname = request.get_host() if request else settings.ROOT_HOSTNAME
        text = _("Your password for account at %(hostname)s: %(password)s") % {'hostname': hostname,
                                                                               'password': password}
        send(to=new_user.profile.phone_mobile, text=text)
        password = _("Password was sent by phone")

    new_user.profile.save(refresh_state=False)  # first save of profile

    send_activation_email(new_user, password, registration_profile)

    # This is needed for "login" function to operate correctly
    new_user.backend = "django.contrib.auth.backends.ModelBackend"

    if request and not phone_based_registration(new_user):
        login(request, new_user)
        days_left = settings.ACCOUNT_ACTIVATION_DAYS
    return new_user
