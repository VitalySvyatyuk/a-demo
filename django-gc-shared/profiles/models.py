# -*- coding: utf-8 -*-
from collections import OrderedDict
from datetime import date
from itertools import imap
from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from django_hstore.hstore import DictionaryField as HStoreField

from geobase.models import Country
from geobase.phone_code_widget import CountryPhoneCodeField
from log.models import Events
from otp.models import DEVICE_TYPES, AUTH_SCHEMES
from payments.models import DepositRequest
from platforms.models import AbstractTrade, TradingAccount
from project.validators import allow_file_extensions, allow_file_size
from shared.models import StateSavingModel
from shared.utils import upload_to


GROUPS = (
    (1, "Portfolio management"),
    (2, "Dealing room"),
    (3, "Back office")
)


class UserProfileQueryset(models.manager.QuerySet):
    def sort_by_acc_creation_date(self, desc=True):
        """
        Returns profiles sorted by the last account creation date (and having an account)

        This is not easily done with Django ORM, so SQL patches are used
        """
        return self.extra(
            select={
                'latest_account': "SELECT {accounts_table}.creation_ts \
                                  FROM {accounts_table} \
                                  WHERE {accounts_table}.user_id = {profiles_table}.user_id \
                                  ORDER BY {accounts_table}.creation_ts DESC \
                                  LIMIT 1".format(accounts_table=TradingAccount._meta.db_table,
                                                  profiles_table=UserProfile._meta.db_table),
            },
            order_by=['-latest_account' if desc else "latest_account"],
            where=["EXISTS("
                   "SELECT {accounts_table}.creation_ts "
                   "FROM {accounts_accounts_table} "
                   "WHERE {accounts_table}.user_id = {profiles_table}.user_id)".format(accounts_table=TradingAccount._meta.db_table,
                                                  profiles_table=UserProfile._meta.db_table)])

    def add_last_activity(self, name, check=None, ts=None):
        from django.db.models.expressions import RawSQL
        from django.db.models import Case, When
        value = RawSQL("ARRAY[%s]::varchar[] || last_activities[1:10]", [name])
        if check == 'first':
            value = Case(
                When(last_activities__0=name, then='last_activities'),
                default=value,
            )
        elif check == 'contains':
            value = Case(
                When(last_activities__contains=[name], then='last_activities'),
                default=value,
            )

        new_ts_value = Case(
            When(last_activity_ts__gte=ts or datetime.now(), then='last_activity_ts'),
            default=ts or datetime.now(),
        )
        self.update(last_activities=value, last_activity_ts=new_ts_value)


class UserProfileManager(models.Manager):
    def get_queryset(self):
        """Returns a new UserProfileQueryset object"""
        return UserProfileQueryset(self.model, using=self._db)

    def birthday_limits(self, lower=None, upper=None):
        """Return only rows, where birthday is beetween lower and upper

        Limits should be provided in current year dates, e.g.
        lower=date(2011,12,28) if current year is 2011
        """
        sql = "birthday + (extract(year from now()) - extract(year from birthday))*'1 year'::interval"
        qs = self.get_queryset()
        if not (lower or upper):
            return qs
        if lower and not upper:
            where = ['%%s <= %s' % sql]
            params = [lower]
        elif upper and not lower:
            where = ['%s <= %%s' % sql]
            params = [upper]
        else:
            where = ['%s BETWEEN %%s AND %%s' % sql]
            params = [lower, upper]
        return qs.extra(where=where, params=params)

    def russian(self):
        return self.get_queryset().filter(models.Q(country__in=Country.objects.russian()) |
                                           models.Q(country=None))

    def non_russian(self):
        return self.get_queryset().filter(country__in=Country.objects.non_russian())

    def similar_by_phone(self, phone):
        from telephony.utils import get_common_phone_tail
        phone_tail = get_common_phone_tail(phone)
        if not phone_tail:
            return self.none()
        return UserProfile.objects.filter(
            phone_mobile__endswith=phone_tail
        ).order_by('id')


class UserProfile(StateSavingModel):
    NET_CAPITAL_CHOICES = ANNUAL_INCOME_CHOICES = (
        ("> 100000", _("over 100 000")),
        ("50000 - 100000", "50 000 - 100 000"),
        ("10000 - 50000", "10 000 - 50 000"),
        ("< 10000", _("below 10 000")),
    )
    FINANCIAL_COMMITMENTS =(
        ("< 20%", _("Less than 20%")),
        ("21% - 40%", "21% - 40%"),
        ("41% - 60%", "41% - 60%"),
        ("61% - 80%", "61% - 80%"),
        ("> 80%", _("Over 80%")),
    )

    FR_TRANSACTIONS = (
        ("Daily", _("Daily")),
        ("Weekly", _("Weekly")),
        ("Monthly", _("Monthly")),
        ("Yearly", _("Yearly")),
    )

    AV_TRANSACTIONS = (
        ("< 10000", _("Less than 10 000")),
        ("10000 - 50000", "10 000 - 50 000"),
        ("50001 - 100000", "50 001 - 100 000"),
        ("100001 - 200000", "100 001 - 200 000"),
        ("> 250000", _("Over 250 000")),
    )

    EMPLOYMENT_STATUS = (
        ("Employed", _("Employed")),
        ("Unemployed", _("Unemployed")),
        ("Self employed", _("Self employed")),
        ("Retired", _("Retired")),
        ('Student', _('Student'))
    )

    PURPOSES = (
        ("Investment", _("Investment")),
        ("Hedging", _("Hedging")),
        ("Speculative trading", _("Speculative trading"))
    )

    user = models.OneToOneField(User, unique=True, related_name="profile")
    middle_name = models.CharField(_('Middle name'), max_length=45,
                                   blank=True, null=True)
    birthday = models.DateField(_('Birthday'), blank=True, null=True)
    country = models.ForeignKey('geobase.Country', verbose_name=_('Country'),
                                blank=True, null=True, help_text=_('Example: Russia'))
    city = models.CharField(_('City'), max_length=100,
                            blank=True, null=True, help_text=_('The city where you live'))
    state = models.ForeignKey('geobase.Region', verbose_name=_('State / Province'),
                              blank=True, null=True)
    address = models.CharField(_('Residential address'), max_length=80,
                               blank=True, null=True, help_text=_('Example: pr. Stachek, 8A'))
    skype = models.CharField(_('Skype'), max_length=80,
                             blank=True, null=True, help_text=_('Example: gc_clients'))
    icq = models.CharField(_('ICQ'), blank=True, null=True, max_length=20,
                           help_text=_('Example: 629301132'))
    phone_home = CountryPhoneCodeField(_('Home phone'), max_length=40, db_index=True,
                                       blank=True, null=True, help_text=_('Example: 8-800-333-1003'))
    phone_work = CountryPhoneCodeField(_('Work phone'), max_length=40, db_index=True,
                                       blank=True, null=True, help_text=_('Example: +7 (812) 300-81-96'))
    phone_mobile = CountryPhoneCodeField(_('Mobile phone'), max_length=40, db_index=True,
                                         blank=True, null=True, help_text=_('Example: +7 (911) 200-19-55'))
    avatar = models.ImageField(_('Avatar'), blank=True, null=True,
                               upload_to=upload_to('userfiles/avatars'), help_text=_('Your photo'))
    social_security = models.CharField(_('Social security number'),
                                       max_length=50, blank=True, null=True)
    tin = models.CharField(_('TIN'), max_length=50,
                           help_text=_('Tax identification number'), blank=True, null=True)
    manager = models.ForeignKey(User, related_name="managed_profiles", blank=True,
                                null=True, verbose_name=u"Менеджер по торговле")
    manager_auto_assigned = models.BooleanField(u'Менеджер назначен атоматически',
                                                default=True)
    assigned_to_current_manager_at = models.DateTimeField(_('Assigned to manager at'), blank=True, null=True)
    language = models.CharField(max_length=20,
                                choices=settings.LANGUAGES, blank=True, null=True)
    agent_code = models.PositiveIntegerField(verbose_name=_('Agent code'),
                                             blank=True, null=True,
                                             help_text=_('If you don\'t know what it is, leave empty'))
    lost_otp = models.BooleanField(_("Did user lose his OTP"), default=False)
    auth_scheme = models.CharField(max_length=10, verbose_name="Auth scheme", choices=AUTH_SCHEMES, null=True)
    params = JSONField(_("Details"), blank=True, null=True, default={})
    user_from = JSONField(_("Source"), blank=True, null=True, default={})
    registered_from = models.CharField(
        max_length=255,
        verbose_name=_('Registered from'),
        default="",
        blank=True
    )
    last_activity_ts = models.DateTimeField(_('Last activity'), default=datetime(1970, 1, 1), db_index=True)
    last_activities = ArrayField(models.CharField(max_length=255), verbose_name='Last activities', default=list)
    nationality = models.ForeignKey('geobase.Country',
                                    verbose_name=_('Nationality'),
                                    related_name='nations',
                                    blank=True, null=True,
                                    help_text=_('Example: Russia'))
    net_capital = models.CharField(_('Net capital (USD)'), max_length=50, choices=NET_CAPITAL_CHOICES,
                                   blank=True, null=True)
    annual_income = models.CharField(_('Annual income (USD)'), max_length=50,
                                     choices=ANNUAL_INCOME_CHOICES,
                                     blank=True, null=True)
    tax_residence = models.ForeignKey('geobase.Country', verbose_name=_('Tax residence'), related_name='taxes',
                                      blank=True, null=True)
    us_citizen = models.BooleanField(_('US citizen'), default=False)
    employment_status = models.CharField(_('Employment status'), max_length=90, choices=EMPLOYMENT_STATUS,
                                         blank=True, null=True)
    source_of_funds = models.CharField(_('Source of funds'), max_length=90, blank=True, null=True)
    nature_of_biz = models.CharField(_('Nature of business'), max_length=90, blank=True, null=True)
    financial_commitments = models.CharField(_('Monthly financial commitments'), max_length=90,
                                             choices=FINANCIAL_COMMITMENTS, blank=True, null=True)

    account_turnover = models.IntegerField(_('Anticipated account turnover (USD)'),
                                           null=True, blank=True)
    purpose = models.CharField(_('Purpose to open an Arum capital account'), choices=PURPOSES,
                               max_length=50, blank=True, null=True)

    education_level = models.CharField(_('Level of education'), max_length=90, blank=True, null=True)

    allow_open_invest = models.BooleanField(_('Can open ECN.Invest accounts'), default=False)

    investment_undertaking = HStoreField(default={"Units of collective investment undertaking": "No"})

    transferable_securities = HStoreField(default={"Transferable securities": "No"})

    derivative_instruments = HStoreField(default={"Derivative instruments (incl. options, futures, swaps, FRAs, etc.)": "No"})

    forex_instruments = HStoreField(default={"Trading experience FOREX/CFDs": "No"})

    objects = UserProfileManager()

    email_verified = models.BooleanField(_('Email is verified'), default=False)

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')

    def __unicode__(self):
        if self.user.first_name and self.user.last_name:
            return u"%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return unicode(self.user)

    ###
    # Helpers section
    ###

    def add_last_activity(self, name, check=None, ts=None):
        UserProfile.objects.filter(id=self.id).add_last_activity(name=name, check=check, ts=ts)
        self.refresh_from_db(fields=['last_activities', 'last_activity_ts'])

    @property
    def last_activity_translated(self):
        from django.utils.translation import ugettext_lazy as _
        return map(_, self.last_activities)

    @property
    def trades(self):
        return AbstractTrade.objects.filter(login__in=list(self.user.accounts.values_list("mt4_id", flat=True)))

    @property
    def is_russian(self):
        return (self.country is None) or self.country.is_russian_language

    def has_groups(self, *groups):
        """
        Returns True if related User is a member of at least one of the
        given groups, else returns False.
        """
        return self.user.groups.filter(name__in=groups).exists()

    has_group = has_groups  # Would work perfectly fine for one group.

    ###
    # Validations section
    ###
    INCOMPLETE = 0
    NO_DOCUMENTS = 1
    UNVERIFIED = 2
    VERIFIED = 3

    STATUSES = {
        INCOMPLETE: _('Registration incomplete'),
        NO_DOCUMENTS: _('Documents have not been uploaded'),
        UNVERIFIED: _('Pending approval'),
        VERIFIED: _('Approved'),
    }


    @property
    def status(self):
        '''
        Returns user status from STATUSES:
        VERIFIED if all satisfied:
            a) profile form is complete (all required fields not null && verified email) 
            b) there is no rejected docs (is_rejected in UserDocument)
            c) and user is marked validated (first_name & last_name in user)
        UNVERIFIED if all satisfied:
            a) profile is complete
            b) there are uploaded but not rejected docs
        NO_DOCUMENTS if all satisfied:
            a) profile is complete
            b) there are no uploaded docs
        INCOMPLETE if:
            profile is not complete OR there are rejected docs!
        '''
        required_fields = ['birthday', 'nationality', 'state', 'city', 'address',
                           'net_capital', 'annual_income']
        complete_profile = all(getattr(self, f) for f in required_fields) and self.email_verified

        user_documents = UserDocument.objects.filter(user=self.user).values_list('is_rejected')

    
        if user_documents and all([i[0] for i in user_documents]):
            return self.INCOMPLETE
        if complete_profile:
            if self.has_valid_documents():
                return self.VERIFIED
            if self.has_documents():
                return self.UNVERIFIED
            return self.NO_DOCUMENTS
        else:
            return self.INCOMPLETE

    def has_valid_phone(self):
        return self.has_validation("phone_mobile")

    def make_valid(self, name):
        set_validation(self.user, name, True)

    def drop_valid(self, name):
        set_validation(self.user, name, False)

    def has_documents(self, *document_types):

        if not document_types:
            document_types = (DOCUMENT_TYPES.PASSPORT_SCAN,
                              DOCUMENT_TYPES.RESIDENTIAL_ADDRESS,
                              DOCUMENT_TYPES.ADDRESS_PROOF)

        return UserDocument.objects.filter(user=self.user, name__in=document_types, is_deleted=False, is_rejected=False).exists()

    def has_valid_documents(self):
        return self.has_validation("first_name", "last_name")

    def make_documents_valid(self):
        '''
        '''
        self.make_valid('first_name')
        self.make_valid('last_name')
        # # Make all documents sent by user not rejected
        # UserDocument.objects.filter(user=self.user).update(is_rejected=False)

    def make_documents_invalid(self, *document_types):
        '''
        '''
        if not document_types:
            document_types = [DOCUMENT_TYPES.PASSPORT_SCAN,
                              DOCUMENT_TYPES.RESIDENTIAL_ADDRESS,
                              DOCUMENT_TYPES.ADDRESS_PROOF]

        UserDocument.objects.filter(user=self.user, name__in=document_types, is_deleted=False,
                                    is_rejected=False).update(is_rejected=True)

        self.drop_valid('first_name')
        self.drop_valid('last_name')

    def has_validation(self, *fields):

        if not fields:
            return False

        return self.user.validations.filter(key__in=fields, is_valid=True).count() == len(fields)

    ###
    # OTP section
    ###

    @property
    def otp_devices(self):
        for device_type in DEVICE_TYPES:
            devices = device_type.objects.devices_for_user(self.user).filter(is_deleted=False)
            if devices:
                return devices
        return devices

    @property
    def otp_device(self):
        if self.otp_devices:
            return self.otp_devices[0]

    @property
    def has_otp_devices(self):
        return any(imap(lambda x: x.objects.devices_for_user(self.user).filter(is_deleted=False).exists(), DEVICE_TYPES))

    def delete_otp_devices(self, lost_otp=False):
        self.otp_devices.update(is_deleted=True)
        self.auth_scheme = None
        if lost_otp:
            self.lost_otp = True
        self.save()

    def set_manager(self, manager, taken_by_manager=False, similar=True):
        """
        Sets manager to this profile and similars with flags and dates
        """
        if manager != self.manager:
            self.assigned_to_current_manager_at = datetime.now()
            self.manager = manager
        self.save()
        if similar:
            with Logger.with_tag('set_manager_similar'):
                with Logger.with_params(set_manager_similar_to=self.id):
                    for sim in self.similar:
                        sim.set_manager(
                            self.manager,
                            taken_by_manager=taken_by_manager,
                            similar=False)

    def autoassign_manager(self, force=False, with_similar=True):
        manager = User.objects.filter(is_superuser=True).first()

        if manager:
            self.set_manager(manager, similar=with_similar)
        return manager

    def get_manager_slices(self, start, end):
        if isinstance(start, date):
            start = datetime.combine(start, datetime.min.time())
        if isinstance(end, date):
            end = datetime.combine(end, datetime.min.time())
        changes = Logger.objects.filter(event=Events.MANAGER_CHANGED, at__range=(start, end),
                                        object_id=self.user.id).order_by('at')
        if changes:
            old_manager_id = changes[0].params.get('old_id')
            starting_manager = User.objects.filter(id=old_manager_id).first() if old_manager_id else None
        else:
            starting_manager = self.manager
        result = [(start, starting_manager)]
        for change in changes:
            changed_to_id = change.params.get('new_id')
            if changed_to_id:
                changed_to = User.objects.filter(id=changed_to_id).first()
                if changed_to:
                    result.append((change.at, changed_to))
        return result

    @staticmethod
    def get_manager_from_slices(slices, date):
        if date < slices[0][0]:
            return slices[0][1]
        for slice in reversed(slices):
            if slice[0] < date:
                return slice[1]
        return slices[-1][1]

    def get_manager_at(self, at):
        """At the time of writing, our managers work for 1-2 weeks and leave, so this method is really indispensable"""
        last_change = Logger.objects.filter(event=Events.MANAGER_CHANGED, at__lte=at,
                                            object_id=self.user.id).order_by('-at').first()
        if last_change:
            changed_to_id = last_change.params.get('new_id')
            if changed_to_id:
                changed_to = User.objects.filter(id=changed_to_id).first()
                if changed_to:
                    return changed_to
        return self.manager  # Ok, we couldn't find the historic manager

    def get_amo(self):
        """Returns AmoContact with protection from non existing"""
        return None

    def get_full_name(self):
        name_parts = filter(lambda x: x, [
            self.user.last_name,
            self.user.first_name,
            self.middle_name,
        ])
        if name_parts:
            return ' '.join(name_parts)
        return self.user.username

    def get_short_name(self):
        return ' '.join([
            self.user.last_name or self.user.username,
            self.user.first_name[0] + '.' if self.user.first_name else '',
            self.middle_name[0] + '.' if self.middle_name else '',
        ]).strip()

    @property
    def related_logs(self):
        qs = Logger.objects.by_object(self.user)
        qs |= Logger.objects.by_object(self)
        qs |= Logger.objects.by_user(self.user)

        from platforms.models import TradingAccount
        pma_ids = self.user.accounts.values_list('id', flat=True)
        qs |= Logger.objects.by_object_ids(TradingAccount, pma_ids)
        return qs

    @property
    def social_profile_link(self):
        social_auth = self.user.social_auth.first()
        if social_auth is None:
            return
        if social_auth.provider == "facebook":
            return u"https://www.facebook.com/%s" % social_auth.uid
        elif social_auth.provider == "vk-oauth2":
            return u"https://vk.com/id%s" % social_auth.uid
        elif social_auth.provider == "odnoklassniki-oauth2":
            return u"http://ok.ru/profile/%s" % social_auth.uid

    ###
    # Alternative sites section
    ###

    def get_site_name(self):
        if self.registered_from in settings.PRIVATE_OFFICES:
            return settings.PRIVATE_OFFICES[self.registered_from]['site_name']
        else:
            return "Arum Capital"

    def get_site_domain(self):
        if self.registered_from in settings.PRIVATE_OFFICES:
            return settings.PRIVATE_OFFICES[self.registered_from]['domain']
        else:
            return "arum.uptrader.us"

    def get_time_zone(self):
        time_zone = None
        if self.state:
            time_zone = self.state.get_time_zone()
        if not time_zone and self.country:
            time_zone = self.country.get_time_zone()
        return time_zone

    def get_local_time(self):
        time_zone = self.get_time_zone()
        if time_zone is None:
            return
        return pytz.timezone("Europe/Moscow").localize(datetime.now()).astimezone(time_zone)

    @property
    def deposit_requests(self):
        return DepositRequest.objects.filter(account__user=self.user)

    def add_verified_card(self, card_number):
        self.params.setdefault('verified_cards', []).append(card_number)
        self.save()

    def is_card_verified(self, card_number):
        return card_number in self.params.get('verified_cards', [])

    def push_notification(self, text, extra=None):
        return

    def full_name(self):
        return format_html(
            '<span style="color: #011d37; '
            'font-size: 38px; '
            'font-family: Arial, Helvetica, sans-serif; '
            'text-shadow: 0px 0px 6px rgba(1,1,1,0.4);">'
            '{} {} {}</span>',
            self.user.first_name,
            self.user.last_name,
            self.middle_name if self.middle_name else '',
        )


class UserDataValidation(models.Model):
    user = models.ForeignKey(User, related_name="validations")
    key = models.CharField(_('Parameter'), max_length=50)
    is_valid = models.NullBooleanField(_('Is the data valid?'),
                                       blank=True, null=True)
    comment = models.CharField(_('Manager comment'), max_length=160,
                               blank=True, null=True)

    def __nonzero__(self):
        return bool(self.is_valid)

    class Meta:
        unique_together = ("user", "key")


def get_validation(user, field):
    validation, created = user.validations.get_or_create(key=field)

    if field == "email" and user.is_active:
        # Email is assumed to be valid if account is activated
        validation.is_valid = True

    return validation


def set_validation(user, field, is_valid, comment=None):
    if not user.validations.filter(key=field).update(is_valid=is_valid, comment=comment):
        user.validations.create(key=field, is_valid=is_valid, comment=comment)


class DOCUMENT_TYPES(object):
    CREDIT_CARD_BACK = 'Credit_card_back_side'
    CREDIT_CARD_FRONT = 'Credit_card_front_side'
    DRIVER_LICENSE = 'driver_license'
    PASSPORT_SCAN = 'passport_scan'
    RESIDENTIAL_ADDRESS = 'residential_address'
    ADDRESS_PROOF = 'address_proof'
    IB_AGREEMENT = 'real_ib_agreement'
    RECEIPT = 'receipt'
    OTHER = 'other'


DOCUMENTS = OrderedDict([
    (DOCUMENT_TYPES.PASSPORT_SCAN, _('Proof of Identification')),
    (DOCUMENT_TYPES.RESIDENTIAL_ADDRESS, _(
        'Copy of your passport page with the registered residential address')),
    (DOCUMENT_TYPES.ADDRESS_PROOF, _('Proof of residential address')),
    (DOCUMENT_TYPES.DRIVER_LICENSE, _('Driver license')),
    (DOCUMENT_TYPES.CREDIT_CARD_BACK, _('Credit card back side')),
    (DOCUMENT_TYPES.CREDIT_CARD_FRONT, _('Credit card front side')),
    (DOCUMENT_TYPES.IB_AGREEMENT, _('Real IB agreement')),
    (DOCUMENT_TYPES.OTHER, _(u'Other document')),
])

DOCUMENTS_FIELDS = {
    DOCUMENT_TYPES.CREDIT_CARD_BACK: [
        _('First name'), _('Last name'), _('Birthday')
    ],
    DOCUMENT_TYPES.CREDIT_CARD_FRONT: [
        _('First name'), _('Last name'), _('Birthday')
    ],
    DOCUMENT_TYPES.RESIDENTIAL_ADDRESS: [
        _('Address'),
    ],
    DOCUMENT_TYPES.DRIVER_LICENSE: [
        _('First name'), _('Last name'), _('ID Number')
    ],
    DOCUMENT_TYPES.PASSPORT_SCAN: [
        _('First name'), _('Last name'), _('ID Number'), _('Issue date')
    ],
    DOCUMENT_TYPES.IB_AGREEMENT: [],
    DOCUMENT_TYPES.OTHER: [],
    DOCUMENT_TYPES.ADDRESS_PROOF: []
}

class UserDocumentManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(is_deleted=False)


class UserDocument(models.Model):
    user = models.ForeignKey(User, related_name="documents")
    name = models.CharField(_('Document name'), max_length=100, choices=DOCUMENTS.items())
    is_rejected = models.BooleanField(_('Documents was rejected'), default=False)
    description = models.TextField(_('Document description'), null=True, blank=True)

    EXTENSIONS = 'doc', 'docx', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pdf'
    FILESIZE_LIMIT = 1024 ** 2 * 5
    file = models.FileField(
        _('File'),
        upload_to=upload_to('files'),
        help_text=_('Supported extensions: %(ext)s. Filesize limit: %(limit)s Mb'),
        validators=[
            allow_file_extensions(EXTENSIONS),
            allow_file_size(FILESIZE_LIMIT)
        ]
    )
    creation_ts = models.DateTimeField(_('Creation timestamp'), auto_now_add=True)
    is_deleted = models.BooleanField('Document is deleted', default=False)
    fields = JSONField(
        _('Document fields'),
        null=True,
        blank=True
    )

    objects = UserDocumentManager()

    def __unicode__(self):
        return unicode(DOCUMENTS[self.name])


from profiles.signal_handlers import *
