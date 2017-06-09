# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geobase', '0001_initial'),
        ('profiles', '0010_userprofile_email_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='av_transactions',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Average size of a transactions (USD)', choices=[(b'Less than $10 000', 'Less than $10 000'), (b'$10 000 - $50 000', b'$10 000 - $50 000'), (b'$50 001 - $100 000', b'$50 001 - $100 000'), (b'$100 001 - $200 000', b'$100 001 - $200 000'), (b'Over $250 000', 'Over $250 000')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='employment_status',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Employemnt status', choices=[(b'Employed', 'Employed'), (b'Unemployed', 'Unemployed'), (b'Self employed', 'Self employed'), (b'Retired', 'Retired'), (b'Student', 'Student')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='financial_commitments',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Monthly financial commitments', choices=[(b'Less than 20%', 'Less than 20%'), (b'21% - 40%', b'21% - 40%'), (b'41% - 60%', b'41% - 60%'), (b'61% - 80%', b'61% - 80%'), (b'Over 80%', 'Over 80%')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='fr_transactions',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Frequency of transactions', choices=[(b'Daily', 'Daily'), (b'Weekly', 'Weekly'), (b'Monthly', 'Monthly'), (b'Yearly', 'Yearly')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='nature_of_biz',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Nature of biz', choices=[(b'Accountancy', 'Accountancy'), (b'Admin/secretarial', 'Admin/ secretarial'), (b'Agricultural', 'Agricultural'), (b'Art', 'Art'), (b'Financial/Banking', 'Financial/Banking'), (b'Catering/Hospitality', 'Catering/Hospitality'), (b'Creative/Media', 'Creative/Media'), (b'Educational', 'Educational'), (b'Emergency', 'Emergency'), (b'Engineering', 'Engineering'), (b'Health/Medicine', 'Health/Medicine'), (b'IT', 'IT'), (b'Legal', 'Legal'), (b'Leisure/ Entertainment/ Tourism', 'Leisure/ Entertainment/ Tourism'), (b'Manufacturing', 'Manufacturing'), (b'Marketing/ Advertising/ PR', 'Marketing/ Advertising/ PR'), (b'Property', 'Property'), (b'Sales', 'Sales'), (b'Social', 'Social'), (b'Telecom', 'Telecom'), (b'Transport/ Logistics', 'Transport/ Logistics'), (b'Other', 'Other')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='source_of_funds',
            field=models.CharField(blank=True, max_length=90, null=True, verbose_name='Source of funds', choices=[(b'Income from professional activity', 'Income from professional activity'), (b'Savings', 'Savings'), (b'Partner/ parent/ family', 'Partner/ parent/ family'), (b'Investments/ Dividends', 'Investments/ Dividends'), (b'Borrowing', 'Borrowing'), (b'Pension', 'Pension'), (b'Other', 'Other')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='tax_residence',
            field=models.ForeignKey(related_name='taxes', blank=True, to='geobase.Country', help_text='Example: Russia', null=True, verbose_name='Tax residence'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='us_citizen',
            field=models.BooleanField(default=False, verbose_name='US citizen'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='annual_income',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Annual income (USD)', choices=[(b'100k', 'over 100 000'), (b'50k', b'50 000 - 100 000'), (b'10k', b'10 000 - 50 000'), (b'0', 'below 10 000')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='net_capital',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Net capital (USD)', choices=[(b'100k', 'over 100 000'), (b'50k', b'50 000 - 100 000'), (b'10k', b'10 000 - 50 000'), (b'0', 'below 10 000')]),
        ),
    ]
