# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0026_auto_20170209_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='education_level',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Level of education', choices=[(b'High school', 'High school'), (b'College', 'College'), (b'University', 'University'), (b'Other', 'Other')]),
        ),
    ]
