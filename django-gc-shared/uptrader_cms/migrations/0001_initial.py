# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyNews',
            fields=[
                ('node_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='node.Node')),
                ('event_date', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430', db_index=True)),
                ('slug', models.SlugField(default=b'', help_text='\u0411\u0443\u0434\u0435\u0442 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d \u043a\u0430\u043a \u0430\u0434\u0440\u0435\u0441 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b', verbose_name='\u0421\u043b\u0430\u0433')),
            ],
            options={
                'ordering': ['-event_date'],
                'verbose_name': 'Company news',
                'verbose_name_plural': 'Company news',
            },
            bases=('node.node', models.Model),
        ),
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0438\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440\u0430')),
                ('name_ru', models.CharField(default=b'', max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0438\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440\u0430')),
                ('name_en', models.CharField(default=b'', max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0438\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440\u0430')),
                ('description', models.TextField(null=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('fxstreet_id', models.CharField(default=b'', max_length=255, verbose_name='\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 FxStreet', blank=True)),
            ],
            options={
                'verbose_name': 'Economic indicator',
                'verbose_name_plural': 'Economic indicators',
            },
        ),
        migrations.CreateModel(
            name='IndicatorCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430')),
                ('name_ru', models.CharField(max_length=20, null=True, verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430')),
                ('name_en', models.CharField(max_length=20, null=True, verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430')),
                ('slug', models.SlugField(verbose_name='\u0421\u043b\u0430\u0433')),
                ('drupal_id', models.IntegerField(null=True, verbose_name='\u0421\u0442\u0430\u0440\u044b\u0439 drupal nid', blank=True)),
                ('code', models.CharField(max_length=3, null=True, blank=True)),
                ('rate_name', models.CharField(max_length=255, null=True, verbose_name='\u0421\u0442\u0430\u0432\u043a\u0430', blank=True)),
            ],
            options={
                'verbose_name': '\u0421\u0442\u0440\u0430\u043d\u0430 \u0434\u043b\u044f \u0438\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440\u0430',
                'verbose_name_plural': '\u0421\u0442\u0440\u0430\u043d\u044b \u0434\u043b\u044f \u0438\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='IndicatorEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u043e\u0431\u044b\u0442\u0438\u044f')),
                ('importance', models.IntegerField(verbose_name='\u0412\u0430\u0436\u043d\u043e\u0441\u0442\u044c', choices=[(1, 'Usual'), (2, 'Important'), (3, 'Very important')])),
                ('event_date', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u043e\u0431\u044b\u0442\u0438\u044f')),
                ('period', models.CharField(blank=True, max_length=255, null=True, verbose_name='\u041f\u0435\u0440\u0438\u043e\u0434', choices=[(b'week', 'a week before'), (b'quarter', 'quarter'), (b'month', 'month')])),
                ('period_date', models.DateField(null=True, verbose_name='Period', blank=True)),
                ('previous', models.CharField(max_length=255, null=True, verbose_name='\u041f\u0440\u0435\u0434\u044b\u0434\u0443\u0449\u0435\u0435', blank=True)),
                ('forecast', models.CharField(max_length=255, null=True, verbose_name='\u041f\u0440\u043e\u0433\u043d\u043e\u0437', blank=True)),
                ('facts', models.CharField(max_length=255, null=True, verbose_name='\u0424\u0430\u043a\u0442\u044b', blank=True)),
                ('indicator', models.ForeignKey(verbose_name='\u0418\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440', to='uptrader_cms.Indicator', help_text='\u041d\u0430\u0447\u043d\u0438\u0442\u0435 \u0432\u0432\u043e\u0434\u0438\u0442\u044c \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0438\u043d\u0434\u0438\u043a\u0430\u0442\u043e\u0440\u0430')),
            ],
            options={
                'ordering': ['-event_date'],
                'verbose_name': 'Economic event',
                'verbose_name_plural': 'Economic events',
            },
        ),
        migrations.AddField(
            model_name='indicator',
            name='country',
            field=models.ForeignKey(verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430', to='uptrader_cms.IndicatorCountry', null=True),
        ),
    ]
