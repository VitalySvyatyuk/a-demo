# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UtmAnalytics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('utm_source', models.CharField(default=b'', max_length=256)),
                ('utm_medium', models.CharField(default=b'', max_length=256)),
                ('utm_campaign', models.CharField(default=b'', max_length=256)),
                ('utm_timestamp', models.DateTimeField(null=True)),
                ('referrer', models.CharField(default=b'', max_length=2048)),
                ('referrer_timestamp', models.DateTimeField(null=True)),
                ('agent_code_timestamp', models.DateTimeField(null=True)),
                ('registration_page', models.CharField(default=b'', max_length=4096)),
                ('user', models.OneToOneField(related_name='utm_analytics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
