# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import node.access
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(default=b'ru', max_length=10, verbose_name='Language', db_index=True, choices=[(b'ru', b'Russian'), (b'en', b'English')])),
                ('title', models.CharField(max_length=250, verbose_name='Title')),
                ('url_alias', models.CharField(max_length=160, verbose_name='URL alias', blank=True)),
                ('body', models.TextField(verbose_name='\u0422\u0435\u043b\u043e')),
                ('published', models.BooleanField(default=False, verbose_name='Published')),
                ('sitemapped', models.BooleanField(default=False, verbose_name='\u0412\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u0432 \u043a\u0430\u0440\u0442\u0443 \u0441\u0430\u0439\u0442\u0430')),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='Creation timestamp')),
                ('update_ts', models.DateTimeField(auto_now=True, verbose_name='Update timestamp')),
            ],
            options={
                'ordering': ('-creation_ts',),
                'verbose_name': 'Node',
                'verbose_name_plural': 'Nodes',
            },
            bases=(models.Model, node.access.PublicAccessMixin),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('node_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='node.Node')),
                ('header', models.CharField(max_length=255, verbose_name='Header')),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
            },
            bases=('node.node',),
        ),
        migrations.AddField(
            model_name='node',
            name='author',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
        migrations.AddField(
            model_name='node',
            name='content_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.CreateModel(
            name='LoggedInUserPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='node.Page')),
            ],
            options={
                'verbose_name': 'LoggedInUserPage',
                'verbose_name_plural': 'LoggedInUserPages',
            },
            bases=(node.access.LoggedInAccessMixin, 'node.page'),
        ),
    ]
