# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uptrader_cms', '0007_auto_20170119_1224'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indicatorcountry',
            options={'verbose_name': 'Country for indicator', 'verbose_name_plural': 'Countries for indicators'},
        ),
        migrations.AlterField(
            model_name='companynews',
            name='event_date',
            field=models.DateTimeField(verbose_name='Date', db_index=True),
        ),
        migrations.AlterField(
            model_name='companynews',
            name='slug',
            field=models.SlugField(default=b'', help_text='It will be used as the address of the page', verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='country',
            field=models.ForeignKey(verbose_name='Country', to='uptrader_cms.IndicatorCountry', null=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='description',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='fxstreet_id',
            field=models.CharField(default=b'', max_length=255, verbose_name='FxStreet ID', blank=True),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='name',
            field=models.CharField(default=b'', max_length=255, null=True, verbose_name='Indicator name'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='name_en',
            field=models.CharField(default=b'', max_length=255, null=True, verbose_name='Indicator name'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='name_ru',
            field=models.CharField(default=b'', max_length=255, null=True, verbose_name='Indicator name'),
        ),
        migrations.AlterField(
            model_name='indicatorcountry',
            name='drupal_id',
            field=models.IntegerField(null=True, verbose_name='Old drupal id', blank=True),
        ),
        migrations.AlterField(
            model_name='indicatorcountry',
            name='name',
            field=models.CharField(max_length=20, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='indicatorcountry',
            name='name_en',
            field=models.CharField(max_length=20, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='indicatorcountry',
            name='name_ru',
            field=models.CharField(max_length=20, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='indicatorcountry',
            name='rate_name',
            field=models.CharField(max_length=255, null=True, verbose_name='Discount rate', blank=True),
        ),
        migrations.AlterField(
            model_name='indicatorcountry',
            name='slug',
            field=models.SlugField(verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='indicatorevent',
            name='event_date',
            field=models.DateTimeField(verbose_name='Event time'),
        ),
        migrations.AlterField(
            model_name='indicatorevent',
            name='facts',
            field=models.CharField(max_length=255, null=True, verbose_name='Facts', blank=True),
        ),
        migrations.AlterField(
            model_name='indicatorevent',
            name='forecast',
            field=models.CharField(max_length=255, null=True, verbose_name='Prediction', blank=True),
        ),
        migrations.AlterField(
            model_name='indicatorevent',
            name='importance',
            field=models.IntegerField(verbose_name='Importance', choices=[(1, 'Usual'), (2, 'Important'), (3, 'Very important')]),
        ),
        migrations.AlterField(
            model_name='indicatorevent',
            name='indicator',
            field=models.ForeignKey(verbose_name='Indicator', to='uptrader_cms.Indicator', help_text='Start typing the name of the indicator'),
        ),
        migrations.AlterField(
            model_name='indicatorevent',
            name='period',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Period', choices=[(b'week', 'a week before'), (b'quarter', 'quarter'), (b'month', 'month')]),
        ),
        migrations.AlterField(
            model_name='indicatorevent',
            name='previous',
            field=models.CharField(max_length=255, null=True, verbose_name='Previous', blank=True),
        ),
        migrations.AlterField(
            model_name='indicatorevent',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Event name'),
        ),
    ]
