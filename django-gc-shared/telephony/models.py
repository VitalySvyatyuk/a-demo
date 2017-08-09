# -*- coding: utf-8 -*-
import re

from django.db import models
from django.db.models import Q, Sum
from django.contrib.auth.models import User
from shared.models import StateSavingModel
from telephony.utils import get_common_phone_tail


def safe_phone_num(phone_num_str):
    if not phone_num_str:
        return phone_num_str
    if phone_num_str.startswith("+") or phone_num_str.isdigit():
        return '***' + phone_num_str[-4:]
    else:
        return phone_num_str


def parse_channel_name(chan_str):
    #channel is a string like SIP/K.COBAIN-00002aac
    # so we sould extract K.COBAIN to find telephony user by SIP
    match = re.search("(?P<type>.+)/(?P<name>.+)-[\dabcdef]+", chan_str)
    if not match:
        return None, None
    return match.group('type'), match.group('name')


class ExternalAsteriskCDR(models.Model):
    class Meta:
        db_table = 'cdr'
        managed = False

    #but anyway we should use https://gist.github.com/iorlas/6219364
    id = models.IntegerField(primary_key=True, db_column='cdr_id')  # FIXME: зачем переопределять pk?
    calldate = models.DateTimeField(auto_now_add=True)
    clid = models.CharField(default=u'', max_length=80)
    src = models.CharField(default=u'', max_length=80)
    dst = models.CharField(default=u'', max_length=80)
    dcontext = models.CharField(default=u'', max_length=80)
    channel = models.CharField(default=u'', max_length=80)
    dstchannel = models.CharField(default=u'', max_length=80)
    lastapp = models.CharField(default=u'', max_length=80)
    lastdata = models.CharField(default=u'', max_length=80)
    duration = models.IntegerField(default=0)
    billsec = models.IntegerField(default=0)
    disposition = models.CharField(default=u'', max_length=45)
    amaflags = models.IntegerField(default=0)
    accountcode = models.CharField(default=u'', max_length=20)
    uniqueid = models.CharField(default=u'', max_length=32)
    recordingfile = models.CharField(default=u'', max_length=255)
    userfield = models.CharField(default=u'', max_length=255)

    def delete(self, *args, **kwargs):
        raise Exception("FUQ U")

    def get_record_path(self):
        if self.recordingfile:
            return "http://138.201.206.11/records/{0}".format(self.recordingfile)

    @property
    def safe_src(self):
        return safe_phone_num(self.src)

    @property
    def safe_dst(self):
        return safe_phone_num(self.dst)

    @property
    def local_cdr(self):
        try:
            return CallDetailRecord.objects.get(external_cdr_id=self.pk)
        except CallDetailRecord.DoesNotExist:
            return None

    def source_info(self):
        from crm.models import PersonalManager
        from profiles.models import UserProfile

        type, name = parse_channel_name(self.channel)
        obj = None
        if 'incoming' in name:
            obj = UserProfile.objects.similar_by_phone(self.src).first()
        elif self.channel:
            obj = PersonalManager.objects.filter(sip_name=name).first()
        return self.src, name, obj.user if obj else None

    def dest_info(self):
        from crm.models import PersonalManager
        from profiles.models import UserProfile

        type, name = parse_channel_name(self.dstchannel or "")
        obj = None

        #Check for existing of B-leg
        if self.dstchannel:
            obj = (PersonalManager.objects.filter(sip_name=name).first()
                   or UserProfile.objects.similar_by_phone(self.dst).first())
        return self.dst, name, obj.user if obj else None


class CallDetailRecordQuerySet(models.QuerySet):
    def by_number(self, phone, out=True, to=True):
        phone_tail = get_common_phone_tail(phone)
        if not phone_tail:
            return self.none()
        q = Q()
        if out:
            q |= Q(number_a__endswith=phone_tail)
        if to:
            q |= Q(number_b__endswith=phone_tail)
        return self.filter(q)

    def _by_user(self, user, out=True, to=True):
        q = Q()
        if out:
            q |= Q(user_a=user)
        if to:
            q |= Q(user_b=user)
        return self.filter(q)

    def by_user(self, user, out=True, to=True, with_phone=True):
        qs = self._by_user(user, out=out, to=to)
        if with_phone:
            qs |= self.by_number(user.profile.phone_mobile, out=out, to=to)
        return qs

    def from_user(self, user, with_phone=True):
        return self.by_user(user, out=True, to=False, with_phone=with_phone)

    def to_user(self, user, with_phone=True):
        return self.by_user(user, out=False, to=True, with_phone=with_phone)

    def from_or_to_user(self, user, with_phone=True):
        return self.by_user(user, out=True, to=True, with_phone=with_phone)

    def total_duration(self):
        return self.aggregate(sum=Sum('duration')).get('sum') or 0

    def answered(self):
        return self.filter(disposition="ANSWERED")

    def not_answered(self):
        return self.exclude(disposition="ANSWERED")


class CallDetailRecord(models.Model):
    external_cdr_id = models.IntegerField(u'External ID', unique=True)
    user_a = models.ForeignKey(User, related_name='outbound_calls', null=True, blank=True)
    user_b = models.ForeignKey(User, related_name='inbound_calls', null=True, blank=True)
    name_a = models.CharField(u'A-User Asterisk', max_length=64, null=True, blank=True)
    name_b = models.CharField(u'B-User Asterisk', max_length=64, null=True, blank=True)
    number_a = models.CharField(u'A-Number Asterisk', max_length=64, null=True, blank=True)
    number_b = models.CharField(u'B-Number Asterisk', max_length=64, null=True, blank=True)

    duration = models.IntegerField(default=0, null=True, blank=True)
    disposition = models.CharField(default=u'', max_length=64, null=True, blank=True)
    recording_file = models.CharField(u'Record', max_length=255, null=True, blank=True)
    call_date = models.DateTimeField(u'Call\'s date')
    price = models.DecimalField(u'Price', max_digits=6, decimal_places=2, null=True, blank=True)

    objects = CallDetailRecordQuerySet.as_manager()

    @property
    def external_cdr(self):
        try:
            return ExternalAsteriskCDR.objects.get(id=self.external_cdr_id)
        except ExternalAsteriskCDR.DoesNotExist:
            return None

    def get_record_path(self):
        if self.recording_file:
            return "http://138.201.206.11/records/{0}".format(self.recording_file)

    @property
    def safe_number_a(self):
        return safe_phone_num(self.number_a)

    @property
    def safe_number_b(self):
        return safe_phone_num(self.number_b)

    def source_str(self, safe=True):
        if self.user_a:
            return self.user_a.get_full_name() or self.user_a.username
        else:
            return u"{0}({1})".format(
                self.safe_number_a if safe else self.number_a,
                self.name_a)

    def dest_str(self, safe=True):
        if self.user_b:
            return self.user_b.get_full_name() or self.user_b.username
        else:
            return u"{0}({1})".format(
                self.safe_number_b if safe else self.number_b,
                self.name_b)

    def __unicode__(self):
        return u"Call from {0} to {1} at {2}".format(
            self.number_a,
            self.number_b,
            self.call_date,
        )


class VoiceMailCDR(StateSavingModel):
    cdr = models.OneToOneField(CallDetailRecord, related_name='voicemail')
    is_manual = models.BooleanField(
        u"Ручная обработка",
        help_text=u"Требуется ручная обработка через ОКП, так как не удалось определить менеджера данного клиента",
        default=False)
    comment = models.TextField(help_text=u"Комментарий о звонке, если необходимо", null=True, blank=True)
    last_commented_by = models.ForeignKey(User, null=True, blank=True)
    call_date = models.DateTimeField(u'Дата звонка')

    def get_record_path(self):
        if self.cdr.recording_file:
            name, ext = self.cdr.recording_file.rsplit('.', 1)
            return "http://138.201.206.11/records/{0}".format(name+u'-voicemail.'+ext)


class PhoneUser(models.Model):
    BOOLEAN_CHOICES = (  # Our telephony admin used char(1) instead of Boolean, I don't know why
        ("0", "No"),
        ("1", "Yes"),
    )
    QUEUE_CHOICES = (
        ("en", "English queue"),
        ("ru", "Russian queue"),
        ("null", "No queue"),
    )

    login = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=250)
    nat = models.CharField(max_length=1, default="0", choices=BOOLEAN_CHOICES,
                           help_text="Enables Asterisk NAT mode; try changing if connection doesn't work")
    permit = models.CharField("Allowed IPs", max_length=10000, default="", blank=True,
                              help_text="CIDR notation, e.g. 192.168.0.1/24&10.1.0.1/24")
    deny = models.CharField("Denied IPs", max_length=10000, default="", blank=True,
                            help_text="CIDR notation, e.g. 192.168.0.1/24&10.1.0.1/24")
    enabled = models.CharField(max_length=1, default="1", choices=BOOLEAN_CHOICES)
    office = models.CharField("Internal number", max_length=3, default="", blank=True)
    sync = models.CharField("Synced with asterisk", default="0", max_length=1, editable=False, choices=BOOLEAN_CHOICES)
    queue = models.CharField(max_length=50, default="null", choices=QUEUE_CHOICES)
    
    def save(self, *args, **kwargs):
        self.sync = 0  # We need to re-sync after each save
        return super(PhoneUser, self).save(*args, **kwargs)

    class Meta:
        db_table = "users"
