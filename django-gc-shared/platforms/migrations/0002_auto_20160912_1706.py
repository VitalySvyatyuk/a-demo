# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('platforms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradingaccount',
            name='registered_from_partner_domain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='referral.PartnerDomain', null=True),
        ),
        migrations.AddField(
            model_name='tradingaccount',
            name='user',
            field=models.ForeignKey(related_name='accounts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='tradingaccount',
            unique_together={('user', 'mt4_id')},
        ),
    ]
