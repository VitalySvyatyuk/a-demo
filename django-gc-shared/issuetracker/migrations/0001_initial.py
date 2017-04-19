# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators
import shared.utils
import project.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericIssue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'open', max_length=50, verbose_name='status', choices=[(b'open', 'New issue'), (b'rejected', 'Issue status rejected'), (b'done', 'Answer received'), (b'processing', 'In process'), (b'closed', 'Issue closed')])),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='creation timestamp')),
                ('update_ts', models.DateTimeField(auto_now=True, verbose_name='update timestamp')),
                ('deadline', models.DateField(null=True, verbose_name='deadline', blank=True)),
                ('title', models.CharField(max_length=160, verbose_name='title')),
                ('text', models.TextField(verbose_name='text')),
                ('internal_description', models.TextField(help_text=b'\xd0\x9d\xd0\xb5 \xd0\xb2\xd0\xb8\xd0\xb4\xd0\xbd\xd0\xbe \xd0\xba\xd0\xbb\xd0\xb8\xd0\xb5\xd0\xbd\xd1\x82\xd1\x83', verbose_name='Internal description', blank=True)),
                ('internal_comment', models.TextField(default=b'', help_text='Not shown to client', verbose_name='Internal comment', blank=True)),
            ],
            options={
                'ordering': ['-creation_ts'],
                'verbose_name': 'issue',
                'verbose_name_plural': 'issues',
            },
        ),
        migrations.CreateModel(
            name='IssueAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(help_text='\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0440\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u0438\u044f: doc, docx, bmp, gif, jpg, jpeg, png, pdf, xls, xlsx. \u041c\u0430\u043a\u0441. \u043e\u0431\u044a\u0435\u043c \u0444\u0430\u0439\u043b\u0430: 5.00 \u041c\u0411', upload_to=shared.utils.UploadTo(b'issue_attachments'), verbose_name='Attachment', validators=[project.validators.allow_file_extensions((b'doc', b'docx', b'bmp', b'gif', b'jpg', b'jpeg', b'png', b'pdf', b'xls', b'xlsx')), project.validators.allow_file_size(5242880)])),
            ],
            options={
                'verbose_name': 'issue attachment',
                'verbose_name_plural': 'issue attachment',
            },
        ),
        migrations.CreateModel(
            name='IssueChangeHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='creation timestamp')),
                ('text', models.TextField(verbose_name='change description')),
            ],
        ),
        migrations.CreateModel(
            name='IssueComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='comment text')),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='creation timestamp')),
            ],
            options={
                'get_latest_by': 'creation_ts',
                'verbose_name': 'issue comment',
                'verbose_name_plural': 'issue comments',
            },
        ),
        migrations.CreateModel(
            name='CheckDocumentIssue',
            fields=[
                ('genericissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='issuetracker.GenericIssue')),
            ],
            options={
                'verbose_name': 'check document issue',
                'verbose_name_plural': 'check document issues',
            },
            bases=('issuetracker.genericissue',),
        ),
        migrations.CreateModel(
            name='CheckOnChargebackIssue',
            fields=[
                ('genericissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='issuetracker.GenericIssue')),
                ('user_requested_check', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u043d\u0430 chargeback',
                'verbose_name_plural': '\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439 \u043d\u0430 chargeback',
            },
            bases=('issuetracker.genericissue',),
        ),
        migrations.CreateModel(
            name='InternalTransferIssue',
            fields=[
                ('genericissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='issuetracker.GenericIssue')),
                ('recipient', models.IntegerField(help_text="Recipient's account number.", blank=True, verbose_name='recipient', validators=[django.core.validators.MinValueValidator(0)])),
                ('amount', models.DecimalField(help_text='Amount of money to transfer', verbose_name='amount', max_digits=10, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('currency', models.CharField(default=b'USD', choices=[(b'RUR', b'RUR'), (b'USD', b'USD'), (b'EUR', b'EUR')], max_length=6, blank=True, null=True, verbose_name='Currency')),
            ],
            options={
                'verbose_name': 'internal transfer issue',
                'verbose_name_plural': 'internal transfer issues',
            },
            bases=('issuetracker.genericissue',),
        ),
        migrations.CreateModel(
            name='RestoreFromArchiveIssue',
            fields=[
                ('genericissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='issuetracker.GenericIssue')),
            ],
            options={
                'verbose_name': 'restore account from archive issue',
                'verbose_name_plural': 'restore account from archive issue',
            },
            bases=('issuetracker.genericissue',),
        ),
        migrations.CreateModel(
            name='UserIssue',
            fields=[
                ('genericissue_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='issuetracker.GenericIssue')),
            ],
            options={
                'verbose_name': 'user issue',
                'verbose_name_plural': 'user issues',
            },
            bases=('issuetracker.genericissue',),
        ),
        migrations.AddField(
            model_name='issuecomment',
            name='issue',
            field=models.ForeignKey(related_name='comments', verbose_name='issue', to='issuetracker.GenericIssue'),
        ),
        migrations.AddField(
            model_name='issuecomment',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='issuechangehistory',
            name='issue',
            field=models.ForeignKey(to='issuetracker.GenericIssue'),
        ),
        migrations.AddField(
            model_name='issuechangehistory',
            name='user',
            field=models.ForeignKey(verbose_name='change initiator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='issueattachment',
            name='issue',
            field=models.ForeignKey(related_name='attachments', verbose_name='issue', to='issuetracker.GenericIssue'),
        ),
        migrations.AddField(
            model_name='issueattachment',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='genericissue',
            name='assignee',
            field=models.ForeignKey(related_name='assigned_issues', verbose_name='assignee', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='genericissue',
            name='author',
            field=models.ForeignKey(related_name='created_issues', verbose_name='author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='genericissue',
            name='department',
            field=models.ForeignKey(verbose_name='department', blank=True, to='auth.Group', null=True),
        ),
    ]
