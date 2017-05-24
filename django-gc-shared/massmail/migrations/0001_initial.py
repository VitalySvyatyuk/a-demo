# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shared.utils
import django.contrib.postgres.fields
import project.fields
import massmail.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Campaign name')),
                ('security_notification', models.BooleanField(default=False, help_text='Forcefully sent to unsubscribed clients', verbose_name='Force send')),
                ('languages', django.contrib.postgres.fields.ArrayField(default=massmail.models.campaign_languages_default, base_field=models.CharField(max_length=10), size=None)),
                ('is_active', models.BooleanField(default=False, help_text='Set campaign to Active to send it immediately', verbose_name='Active')),
                ('is_sent', models.BooleanField(default=False, verbose_name='Is sent')),
                ('send_once', models.BooleanField(default=False, verbose_name='Delayed campaign')),
                ('send_once_datetime', models.DateTimeField(null=True, verbose_name='Date of mailing', blank=True)),
                ('send_period', models.BooleanField(default=False, verbose_name='Send periodicaly')),
                ('cron', models.CharField(max_length=100, null=True, verbose_name='Schedule (in cron format)', blank=True)),
                ('personal', models.BooleanField(default=True, verbose_name='Personal greeting')),
                ('send_email', models.BooleanField(default=True, verbose_name='Send email')),
                ('send_in_private', models.BooleanField(default=True, verbose_name='Send to internal messages')),
                ('ga_slug', models.SlugField(blank=True, help_text='Name in Google Analytics', null=True, verbose_name='Name in GA')),
                ('email_subject', models.CharField(help_text=b'Available variables: first_name, last_name For example: Hi, {{first_name}}!', max_length=255, verbose_name='Message subject')),
                ('custom_email_from', models.CharField(default=b'', help_text='name@example.com Leave empty to use default address', max_length=100, verbose_name="Sender's email", blank=True)),
                ('custom_email_from_name', models.CharField(default=b'', help_text='Leave empty to use default name', max_length=255, verbose_name="Sender's name", blank=True)),
                ('po_sent_count', models.PositiveIntegerField(default=0, verbose_name='Messages sent')),
                ('_lock', models.BooleanField(default=False, help_text='Lock is active when campaign is being sent', verbose_name=b'Lock')),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('unsubscribed', models.PositiveIntegerField(default=0, verbose_name='Unsubscribed')),
                ('is_auto', models.BooleanField(default=False, verbose_name='Automatical')),
            ],
            options={
                'verbose_name': 'Campaign',
                'verbose_name_plural': 'Campaigns',
            },
        ),
        migrations.CreateModel(
            name='CampaignType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('title_en', models.CharField(max_length=100, null=True)),
                ('title_zh_cn', models.CharField(max_length=100, null=True)),
                ('unsubscribed', models.PositiveIntegerField(default=0, verbose_name='Unsubscribed')),
            ],
        ),
        migrations.CreateModel(
            name='MailingList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('query', models.TextField(help_text='Should return a list of Users', null=True, verbose_name='Eval-query', blank=True)),
                ('subscribers_count', models.PositiveIntegerField(default=0, help_text='Number of subscribers')),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('auto_campaign_name', models.CharField(max_length=1000, unique=True, null=True, editable=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Mailing list',
                'verbose_name_plural': 'Mailing lists',
            },
        ),
        migrations.CreateModel(
            name='MessageBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(default=b'main_content', help_text='Name of the block in the template, for example main_content', verbose_name='Key')),
                ('value_text', models.TextField(help_text=b'Available variables: first_name, last_name For example: Hi, {{first_name}}!', null=True, verbose_name='Plaintext message', blank=True)),
                ('value_html', models.TextField(help_text=b'Available variables: first_name, last_name For example: Hi, {{first_name}}!', null=True, verbose_name='HTML message', blank=True)),
                ('campaign', models.ForeignKey(related_name='blocks', to='massmail.Campaign')),
            ],
            options={
                'verbose_name': 'Content block',
                'verbose_name_plural': 'Content blocks',
            },
        ),
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Template name')),
                ('subject', models.CharField(help_text="The default subject if a campaign doesn't specify it", max_length=255, verbose_name='Subject')),
                ('text', models.TextField(help_text='Available variables: current_site, domain, unsubscribe_url, browser_url, subject', null=True, verbose_name='Plaintext message', blank=True)),
                ('html', models.TextField(help_text='Available variables: current_site, domain, unsubscribe_url, browser_url, subject', null=True, verbose_name='HTML message', blank=True)),
                ('language', project.fields.LanguageField(default=b'ru', max_length=10, verbose_name='Language', db_index=True, choices=[(b'en', b'English'), (b'zh-cn', b'Chinese')])),
            ],
            options={
                'verbose_name': 'Message template',
                'verbose_name_plural': 'Message templates',
            },
        ),
        migrations.CreateModel(
            name='OpenedCampaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('clicked', models.BooleanField(default=False)),
                ('opened', models.BooleanField(default=False)),
                ('campaign', models.ForeignKey(related_name='clicks', to='massmail.Campaign')),
            ],
        ),
        migrations.CreateModel(
            name='SentMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('campaign', models.ForeignKey(related_name='sent_messages', to='massmail.Campaign')),
            ],
        ),
        migrations.CreateModel(
            name='SentSms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SmsCampaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Campaign name')),
                ('is_active', models.BooleanField(default=False, help_text='Set campaign to Active to send it immediately', verbose_name='Active')),
                ('is_sent', models.BooleanField(default=False, verbose_name='Is sent')),
                ('is_scheduled', models.BooleanField(default=False, verbose_name='Scheduled')),
                ('languages', django.contrib.postgres.fields.ArrayField(default=massmail.models.campaign_languages_default, base_field=models.CharField(max_length=10), size=None)),
                ('schedule_date', models.DateField(null=True, verbose_name='Send at (date)', blank=True)),
                ('schedule_time', models.TimeField(null=True, verbose_name='Send at (time)', blank=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('unsubscribed', models.PositiveIntegerField(default=0, verbose_name='Unsubscribed')),
                ('text', models.TextField(help_text='8 SMS max', verbose_name='Message text')),
                ('confirmed_only', models.BooleanField(default=True, verbose_name='Send only to verified phone numbers')),
                ('_lock', models.BooleanField(default=False, help_text='Lock is active when campaign is being sent', verbose_name='Lock')),
                ('campaign_type', models.ManyToManyField(to='massmail.CampaignType', null=True, blank=True)),
                ('mailing_list', models.ManyToManyField(to='massmail.MailingList', verbose_name='Mailing lists', blank=True)),
                ('negative_mailing_list', models.ManyToManyField(related_name='excluded_from_sms_campaigns', to='massmail.MailingList', blank=True, help_text='These emails will be excluded from the campaign', null=True, verbose_name='Exclusion lists')),
            ],
        ),
        migrations.CreateModel(
            name='Subscribed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(max_length=255, null=True, blank=True)),
                ('last_name', models.CharField(max_length=255, null=True, blank=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('mailing_list', models.ForeignKey(related_name='subscribers', to='massmail.MailingList')),
            ],
        ),
        migrations.CreateModel(
            name='TemplateAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=shared.utils.UploadTo(b'attachments'))),
                ('content_id', models.SlugField(help_text=b'Used to insert links to the HTML message, for example Content id = "testimage", &ltimg src="cid:testimage" /&gt', verbose_name='Content id')),
                ('template', models.ForeignKey(related_name='attachments', to='massmail.MessageTemplate')),
            ],
        ),
        migrations.CreateModel(
            name='Unsubscribed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['email'],
            },
        ),
        migrations.AddField(
            model_name='sentsms',
            name='campaign',
            field=models.ForeignKey(related_name='sent_messages', to='massmail.SmsCampaign'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='campaign_type',
            field=models.ManyToManyField(to='massmail.CampaignType', null=True, verbose_name='Campaign type'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='mailing_list',
            field=models.ManyToManyField(to='massmail.MailingList', verbose_name='Mailing lists', blank=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='negative_mailing_list',
            field=models.ManyToManyField(related_name='excluded_from_campaigns', to='massmail.MailingList', blank=True, help_text='These emails will be excluded from the campaign', null=True, verbose_name='Exclusion lists'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='template',
            field=models.ForeignKey(verbose_name='Template', to='massmail.MessageTemplate'),
        ),
        migrations.AlterUniqueTogether(
            name='openedcampaign',
            unique_together=set([('campaign', 'email')]),
        ),
    ]
