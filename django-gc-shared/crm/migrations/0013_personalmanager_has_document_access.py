# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0012_auto_20160714_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalmanager',
            name='has_document_access',
            field=models.BooleanField(default=False, verbose_name='\u041c\u043e\u0436\u0435\u0442 \u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b'),
        ),
    ]
