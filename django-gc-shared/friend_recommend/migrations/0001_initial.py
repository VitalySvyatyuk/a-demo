# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name="Friend's name")),
                ('email', models.EmailField(max_length=254, verbose_name="Friend's email")),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u044f \u0434\u0440\u0443\u0433\u0443',
                'verbose_name_plural': '\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438 \u0434\u0440\u0443\u0437\u044c\u044f\u043c',
            },
        ),
    ]
