# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0010_personalmanager_needs_call_check'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personalmanager',
            name='manager_page_regexp',
        ),
    ]
