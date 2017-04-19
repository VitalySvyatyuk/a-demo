# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webinar',
            name='language',
            field=project.fields.LanguageField(default=b'en', max_length=10, verbose_name='Language', db_index=True, choices=[(b'ru', b'Russian'), (b'en', b'English')]),
        ),
    ]
