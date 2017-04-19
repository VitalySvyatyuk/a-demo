# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gcrm', '0009_auto_20151213_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('update_ts', models.DateTimeField(auto_now=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f')),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('author', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('contact', models.ForeignKey(related_name='notes', to='gcrm.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('update_ts', models.DateTimeField(auto_now=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f')),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('task_type', models.CharField(default='CALL', max_length=255, verbose_name='\u0422\u0438\u043f', choices=[('CALL', '\u0417\u0432\u043e\u043d\u043e\u043a'), ('LETTER', '\u041f\u0438\u0441\u044c\u043c\u043e'), ('MEETING', '\u0412\u0441\u0442\u0440\u0435\u0447\u0430'), ('FIRSTCALL', '\u041f\u0435\u0440\u0432\u0430\u044f \u0441\u0432\u044f\u0437\u044c')])),
                ('to_complete_at', models.DateTimeField(null=True, verbose_name='\u0414\u0435\u0434\u043b\u0430\u0439\u043d', blank=True)),
                ('completed_at', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f', blank=True)),
                ('assignee', models.ForeignKey(related_name='assigned_crm_tasks', to=settings.AUTH_USER_MODEL)),
                ('author', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('contact', models.ForeignKey(related_name='tasks', to='gcrm.Contact')),
            ],
        ),
    ]
