# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TypicalComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442 \u0442\u0438\u043f\u043e\u0432\u043e\u0433\u043e \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u044f')),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-creation_ts',),
                'verbose_name': '\u0422\u0438\u043f\u043e\u0432\u043e\u0439 \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439',
                'verbose_name_plural': '\u0422\u0438\u043f\u043e\u0432\u044b\u0435 \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='TypicalCommentsCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438')),
            ],
            options={
                'verbose_name': '\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0442\u0438\u043f\u043e\u0432\u044b\u0445 \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432',
                'verbose_name_plural': '\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 \u0442\u0438\u043f\u043e\u0432\u044b\u0445 \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432',
            },
        ),
        migrations.AddField(
            model_name='typicalcomment',
            name='category',
            field=models.ForeignKey(verbose_name='\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0442\u0438\u043f\u043e\u0432\u043e\u0433\u043e \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u044f', to='typical_comments.TypicalCommentsCategory'),
        ),
    ]
