# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gcrm', '0010_note_task'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='completed_at',
        ),
        migrations.AddField(
            model_name='task',
            name='closed_at',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u043a\u0440\u044b\u0442\u0438\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='closed_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', choices=[('COMPLETED', '\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430'), ('POSTPONED', '\u041f\u0435\u0440\u0435\u043d\u0435\u0441\u0435\u043d\u0430')]),
        ),
    ]
