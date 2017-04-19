from django.core.management import BaseCommand

from platforms.types import get_account_type
from platforms.models import TradingAccount, Mt4DemoUser
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime, timedelta
from shared.validators import email_re
from smtplib import SMTPRecipientsRefused
from registration.backends import register_user


def guess_country(name):
    from geobase.models import Country
    name = unicode(name)  # 4 sure, to make title() work
    countries = Country.objects.filter(
        Q(name=name) | Q(name_en=name) |
        Q(name=name.title()) | Q(name_en=name.title())
    )
    return countries[0] if countries else None


def guess_state(name, city_name):
    from geobase.models import Region, City
    name = unicode(name)  # 4 sure, to make title() work
    regions = Region.objects.filter(
        Q(name=name) | Q(name_en=name) |
        Q(name=name.title()) | Q(name_en=name.title())
    )
    region = None
    if regions:
        region = regions[0]
    else:
        #try to guess region by city name
        cities = City.objects.filter(
            Q(name=city_name) | Q(name_en=city_name) |
            Q(name=city_name.title()) | Q(name_en=city_name.title())
        )
        if cities and cities[0].region:
            region = cities[0].region
    return region


# noinspection PyAbstractClass
class Command(BaseCommand):
    def execute(self, *args, **options):
        #select accounts, created in last day
        #with email set
        for mt4du in (Mt4DemoUser.objects
                                 .filter(regdate__gt=datetime.now()-timedelta(1), enable=1)
                                 .exclude(Q(email=None) | Q(email=''))):
            #if we have no Mt4Account for this Mt4DemoUser
            if TradingAccount.objects.filter(mt4_id=mt4du.login).exists():
                continue

            #damn, we could have multiple accounts with same email, so
            # we should take latest one
            users = User.objects.filter(email__iexact=mt4du.email).order_by('-date_joined')

            if users:
                user = users[0]
            else:
                #possible, we should create new one
                user = self.create_user_from_mt4demouser(mt4du)

            #if we cannot create user - skip this one
            if not user:
                continue

            #damn, safe if better than unsafe, lol
            TradingAccount.objects.get_or_create(
                user=user,
                mt4_id=mt4du.login,
                creation_ts=mt4du.regdate,
                group_name=mt4du.group,
                #simplied code from create_account task
                _group_as_char=unicode(get_account_type(mt4du.group))
            )

    @staticmethod
    def create_user_from_mt4demouser(mt4du):
        if (not email_re.match(mt4du.email)
                or not get_account_type(mt4du.group)
                or not mt4du.name):
            return None

        names = mt4du.name.split()
        try:
            new_user = register_user(
                email=mt4du.email.lower(),
                first_name=names[0],
                last_name=names[1] if len(names) > 1 else u'',
                phone_mobile=mt4du.phone,
                country=guess_country(mt4du.country),
                state=guess_state(mt4du.state, mt4du.city),
                city=mt4du.city,
                address=mt4du.address
            )
        #skip accounts with wrong email
        except SMTPRecipientsRefused:
            return None

        assert new_user
        #update date_joined to match mt4 account creation date
        new_user.date_joined = mt4du.regdate
        new_user.save()

        profile = new_user.profile
        profile.user_from = {'system': 'MT4'}
        profile.save()
        return new_user
