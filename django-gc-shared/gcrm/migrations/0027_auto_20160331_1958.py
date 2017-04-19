# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gcrm', '0026_task_close_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'permissions': (('user_reset_otp', 'Can reset OTP of observable contacts'),)},
        ),
        migrations.AlterField(
            model_name='contact',
            name='manager',
            field=models.ForeignKey(related_name='gcrm_contacts', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='managerreassignrequest',
            name='close_comment',
            field=models.TextField(null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043a \u0440\u0435\u0448\u0435\u043d\u0438\u044e'),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_type',
            field=models.CharField(default='CALL', max_length=255, verbose_name='\u0422\u0438\u043f', choices=[('CALL', '\u0417\u0432\u043e\u043d\u043e\u043a'), ('LETTER', '\u041f\u0438\u0441\u044c\u043c\u043e'), ('MEETING', '\u0412\u0441\u0442\u0440\u0435\u0447\u0430'), ('MONITORING', '\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433'), ('LECTURE', '\u041b\u0435\u043a\u0446\u0438\u044f'), ('PRACTICE', '\u041f\u0440\u0430\u043a\u0442\u0438\u043a\u0430')]),
        ),
    ]
