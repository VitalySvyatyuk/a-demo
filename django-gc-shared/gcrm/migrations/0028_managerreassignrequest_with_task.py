# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0027_auto_20160331_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='managerreassignrequest',
            name='with_task',
            field=models.TextField(verbose_name='\u041d\u0430\u0437\u043d\u0430\u0447\u0438\u0442\u044c \u043d\u043e\u0432\u043e\u043c\u0443 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0443 \u0437\u0430\u0434\u0430\u0447\u0443 \u043f\u0440\u0438 \u043e\u0434\u043e\u0431\u0440\u0435\u043d\u0438\u0438', blank=True),
        ),
    ]
