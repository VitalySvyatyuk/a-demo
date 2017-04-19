# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0003_menuitem_caption_pt'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='caption_ar',
            field=models.CharField(max_length=150, null=True, verbose_name='Caption Arabic', blank=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='icon',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Icon', choices=[(b'consult.png', b'consult'), (b'profile.png', b'profile'), (b'forum.png', b'forum'), (b'investments.png', b'investments'), (b'education.png', b'education'), (b'analytics.png', b'analytics'), (b'service.png', b'service'), (b'support.png', b'support'), (b'partnership.png', b'partnership'), (b'accounts.png', b'accounts')]),
        ),
    ]
