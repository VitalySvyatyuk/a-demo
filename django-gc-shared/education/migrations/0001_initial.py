# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Webinar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u0421\u0435\u043c\u0438\u043d\u0430\u0440')),
                ('slug', models.SlugField(help_text='\u041c\u0430\u0448\u0438\u043d\u043d\u043e\u0435 \u0438\u043c\u044f (\u0434\u043b\u044f \u0441\u0441\u044b\u043b\u043e\u043a)', verbose_name='\u0421\u043b\u0430\u0433')),
                ('price', models.PositiveIntegerField(default=0, verbose_name='\u0426\u0435\u043d\u0430')),
                ('category', models.CharField(max_length=20, verbose_name='\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0432\u0435\u0431\u0438\u043d\u0430\u0440\u0430', choices=[(b'basic', 'For beginners'), (b'topic', 'For advanced traders'), (b'analytic', 'Market reviews'), (b'for_partners', 'For partners')])),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0432\u0435\u0431\u0438\u043d\u0430\u0440\u0430')),
                ('favorite', models.BooleanField(default=False, help_text='\u0415\u0441\u043b\u0438 \u0432\u044b\u0431\u0440\u0430\u043d\u0430, \u0442\u043e \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0440\u044f\u0434\u043e\u043c \u0441 \u043a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u0435\u043c \u0432\u0435\u0431\u0438\u043d\u0430\u0440\u043e\u0432', verbose_name='\u0418\u0437\u0431\u0440\u0430\u043d\u043d\u044b\u0439 \u0432\u0435\u0431\u0438\u043d\u0430\u0440')),
                ('password', models.CharField(default=b'', max_length=100, verbose_name='\u041f\u0430\u0440\u043e\u043b\u044c \u043e\u0442 \u043a\u043e\u043c\u043d\u0430\u0442\u044b', blank=True)),
                ('speaker', models.CharField(default=b'', max_length=200, verbose_name='\u0412\u0435\u0434\u0443\u0449\u0438\u0439 \u0432\u0435\u0431\u0438\u043d\u0430\u0440\u0430')),
            ],
            options={
                'verbose_name': '\u0412\u0435\u0431\u0438\u043d\u0430\u0440',
                'verbose_name_plural': '\u0412\u0435\u0431\u0438\u043d\u0430\u0440\u044b',
            },
        ),
        migrations.CreateModel(
            name='WebinarEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('youtube_video_url', models.CharField(help_text='A full url to youtube video, e.g. http://www.youtube.com/watch?v=IqaAZi2ppCE', max_length=50, null=True, verbose_name='Youtube video url', blank=True)),
                ('slug', models.SlugField(help_text='\u041c\u0430\u0448\u0438\u043d\u043d\u043e\u0435 \u0438\u043c\u044f (\u0434\u043b\u044f \u0441\u0441\u044b\u043b\u043e\u043a)', unique=True, verbose_name='\u0421\u043b\u0430\u0433')),
                ('starts_at', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f')),
                ('link_to_room', models.URLField(null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u0432\u0435\u0431\u0438\u043d\u0430\u0440\u043d\u0443\u044e \u043a\u043e\u043c\u043d\u0430\u0442\u0443', blank=True)),
                ('webinar', models.ForeignKey(to='education.Webinar', null=True)),
            ],
            options={
                'ordering': ('-starts_at',),
            },
        ),
        migrations.CreateModel(
            name='WebinarRegistration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438')),
                ('is_paid', models.BooleanField(default=False, verbose_name='\u041e\u043f\u043b\u0430\u0447\u0435\u043d')),
                ('paid_ts', models.DateTimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043f\u043b\u0430\u0442\u044b', blank=True)),
                ('content_type', models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True)),
                ('tutorial', models.ForeignKey(related_name='registrations', verbose_name='\u0412\u0435\u0431\u0438\u043d\u0430\u0440', to='education.WebinarEvent')),
                ('user', models.ForeignKey(related_name='webinarregistration', verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f \u043d\u0430 \u0432\u0435\u0431\u0438\u043d\u0430\u0440',
                'verbose_name_plural': '\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438 \u043d\u0430 \u0432\u0435\u0431\u0438\u043d\u0430\u0440',
            },
        ),
    ]
