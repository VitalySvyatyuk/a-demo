# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('name_en', models.CharField(default=b'', max_length=50, verbose_name='Name Eng')),
            ],
            options={
                'ordering': ['country__name', 'name'],
                'verbose_name': 'City',
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('name_ru', models.CharField(max_length=50, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='Name')),
                ('slug', models.SlugField(help_text='Unique string for url generating', verbose_name='Slug')),
                ('code', models.CharField(null=True, max_length=5, blank=True, unique=True, verbose_name='Code', db_index=True)),
                ('weight', models.IntegerField(default=100, verbose_name='Weight')),
                ('phone_code', models.SmallIntegerField(default=None, null=True, verbose_name='Phone code', blank=True)),
                ('is_primary', models.BooleanField(default=False, verbose_name='This country is primary in this phone code group')),
                ('phone_code_mask', models.CharField(default=b'', help_text='"9" \u043e\u0431\u043e\u0437\u043d\u0430\u0447\u0430\u0435\u0442 \u043b\u044e\u0431\u0443\u044e \u0446\u0438\u0444\u0440\u0443, \u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440 (999) 999-9999', max_length=30, verbose_name='\u041c\u0430\u0441\u043a\u0430 \u043d\u043e\u043c\u0435\u0440\u0430', blank=True)),
                ('language', models.CharField(default=b'', choices=[(b'en', b'English'), (b'ru', b'Russian'), (b'zh-cn', b'Chinese'), (b'id', b'Indonesian'), (b'es', b'Spanish'), (b'fr', b'French'), (b'ar', b'Arabic'), (b'ms', b'Malaysian'), (b'pt', b'Portuguese'), (b'hi', b'Hindi')], max_length=10, blank=True, help_text='\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u044f\u0437\u044b\u043a \u0441\u0442\u0440\u0430\u043d\u044b', verbose_name='Language')),
            ],
            options={
                'ordering': ['weight', 'name'],
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(db_index=True, max_length=5, null=True, verbose_name='Code', blank=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('name_ru', models.CharField(max_length=50, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=50, null=True, verbose_name='Name')),
                ('country', models.ForeignKey(related_name='regions', verbose_name='Country', to='geobase.Country')),
            ],
            options={
                'ordering': ['country__name', 'name'],
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regions',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(verbose_name='Country', to='geobase.Country'),
        ),
        migrations.AddField(
            model_name='city',
            name='region',
            field=models.ForeignKey(verbose_name='Region', blank=True, to='geobase.Region', null=True),
        ),
    ]
