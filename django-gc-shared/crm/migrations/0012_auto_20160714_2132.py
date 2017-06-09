# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0011_auto_20160602_2252'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='managerreassignrequest',
            options={'get_latest_by': 'created_at', 'verbose_name': 'Manager reassign request', 'verbose_name_plural': 'Manager reassign requests'},
        ),
        migrations.AlterModelOptions(
            name='personalmanager',
            options={'verbose_name': 'Manager', 'verbose_name_plural': 'Managers', 'permissions': (('view_all_clients', 'Can see all clients in CRM'),)},
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='assign_to',
            field=models.ForeignKey(related_name='+', verbose_name='Assign to', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='author',
            field=models.ForeignKey(related_name='+', verbose_name='Request author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='comment',
            field=models.TextField(null=True, verbose_name='Comment', blank=True),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='completed_by',
            field=models.ForeignKey(related_name='+', verbose_name='Processed', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='previous',
            field=models.ForeignKey(related_name='+', verbose_name='Previous manager', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='reject_reason',
            field=models.TextField(null=True, verbose_name='Rejection reason', blank=True),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='status',
            field=models.CharField(default=b'new', max_length=255, verbose_name='Status', choices=[(b'new', 'New'), (b'accepted', 'Approved'), (b'rejected', 'Declined')]),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Changed at'),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='user',
            field=models.ForeignKey(related_name='+', verbose_name='Client', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='allowed_ips',
            field=models.CharField(help_text='Allowed IP-addresses. Separated by spaces. Specify "*" to allow any IP. Subnets can be specified: 192.168.1.0/25', max_length=1000, verbose_name='IP'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='amo_synced_at',
            field=models.DateTimeField(null=True, verbose_name='Last sync date', blank=True),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='amo_unsynced',
            field=models.BooleanField(default=True, verbose_name='Needs sync'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='can_be_auto_assigned',
            field=models.BooleanField(default=False, help_text='Can be assigned to clients automatically', verbose_name='Auto'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='can_request_new_customers',
            field=models.BooleanField(default=False, help_text='Can get client through the NEXT button', verbose_name='NEXT button'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='can_see_all_calls',
            field=models.BooleanField(default=False, verbose_name='Can view all calls'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='can_see_all_users',
            field=models.BooleanField(default=False, verbose_name='Has access to all clients'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='country_state_names',
            field=models.TextField(default='', help_text='Names of countries and regions, separated by spaces. In English.', verbose_name='Countries/Regions', blank=True),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='daily_limit',
            field=models.PositiveIntegerField(help_text='How much clients per day can be viewed. If not specified, a default value is used. WARGNING: if you increase this limit make sure that the manager has at least IP filter enabled', null=True, verbose_name='Day limit', blank=True),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='force_tasks_full_day',
            field=models.BooleanField(default=False, help_text='Force all the tasks to be set for the whole day', verbose_name='Set tasks for the whole day'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='ib_account',
            field=models.PositiveIntegerField(null=True, verbose_name='IB account number', blank=True),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='is_office_supermanager',
            field=models.BooleanField(default=False, help_text="Can manage office's clients", verbose_name='Office head'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='is_on_vacancies',
            field=models.BooleanField(default=False, verbose_name='On vacation'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='languages',
            field=models.CharField(default=b'ru', help_text='Comma-separated language codes, e.g. ru,en,zh-cn', max_length=10, verbose_name='Works with languages', blank=True),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='last_assigned',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date and time of the last client assignment'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='needs_call_check',
            field=models.BooleanField(default=True, help_text='Verify that the manager calls the clients they get', verbose_name='Verify calls'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='on_vacancies_until',
            field=models.DateField(null=True, verbose_name='On vacation until', blank=True),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='reassign_agent_code_to_office',
            field=models.BooleanField(default=False, help_text="If a user registers with the manager's agent code, change it to the office's agent code", verbose_name='Change agent code to the office'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='sip_name',
            field=models.CharField(max_length=1000, null=True, verbose_name='SIP login', blank=True),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='substitute',
            field=models.ForeignKey(verbose_name='Substitute for the vacation', blank=True, to='crm.PersonalManager', null=True),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='works_with_ib',
            field=models.BooleanField(default=False, verbose_name='Works with IB partners'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='works_with_office_clients',
            field=models.BooleanField(default=True, help_text='Works with the clients of the office', verbose_name='Works with the office'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='worktime_end',
            field=models.TimeField(default=datetime.time(16, 0), verbose_name='End of the shift'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='worktime_start',
            field=models.TimeField(default=datetime.time(9, 0), verbose_name='Start of the shift'),
        ),
    ]
