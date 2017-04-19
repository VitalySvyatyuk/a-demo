# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gcrm', '0006_contact_system_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerReassignRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(default='', verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439')),
                ('result', models.NullBooleanField(default=None, verbose_name='\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442')),
                ('close_comment', models.TextField(default='', verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043a \u0440\u0435\u0448\u0435\u043d\u0438\u044e')),
                ('update_ts', models.DateTimeField(auto_now=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f')),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('author', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('closed_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('contact', models.ForeignKey(related_name='manager_reassign_requests', to='gcrm.Contact')),
                ('new_manager', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('previous_manager', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
