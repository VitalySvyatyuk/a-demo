# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0002_webinar_language'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='webinar',
            options={'verbose_name': 'Webinar', 'verbose_name_plural': 'Webinars'},
        ),
        migrations.AlterModelOptions(
            name='webinarregistration',
            options={'verbose_name': 'Registration for the webinar', 'verbose_name_plural': 'Registration for the webinar'},
        ),
        migrations.AlterField(
            model_name='webinar',
            name='category',
            field=models.CharField(max_length=20, verbose_name='Webinar category', choices=[(b'basic', 'For beginners'), (b'topic', 'For advanced traders'), (b'analytic', 'Market reviews'), (b'for_partners', 'For partners')]),
        ),
        migrations.AlterField(
            model_name='webinar',
            name='description',
            field=models.TextField(verbose_name='Webinar description'),
        ),
        migrations.AlterField(
            model_name='webinar',
            name='favorite',
            field=models.BooleanField(default=False, help_text='If selected it is shown next to the webinars calendar', verbose_name='Favorite webinar'),
        ),
        migrations.AlterField(
            model_name='webinar',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Seminar'),
        ),
        migrations.AlterField(
            model_name='webinar',
            name='password',
            field=models.CharField(default=b'', max_length=100, verbose_name='Room password', blank=True),
        ),
        migrations.AlterField(
            model_name='webinar',
            name='price',
            field=models.PositiveIntegerField(default=0, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='webinar',
            name='slug',
            field=models.SlugField(help_text="Machine name (for URL's)", verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='webinar',
            name='speaker',
            field=models.CharField(default=b'', max_length=200, verbose_name='Webinar leader'),
        ),
        migrations.AlterField(
            model_name='webinarevent',
            name='link_to_room',
            field=models.URLField(null=True, verbose_name='Link to webinar room', blank=True),
        ),
        migrations.AlterField(
            model_name='webinarevent',
            name='slug',
            field=models.SlugField(help_text="Machine name (for URL's)", unique=True, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='webinarevent',
            name='starts_at',
            field=models.DateTimeField(verbose_name='Webinar date'),
        ),
        migrations.AlterField(
            model_name='webinarregistration',
            name='creation_ts',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Registration time'),
        ),
        migrations.AlterField(
            model_name='webinarregistration',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Paid'),
        ),
        migrations.AlterField(
            model_name='webinarregistration',
            name='paid_ts',
            field=models.DateTimeField(null=True, verbose_name='Paid time', blank=True),
        ),
        migrations.AlterField(
            model_name='webinarregistration',
            name='tutorial',
            field=models.ForeignKey(related_name='registrations', verbose_name='Webinar', to='education.WebinarEvent'),
        ),
        migrations.AlterField(
            model_name='webinarregistration',
            name='user',
            field=models.ForeignKey(related_name='webinarregistration', verbose_name='User', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
