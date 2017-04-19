# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Menu',
                'verbose_name_plural': 'Menus',
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=200, verbose_name='URL', blank=True)),
                ('named_url', models.CharField(max_length=200, verbose_name='Named URL', blank=True)),
                ('regex_url', models.CharField(max_length=200, null=True, verbose_name='Regex URL', blank=True)),
                ('level', models.IntegerField(default=0, verbose_name='Level', editable=False)),
                ('rank', models.IntegerField(default=0, verbose_name='Rank', editable=False)),
                ('caption_ru', models.CharField(max_length=150, null=True, verbose_name='Caption Russian', blank=True)),
                ('caption_en', models.CharField(max_length=150, null=True, verbose_name='Caption English', blank=True)),
                ('caption_id', models.CharField(max_length=150, null=True, verbose_name='Caption Indonesian ', blank=True)),
                ('caption_zh_cn', models.CharField(max_length=150, null=True, verbose_name='Caption Chinese', blank=True)),
                ('visibility_condition', models.CharField(max_length=200, null=True, verbose_name='Visibility Condition', blank=True)),
                ('do_permission_check', models.BooleanField(default=False, verbose_name='Perform permission check')),
                ('icon', models.CharField(blank=True, max_length=150, null=True, verbose_name='Icon', choices=[(b'investments.png', b'investments'), (b'consult.png', b'consult'), (b'profile.png', b'profile'), (b'education.png', b'education'), (b'forum.png', b'forum'), (b'accounts.png', b'accounts'), (b'analytics.png', b'analytics'), (b'partnership.png', b'partnership'), (b'service.png', b'service'), (b'support.png', b'support')])),
                ('widget', models.CharField(max_length=150, null=True, verbose_name='Widget name', blank=True)),
                ('menu', models.ForeignKey(related_name='contained_items', blank=True, editable=False, to='treemenus.Menu', null=True, verbose_name='Menu')),
                ('parent', models.ForeignKey(verbose_name='Parent', blank=True, to='treemenus.MenuItem', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='menu',
            name='root_item',
            field=models.ForeignKey(related_name='is_root_item_of', blank=True, editable=False, to='treemenus.MenuItem', null=True, verbose_name='Root Item'),
        ),
    ]
