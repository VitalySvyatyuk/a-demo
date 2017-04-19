# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('_account_mt4_ids', models.TextField(help_text=b'One Mt4_Id on a line', blank=True)),
                ('query', models.TextField(help_text='\u0414\u043e\u043b\u0436\u0435\u043d \u0432\u0435\u0440\u043d\u0443\u0442\u044c \u0441\u043f\u0438\u0441\u043e\u043a \u043b\u043e\u0433\u0438\u043d\u043e\u0432 mt4', null=True, verbose_name='Eval-\u0437\u0430\u043f\u0440\u043e\u0441', blank=True)),
                ('slug', models.SlugField(editable=False, blank=True, null=True, verbose_name='Slug')),
                ('does_not_need_manager', models.BooleanField(default=False, help_text='\u041a\u043b\u0438\u0435\u043d\u0442\u0430\u043c, \u043e\u0442\u043a\u0440\u044b\u0432\u0448\u0438\u043c\u0441\u044f \u043f\u043e\u0434 \u044d\u0442\u0438\u043c\u0438 \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u043a\u0438\u043c\u0438 \u0441\u0447\u0451\u0442\u0430\u043c\u0438, \u043d\u0435 \u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440, \u0435\u0441\u043b\u0438 \u044d\u0442\u043e \u0440\u0435\u0433. \u043e\u0444\u0438\u0441\u044b)', verbose_name='\u041d\u0435 \u043d\u0443\u0436\u0435\u043d \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440')),
                ('allowed_users', models.ManyToManyField(help_text='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043c\u043e\u0436\u0435\u0442 \u0437\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0442\u044c \u043e\u0442\u0447\u0451\u0442\u044b \u0434\u043b\u044f \u044d\u0442\u043e\u0439 \u0433\u0440\u0443\u043f\u043f\u044b \u0441\u0447\u0435\u0442\u043e\u0432 (\u043f\u0440\u0438 \u043d\u0430\u043b\u0438\u0447\u0438\u0438 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0445 \u043f\u0440\u0430\u0432)', related_name='allowed_account_groups', to=settings.AUTH_USER_MODEL, blank=True)),
                ('force_exclude_for_users', models.ManyToManyField(help_text='\u042d\u0442\u0430 \u0433\u0440\u0443\u043f\u043f\u0430 \u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u043e \u0438\u0441\u043a\u043b\u044e\u0447\u0430\u0435\u0442\u0441\u044f \u043f\u0440\u0438 \u0437\u0430\u043f\u0440\u043e\u0441\u0435 \u043e\u0442\u0447\u0451\u0442\u043e\u0432 \u044d\u0442\u0438\u043c\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f\u043c\u0438', related_name='excluded_account_groups', to=settings.AUTH_USER_MODEL, blank=True)),
                ('subpartner_user', models.ForeignKey(verbose_name=b"Partner's manager", blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Account group',
                'verbose_name_plural': 'Account groups',
            },
        ),
        migrations.CreateModel(
            name='IBSettings',
            fields=[
                ('ib_account', models.PositiveIntegerField(serialize=False, verbose_name='\u2116 \u043f\u0430\u0440\u0442\u043d\u0451\u0440\u0441\u043a\u043e\u0433\u043e \u0441\u0447\u0451\u0442\u0430', primary_key=True)),
                ('reward_type', models.PositiveSmallIntegerField(verbose_name='\u0422\u0438\u043f \u0432\u043e\u0437\u043d\u0430\u0433\u0440\u0430\u0436\u0434\u0435\u043d\u0438\u044f', choices=[(0, '\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440'), (1, '\u0421\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u043e\u0444\u0438\u0441'), (2, 'CL'), (3, '\u0420\u0443\u0447\u043d\u043e\u0435 \u043d\u0430\u0447\u0438\u0441\u043b\u0435\u043d\u0438\u0435')])),
                ('cl_percent', models.PositiveSmallIntegerField(null=True, verbose_name='%CL', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='SavedReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('filename', models.CharField(max_length=100, null=True, blank=True)),
                ('celery_task_id', models.CharField(max_length=100, null=True, blank=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('for_user', models.ForeignKey(related_name='saved_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Saved report',
                'verbose_name_plural': 'Saved reports',
            },
        ),
        migrations.CreateModel(
            name='SavedReportData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', jsonfield.fields.JSONField(default={}, verbose_name='\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442')),
                ('params', jsonfield.fields.JSONField(default={}, help_text='\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0432\u0448\u0438\u0435\u0441\u044f \u0434\u043b\u044f \u0437\u0430\u043f\u0440\u043e\u0441\u0430 \u043e\u0442\u0447\u0451\u0442\u0430', verbose_name='\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b')),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
