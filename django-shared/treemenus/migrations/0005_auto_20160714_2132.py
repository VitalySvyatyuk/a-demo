# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0004_auto_20160329_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='caption_fa',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption Persian', blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='caption_fr',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption French', blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='caption_hy',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption Armenian', blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='caption_ka',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption Georgian', blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='caption_th',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption Thai', blank=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='caption_uk',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption Ukrainian', blank=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='icon',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Icon', choices=[(b'accounts.png', b'accounts'), (b'investments.png', b'investments'), (b'partnership.png', b'partnership'), (b'profile.png', b'profile'), (b'education.png', b'education'), (b'analytics.png', b'analytics'), (b'service.png', b'service'), (b'support.png', b'support'), (b'forum.png', b'forum'), (b'consult.png', b'consult')]),
        ),
    ]
