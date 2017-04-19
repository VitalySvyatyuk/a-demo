# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_auto_20170118_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='derivatives_exp',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='financial_exp',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='forex_exp',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='education_level',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Level of education', choices=[(b'High school', 'High school'), (b'College', 'College'), (b'University', 'University'), (b'Other', 'Other')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pass_seminar',
            field=models.BooleanField(default=False, verbose_name='I have attended a seminar or a course on Forex Trading'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='trade_years',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='For how many years did you trade Forex/CFDs?', choices=[(b'Less than 1 year', 'Less than 1 year'), (b'1 to 5 years', '1 to 5 years'), (b'Over 5 years', 'Over 5 years')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='traded_forex',
            field=models.BooleanField(default=False, verbose_name='Have you ever traded Forex or CFDs?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.CharField(help_text='Example: pr. Stachek, 8A', max_length=80, null=True, verbose_name='Residential address', blank=True),
        ),
    ]
