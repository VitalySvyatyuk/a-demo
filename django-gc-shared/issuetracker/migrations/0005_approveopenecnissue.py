# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuetracker', '0004_auto_20170118_1356'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApproveOpenECNIssue',
            fields=[
                ('genericissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='issuetracker.GenericIssue')),
            ],
            options={
                'verbose_name': 'Approve open ECN account',
                'verbose_name_plural': 'Approves open ECN account',
            },
            bases=('issuetracker.genericissue',),
        ),
    ]
