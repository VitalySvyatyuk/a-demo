# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('requisits', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0001_initial'),
        ('platforms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawrequestsgroup',
            name='account',
            field=models.ForeignKey(related_name='withdrawrequestgroups', verbose_name='Account', to='platforms.TradingAccount'),
        ),
        migrations.AddField(
            model_name='withdrawrequestsgroup',
            name='attention_list',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Needs attention'),
        ),
        migrations.AddField(
            model_name='additionaltransaction',
            name='account',
            field=models.ForeignKey(verbose_name='Account', to='platforms.TradingAccount'),
        ),
        migrations.AddField(
            model_name='additionaltransaction',
            name='by',
            field=models.ForeignKey(verbose_name='Author', blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='withdrawrequest',
            name='account',
            field=models.ForeignKey(related_name='withdrawrequest', verbose_name='Account', to='platforms.TradingAccount', help_text='Select one of your accounts', null=True),
        ),
        migrations.AddField(
            model_name='withdrawrequest',
            name='closed_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='Who closed the request', null=True, verbose_name='Closed by'),
        ),
        migrations.AddField(
            model_name='withdrawrequest',
            name='group',
            field=models.ForeignKey(related_name='requests', verbose_name='Withdraw Requests Group', to='payments.WithdrawRequestsGroup', null=True),
        ),
        migrations.AddField(
            model_name='withdrawrequest',
            name='requisit',
            field=models.ForeignKey(related_name='withdraw_requests', default=None, to='requisits.UserRequisit', blank=True, help_text='Select one of your payment details', null=True, verbose_name='Requisit'),
        ),
        migrations.AddField(
            model_name='depositrequest',
            name='account',
            field=models.ForeignKey(related_name='depositrequest', verbose_name='Account', to='platforms.TradingAccount', help_text='Select one of your accounts', null=True),
        ),
    ]
