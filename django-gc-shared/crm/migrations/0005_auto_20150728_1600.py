# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_auto_20150401_1621'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personalmanager',
            name='works_with_english',
        ),
        migrations.AddField(
            model_name='personalmanager',
            name='languages',
            field=models.CharField(default=b'ru', help_text='\u041a\u043e\u0434\u044b \u044f\u0437\u044b\u043a\u043e\u0432 \u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e, \u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440 ru,en,zh-cn', max_length=10, verbose_name='\u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u0441 \u044f\u0437\u044b\u043a\u0430\u043c\u0438', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='works_with_office_clients',
            field=models.BooleanField(default=True, help_text='\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u043a\u043b\u0438\u0435\u043d\u0442\u0430\u043c\u0438 \u043e\u0444\u0438\u0441\u0430', verbose_name='\u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442 c \u043e\u0444\u0438\u0441\u043e\u043c'),
            preserve_default=True,
        ),
    ]
