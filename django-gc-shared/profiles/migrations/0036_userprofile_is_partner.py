# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0035_userprofile_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_partner',
            field=models.BooleanField(default=False, help_text='User can browse partner section', verbose_name='Is partner'),
        ),
    ]
