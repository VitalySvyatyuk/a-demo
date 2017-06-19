# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import payments.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRequisit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(default=b'', help_text='Give these payment details a name, for example "Forex wallet". It will help you find them in forms more easily', max_length=255, verbose_name='alias', blank=True)),
                ('purse', models.CharField(db_index=True, max_length=255, verbose_name='purse', blank=True)),
                ('payment_system', payments.fields.PaymentSystemField(max_length=50, verbose_name='payment system')),
                ('is_valid', models.NullBooleanField(default=False, verbose_name='is the data valid?')),
                ('is_deleted', models.BooleanField(default=False, help_text='Users do not see deleted requisits', verbose_name='Is deleted')),
                ('comment', models.TextField(help_text='If you reject a requisit, leave a comment here', null=True, verbose_name='manager comment', blank=True)),
                ('params', jsonfield.fields.JSONField(null=True, verbose_name='details', blank=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('previous', models.ForeignKey(verbose_name='previous version of requisit', blank=True, to='requisits.UserRequisit', null=True)),
                ('user', models.ForeignKey(related_name='requisits', verbose_name='user', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['payment_system', '-creation_ts'],
                'verbose_name': 'user requisit',
                'verbose_name_plural': 'user requisits',
            },
        ),
        migrations.AlterUniqueTogether(
            name='userrequisit',
            unique_together=set([('purse', 'payment_system', 'user')]),
        ),
    ]
