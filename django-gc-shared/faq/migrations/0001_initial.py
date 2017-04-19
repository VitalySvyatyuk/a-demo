# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=160, verbose_name='name')),
                ('priority', models.PositiveSmallIntegerField(default=0, help_text='defines order in category list', verbose_name='priority')),
                ('slug', models.SlugField(help_text='short url name', verbose_name='slug')),
                ('lang', models.CharField(default=b'ru', max_length=10, verbose_name='language', choices=[(b'ru', b'Russian'), (b'en', b'English')])),
                ('faq_version', models.PositiveSmallIntegerField(default=0, verbose_name='\u0412\u0435\u0440\u0441\u0438\u044f FAQ', choices=[(0, b'Main FAQ'), (1, b'Instruments information'), (2, b'Glossary')])),
            ],
            options={
                'ordering': ('-priority',),
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=b'1024', verbose_name='question')),
                ('answer', models.TextField(verbose_name='answer')),
                ('priority', models.PositiveSmallIntegerField(default=0, help_text='defines order in category list', verbose_name='priority')),
                ('is_top10', models.BooleanField(default=False, verbose_name='in TOP 10')),
                ('lang', models.CharField(default=b'ru', max_length=10, verbose_name='language', choices=[(b'ru', b'Russian'), (b'en', b'English')])),
                ('published', models.BooleanField(default=True, verbose_name='\u041e\u043f\u0443\u0431\u043b\u0438\u043a\u043e\u0432\u0430\u043d\u043e')),
                ('categories', models.ManyToManyField(related_name='questions', to='faq.Category')),
            ],
            options={
                'ordering': ('-priority', '-question'),
                'verbose_name': 'Quesstion',
                'verbose_name_plural': 'Quesstions',
            },
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('slug', 'lang')]),
        ),
    ]
