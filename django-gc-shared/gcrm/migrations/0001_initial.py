# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields
from django.conf import settings
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024, verbose_name='\u0418\u043c\u044f')),
                ('info', django.contrib.postgres.fields.ArrayField(default=list, base_field=annoying.fields.JSONField(default=dict), verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f', size=None)),
                ('tags', django.contrib.postgres.fields.ArrayField(default=list, base_field=models.CharField(max_length=255), verbose_name='\u0422\u044d\u0433\u0438', size=None)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('manager', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='gcrm_contact', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('note_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gcrm.Note')),
                ('task_type', models.CharField(default='CALL', max_length=255, verbose_name='\u0422\u0438\u043f', choices=[('CALL', '\u0417\u0432\u043e\u043d\u043e\u043a'), ('LETTER', '\u041f\u0438\u0441\u044c\u043c\u043e'), ('MEETING', '\u0412\u0441\u0442\u0440\u0435\u0447\u0430'), ('FIRSTCALL', '\u041f\u0435\u0440\u0432\u0430\u044f \u0441\u0432\u044f\u0437\u044c')])),
                ('to_complete_at', models.DateTimeField(null=True, verbose_name='\u0414\u0435\u0434\u043b\u0430\u0439\u043d', blank=True)),
                ('completed_at', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f', blank=True)),
                ('assignee', models.ForeignKey(related_name='assigned_crm_tasks', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('gcrm.note',),
        ),
        migrations.AddField(
            model_name='note',
            name='author',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='note',
            name='contact',
            field=models.ForeignKey(related_name='notes', to='gcrm.Contact'),
        ),
        migrations.AddField(
            model_name='contact',
            name='last_non_completed_task',
            field=models.ForeignKey(related_name='+', to='gcrm.Task'),
        ),
    ]
