# -*- coding: utf-8 -*-
import random
from hashlib import sha1

from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from geobase.phone_code_widget import CountryPhoneCodeField
from issuetracker.models import GenericIssue
from project.validators import DomainValidator


class ClickManager(models.Manager):
    def total(self, agent_code):
        clicks = self.filter(agent_code=agent_code). \
            aggregate(clicks=models.Sum('clicks'),
                      unique=models.Sum('unique_clicks'))
        if not clicks['clicks']:
            clicks['clicks'] = 0
        if not clicks['unique']:
            clicks['unique'] = 0
        return clicks


class Click(models.Model):
    agent_code = models.IntegerField(_('Agent code'))
    date = models.DateField(auto_now=True)
    clicks = models.IntegerField(_('Click count'), default=0)
    partner_domain_requests = models.IntegerField(u"Кол-во просмотров партнёрских материалов", default=0)
    unique_clicks = models.IntegerField(_('Unique click count'), default=0)

    objects = ClickManager()

    def __unicode__(self):
        return unicode(self.agent_code)

    class Meta:
        verbose_name = _('Agent code click')
        verbose_name_plural = _('Agent code clicks')
        unique_together = ('agent_code', 'date')


class PartnerCertificateIssue(GenericIssue):
    partner_account_number = models.PositiveIntegerField(u'Партнерский счет',
                                                         blank=True, null=True)
    tel_numb = models.CharField(u'Номер телефона', max_length=40,
                                blank=True, null=True)

    def generate_title(self):
        return u'Создать сертификат партнера для %s' % self.author.profile

    def generate_text(self):
        return self.generate_title()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.department = Group.objects.get(name="Partnership")
        return super(PartnerCertificateIssue, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Application for certificate creation')
        verbose_name_plural = _('Applications for certificate creation')


class PartnerDomain(models.Model):
    account = models.ForeignKey(User, related_name='partner_domains')
    domain = models.CharField(max_length=73, db_index=True, validators=[DomainValidator()])
    creation_ts = models.DateTimeField(_('Created'), auto_now_add=True)
    api_key = models.CharField(max_length=40, unique=True, db_index=True)
    ib_account = models.ForeignKey('platforms.TradingAccount')

    class Meta:
        verbose_name = _('Partner domain')

    def __unicode__(self):
        return ' '.join((self.domain, str(self.ib_account)))

    @staticmethod
    def generate_api_key(domain):
        random_salt = str(random.SystemRandom().randint(1, 9999999))
        return sha1(random_salt + domain.encode('utf-8')).hexdigest()

    def regenerate_api_key(self):
        self.api_key = self.generate_api_key(self.domain)
        return self.api_key


class PartnershipApplication(models.Model):
    name = models.CharField(_('Your name'), max_length=200)
    phone = CountryPhoneCodeField(_('Phone number'), max_length=40)
    email = models.EmailField(verbose_name=_('E-mail'), max_length=254)
    partnership_type = models.CharField(u"Тип партнёрства", max_length=20)

    def format_as_message(self):
        return u"Имя: {}\nТелефон: {}\nEmail: {}\nТип партнёрства: ".format(self.name, self.phone,
                                                                            self.email, self.partnership_type)

    class Meta:
        verbose_name = u"Заявка на партнёрство"
        verbose_name_plural = u"Заявки на партнёрство"