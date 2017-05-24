# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massmail', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaigntype',
            name='title_zh_cn',
        ),
        migrations.AddField(
            model_name='campaign',
            name='previous_campaigns',
            field=models.ManyToManyField(related_name='_campaign_previous_campaigns_+', null=True, to='massmail.Campaign', blank=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='previous_campaigns_type',
            field=models.CharField(default=b'', max_length=20, blank=True, choices=[(b'none', "Didn't get the message"), (b'all', 'Got the message'), (b'read', 'Read the message'), (b'unread', "Didn't read the message"), (b'clicked', 'Clicked on a link'), (b'unclicked', "Read, but didn't click on a link")]),
        ),
        migrations.AddField(
            model_name='campaigntype',
            name='title_ru',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
