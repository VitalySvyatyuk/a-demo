# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0013_personalmanager_has_document_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalmanager',
            name='can_set_agent_codes',
            field=models.BooleanField(default=False, help_text='Can set agent codes', verbose_name='Agent code'),
        ),
        migrations.AlterField(
            model_name='personalmanager',
            name='has_document_access',
            field=models.BooleanField(default=False, verbose_name='Can view uploaded documents'),
        ),
    ]
